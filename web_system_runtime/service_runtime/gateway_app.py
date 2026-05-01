from __future__ import annotations

import os
import shutil
import tempfile
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pandas as pd
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from shared.result_table import build_run_summary, finalize_result_table
from shared.sample_validation import validate_model_output, validate_samples_csv


MODEL_SERVICE_URLS = {
    "DualSyn": os.environ.get("DUALSYN_SERVICE_URL", "").strip(),
    "MFSynDCP": os.environ.get("MFSYNDCP_SERVICE_URL", "").strip(),
    "MVCASyn": os.environ.get("MVCASYN_SERVICE_URL", "").strip(),
    "MTLSynergy": os.environ.get("MTLSYNERGY_SERVICE_URL", "").strip(),
}
DOWNSTREAM_TIMEOUT_SECONDS = int(os.environ.get("GATEWAY_DOWNSTREAM_TIMEOUT", "3600"))
RUN_LOG_TAIL_SIZE = 30
RUNTIME_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = Path(os.environ.get("SYNERGY_WORKSPACE_ROOT", RUNTIME_ROOT.parent)).resolve()
TRAINED_MODEL_ROOT = Path(os.environ.get("SYNERGY_TRAINED_MODEL_ROOT", RUNTIME_ROOT / "trained_model_versions")).resolve()

RUNS: Dict[str, Dict[str, object]] = {}
RUNS_LOCK = threading.Lock()


class GatewayPredictRequest(BaseModel):
    samples_csv: str
    selected_models: List[str]
    output_root: str
    model_version_id: str = "__default__"


app = FastAPI(title="Synergy inference gateway")


class RunCancelled(Exception):
    def __init__(self, message: str, accumulated_log: str = "") -> None:
        super().__init__(message)
        self.accumulated_log = accumulated_log


def _now_iso() -> str:
    return datetime.now().isoformat()


def _service_health(service_url: str) -> Dict[str, object]:
    if not service_url:
        return {"ready": False, "detail": "missing service url"}
    try:
        response = requests.get(f"{service_url.rstrip('/')}/health", timeout=10)
        response.raise_for_status()
        payload = response.json()
        return {"ready": bool(payload.get("ready")), "payload": payload}
    except Exception as exc:  # pragma: no cover - defensive network boundary
        return {"ready": False, "detail": str(exc)}


def _load_model_result(model_output_csv: Path, payload: Dict[str, object]) -> pd.DataFrame:
    if payload.get("output_persisted") and model_output_csv.exists():
        return pd.read_csv(model_output_csv)

    rows = payload.get("rows") or []
    if not rows:
        raise HTTPException(status_code=500, detail=f"Model service returned no rows and no readable CSV: {model_output_csv}")
    return pd.DataFrame(rows)


def _append_full_log(run: Dict[str, object], message: str) -> None:
    if not message:
        return
    full_log = str(run.get("full_log", ""))
    run["full_log"] = f"{full_log}\n{message}".strip()
    log_lines = list(run.get("log_lines", []))
    log_lines.extend(str(message).splitlines())
    run["log_lines"] = log_lines[-200:]


def _create_run_record(request: GatewayPredictRequest) -> Dict[str, object]:
    run_id = uuid.uuid4().hex[:12]
    return {
        "run_id": run_id,
        "state": "running",
        "phase_key": "validating",
        "phase_label": "输入检查",
        "progress_percent": 3,
        "current_model": "",
        "model_statuses": {model_name: "waiting" for model_name in request.selected_models},
        "log_lines": ["已收到推理请求，正在检查输入。"],
        "full_log": "已收到推理请求，正在检查输入。",
        "error": "",
        "started_at": _now_iso(),
        "finished_at": None,
        "output_path": None,
        "summary": None,
        "service_outputs": {},
        "resource_reports": {},
        "selected_models": list(request.selected_models),
        "model_version_id": request.model_version_id,
        "samples_csv": request.samples_csv,
        "output_root": request.output_root,
        "cancel_requested": False,
    }


def _serialize_run(run: Dict[str, object]) -> Dict[str, object]:
    payload = {
        "run_id": run["run_id"],
        "state": run["state"],
        "phase_key": run["phase_key"],
        "phase_label": run["phase_label"],
        "progress_percent": run["progress_percent"],
        "current_model": run["current_model"],
        "model_statuses": run["model_statuses"],
        "latest_log_lines": run.get("log_lines", [])[-RUN_LOG_TAIL_SIZE:],
        "error": run.get("error", ""),
        "started_at": run.get("started_at"),
        "finished_at": run.get("finished_at"),
        "output_path": run.get("output_path"),
        "summary": run.get("summary"),
        "service_outputs": run.get("service_outputs", {}),
        "resource_reports": run.get("resource_reports", {}),
        "selected_models": run.get("selected_models", []),
        "model_version_id": run.get("model_version_id", "__default__"),
        "samples_csv": run.get("samples_csv", ""),
        "result_rows": (run.get("summary") or {}).get("row_count", 0),
        "cancel_requested": bool(run.get("cancel_requested", False)),
    }
    if run["state"] in {"completed", "failed"}:
        payload["full_log"] = run.get("full_log", "")
    if run["state"] in {"canceled", "canceling"}:
        payload["full_log"] = run.get("full_log", "")
    return payload


def _update_run(
    run_id: str,
    *,
    state: str | None = None,
    phase_key: str | None = None,
    phase_label: str | None = None,
    progress_percent: int | None = None,
    current_model: str | None = None,
    model_name: str | None = None,
    model_state: str | None = None,
    log_message: str | None = None,
    error: str | None = None,
    output_path: str | None = None,
    summary: Dict[str, object] | None = None,
    service_outputs: Dict[str, object] | None = None,
    resource_reports: Dict[str, object] | None = None,
    cancel_requested: bool | None = None,
    finished: bool = False,
) -> None:
    with RUNS_LOCK:
        run = RUNS.get(run_id)
        if not run:
            return
        if state is not None:
            run["state"] = state
        if phase_key is not None:
            run["phase_key"] = phase_key
        if phase_label is not None:
            run["phase_label"] = phase_label
        if progress_percent is not None:
            run["progress_percent"] = progress_percent
        if current_model is not None:
            run["current_model"] = current_model
        if model_name and model_state:
            model_statuses = dict(run.get("model_statuses", {}))
            model_statuses[model_name] = model_state
            run["model_statuses"] = model_statuses
        if log_message:
            _append_full_log(run, log_message)
        if error is not None:
            run["error"] = error
        if output_path is not None:
            run["output_path"] = output_path
        if summary is not None:
            run["summary"] = summary
        if service_outputs is not None:
            run["service_outputs"] = service_outputs
        if resource_reports is not None:
            run["resource_reports"] = resource_reports
        if cancel_requested is not None:
            run["cancel_requested"] = cancel_requested
        if finished:
            run["finished_at"] = _now_iso()


def _is_cancel_requested(run_id: str | None) -> bool:
    if not run_id:
        return False
    with RUNS_LOCK:
        run = RUNS.get(run_id)
        return bool(run and run.get("cancel_requested"))


def _cancel_downstream_services(run_id: str) -> list[str]:
    messages: list[str] = []
    for model_name, service_url in MODEL_SERVICE_URLS.items():
        if not service_url:
            continue
        try:
            response = requests.post(
                f"{service_url.rstrip('/')}/cancel-current",
                json={"run_id": run_id},
                timeout=10,
            )
            payload = response.json() if response.content else {}
            detail = payload.get("detail", "")
            if payload.get("canceled"):
                messages.append(f"{model_name} 停止成功。{detail}".strip())
            elif detail:
                messages.append(f"{model_name} 未停止：{detail}")
        except Exception as exc:  # pragma: no cover - defensive network boundary
            messages.append(f"{model_name} 停止请求失败：{exc}")
    return messages


def _raise_if_cancel_requested(run_id: str | None, logs: List[str]) -> None:
    if _is_cancel_requested(run_id):
        raise RunCancelled("用户已中断推理任务。", "\n\n".join(logs).strip())


def _apply_canceled_model_statuses(run_id: str) -> None:
    with RUNS_LOCK:
        run = RUNS.get(run_id)
        if not run:
            return
        current_model = str(run.get("current_model", "") or "")
        model_statuses = dict(run.get("model_statuses", {}))
        for model_name, model_state in list(model_statuses.items()):
            if model_name == current_model and model_state == "running":
                model_statuses[model_name] = "canceled"
            elif model_state == "waiting":
                model_statuses[model_name] = "skipped"
        run["model_statuses"] = model_statuses


def _validated_samples(request: GatewayPredictRequest) -> tuple[Path, Path, pd.DataFrame]:
    if not request.selected_models:
        raise HTTPException(status_code=400, detail="No models were selected.")

    unknown_models = [model_name for model_name in request.selected_models if model_name not in MODEL_SERVICE_URLS]
    if unknown_models:
        raise HTTPException(status_code=400, detail=f"Unknown models: {unknown_models}")

    samples_csv = Path(request.samples_csv).resolve()
    output_root = Path(request.output_root).resolve()
    if not samples_csv.exists():
        raise HTTPException(status_code=400, detail=f"Samples CSV does not exist: {samples_csv}")

    validation = validate_samples_csv(
        samples_csv,
        workspace_root=WORKSPACE_ROOT,
        selected_models=request.selected_models,
    )
    if not validation.valid:
        raise HTTPException(status_code=400, detail=validation.detail)

    samples_df = pd.read_csv(samples_csv)
    output_root.mkdir(parents=True, exist_ok=True)
    return samples_csv, output_root, samples_df


def _execute_prediction(
    request: GatewayPredictRequest,
    *,
    run_id: str | None = None,
) -> Dict[str, object]:
    if run_id:
        _update_run(run_id, phase_key="validating", phase_label="输入检查", progress_percent=5)

    samples_csv, output_root, samples_df = _validated_samples(request)
    if run_id:
        _update_run(
            run_id,
            phase_key="dispatching",
            phase_label="连接服务/准备任务",
            progress_percent=12,
            log_message="输入校验完成，准备连接模型服务。",
        )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_root = Path(tempfile.mkdtemp(prefix=f"gateway_run_{timestamp}_"))
    base_result_df = samples_df[["sample_id", "drug_a_name", "drug_b_name", "cell_line"]].copy()
    logs: List[str] = []
    service_outputs: Dict[str, object] = {}
    resource_reports: Dict[str, object] = {}
    try:
        model_count = max(1, len(request.selected_models))
        for index, model_name in enumerate(request.selected_models):
            _raise_if_cancel_requested(run_id, logs)
            service_url = MODEL_SERVICE_URLS.get(model_name)
            if not service_url:
                raise HTTPException(status_code=500, detail=f"Service URL is not configured for {model_name}")

            progress_start = 15 + int((index / model_count) * 70)
            progress_end = 15 + int(((index + 1) / model_count) * 70)
            if run_id:
                _update_run(
                    run_id,
                    phase_key="model_running",
                    phase_label=f"{model_name} 运行",
                    progress_percent=progress_start,
                    current_model=model_name,
                    model_name=model_name,
                    model_state="running",
                    log_message=f"{model_name} 开始运行。",
                )

            model_output_csv = temp_root / f"{model_name.lower()}_predictions.csv"
            service_payload = {
                "samples_csv": str(samples_csv),
                "output_csv": str(model_output_csv),
                "run_id": run_id,
            }
            if request.model_version_id and request.model_version_id != "__default__":
                artifact_root = TRAINED_MODEL_ROOT / request.model_version_id / "artifacts" / model_name
                if not artifact_root.exists():
                    raise HTTPException(status_code=400, detail=f"{model_name} 训练版本权重目录不存在: {artifact_root}")
                service_payload["artifact_root"] = str(artifact_root)
            response = requests.post(
                f"{service_url.rstrip('/')}/predict",
                json=service_payload,
                timeout=DOWNSTREAM_TIMEOUT_SECONDS,
            )
            if response.status_code >= 400:
                if _is_cancel_requested(run_id):
                    raise RunCancelled("用户已中断推理任务。", "\n\n".join(logs).strip())
                raise HTTPException(status_code=500, detail=f"{model_name} service failed: {response.text}")

            payload = response.json()
            if payload.get("persist_error"):
                logs.append(f"[{model_name}] output persist warning: {payload['persist_error']}")
            logs.append(f"[{model_name}] {payload.get('log', '')}".strip())
            resource_report = payload.get("resource_report", {})
            service_outputs[model_name] = {
                "output_csv": payload.get("output_csv"),
                "output_persisted": payload.get("output_persisted", False),
                "resource_report": resource_report,
            }
            resource_reports[model_name] = resource_report
            model_df = _load_model_result(model_output_csv, payload)
            output_valid, output_error = validate_model_output(model_df, samples_df, model_name=model_name)
            if not output_valid:
                raise HTTPException(status_code=500, detail=output_error)
            base_result_df = base_result_df.merge(model_df, on="sample_id", how="left")
            _raise_if_cancel_requested(run_id, logs)

            if run_id:
                _update_run(
                    run_id,
                    phase_key="model_running",
                    phase_label=f"{model_name} 运行",
                    progress_percent=progress_end,
                    current_model=model_name,
                    model_name=model_name,
                    model_state="completed",
                    log_message=f"{model_name} 已完成。",
                    service_outputs=service_outputs,
                    resource_reports=resource_reports,
                )

        _raise_if_cancel_requested(run_id, logs)
        if run_id:
            _update_run(
                run_id,
                phase_key="merging",
                phase_label="结果合并与写出",
                progress_percent=92,
                current_model="",
                log_message="模型运行完成，正在合并结果并写出文件。",
            )

        result_df = finalize_result_table(base_result_df, request.selected_models, run_mode="docker-real-inference")
        output_path = output_root / f"docker_predictions_{samples_csv.stem}_{timestamp}.csv"
        result_df.to_csv(output_path, index=False, encoding="utf-8-sig")
        summary = build_run_summary(result_df, request.selected_models, output_path)
        full_log = "\n\n".join(logs)

        if run_id:
            _update_run(
                run_id,
                state="completed",
                phase_key="completed",
                phase_label="完成",
                progress_percent=100,
                current_model="",
                log_message="推理完成，结果文件已生成。",
                output_path=str(output_path),
                summary=summary,
                service_outputs=service_outputs,
                resource_reports=resource_reports,
                finished=True,
            )
            if full_log:
                _update_run(run_id, log_message=full_log)

        return {
            "output_path": str(output_path),
            "summary": summary,
            "run_log": full_log,
            "service_outputs": service_outputs,
            "resource_reports": resource_reports,
        }
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def _run_prediction_background(run_id: str, request: GatewayPredictRequest) -> None:
    try:
        _execute_prediction(request, run_id=run_id)
    except RunCancelled as exc:
        _apply_canceled_model_statuses(run_id)
        if exc.accumulated_log:
            _update_run(run_id, log_message=exc.accumulated_log)
        _update_run(
            run_id,
            state="canceled",
            phase_key="canceled",
            phase_label="已中断",
            progress_percent=100,
            current_model="",
            error=str(exc),
            log_message="推理已被用户中断。",
            finished=True,
        )
    except Exception as exc:  # pragma: no cover - background execution boundary
        _update_run(
            run_id,
            state="failed",
            phase_key="failed",
            phase_label="已失败",
            current_model="",
            error=str(exc),
            log_message=f"任务失败：{exc}",
            finished=True,
        )


@app.get("/health")
def health() -> Dict[str, object]:
    services = {model_name: _service_health(service_url) for model_name, service_url in MODEL_SERVICE_URLS.items()}
    return {
        "services": services,
        "all_ready": all(entry["ready"] for entry in services.values()),
    }


@app.post("/predict")
def predict(request: GatewayPredictRequest) -> Dict[str, object]:
    return _execute_prediction(request)


@app.post("/runs")
def create_run(request: GatewayPredictRequest) -> Dict[str, object]:
    _validated_samples(request)
    run = _create_run_record(request)
    with RUNS_LOCK:
        RUNS[run["run_id"]] = run

    worker = threading.Thread(
        target=_run_prediction_background,
        args=(run["run_id"], request),
        daemon=True,
    )
    worker.start()
    return _serialize_run(run)


@app.get("/runs/{run_id}")
def get_run(run_id: str) -> Dict[str, object]:
    with RUNS_LOCK:
        run = RUNS.get(run_id)
        if not run:
            raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")
        return _serialize_run(run)


@app.post("/runs/{run_id}/cancel")
def cancel_run(run_id: str) -> Dict[str, object]:
    with RUNS_LOCK:
        run = RUNS.get(run_id)
        if not run:
            raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")
        if run["state"] in {"completed", "failed", "canceled"}:
            return _serialize_run(run)
        run["cancel_requested"] = True
        run["state"] = "canceling"
        run["phase_key"] = "canceling"
        run["phase_label"] = "正在中断"
        _append_full_log(run, "已收到中断请求，正在停止当前模型。")

    cancel_messages = _cancel_downstream_services(run_id)
    _apply_canceled_model_statuses(run_id)
    if cancel_messages:
        _update_run(run_id, log_message="\n".join(cancel_messages))
    with RUNS_LOCK:
        run = RUNS.get(run_id)
        if not run:
            raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")
        return _serialize_run(run)
