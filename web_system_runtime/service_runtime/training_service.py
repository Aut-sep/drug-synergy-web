from __future__ import annotations

import json
import os
import selectors
import signal
import shutil
import subprocess
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


APP_ROOT = Path(os.environ.get("SYNERGY_RUNTIME_ROOT", Path(__file__).resolve().parents[1])).resolve()
REPO_ROOT = Path(os.environ.get("SYNERGY_REPO_ROOT", APP_ROOT.parent)).resolve()
TRAINING_WORK_ROOT = Path(os.environ.get("SYNERGY_TRAINING_WORK_ROOT", Path.home() / ".cache" / "bishe_training_runs")).resolve()
TRAINED_MODEL_ROOT = Path(os.environ.get("SYNERGY_TRAINED_MODEL_ROOT", APP_ROOT / "trained_model_versions")).resolve()
CONDA_EXE = os.environ.get("SYNERGY_CONDA_EXE", str(Path.home() / "miniconda3" / "bin" / "conda"))
RUNTIME_MOUNT_ROOT = os.environ.get("SYNERGY_RUNTIME_MOUNT_ROOT", "/workspace/web_system_runtime").rstrip("/")

MODEL_ENVS = {
    "DualSyn": os.environ.get("DUALSYN_TRAIN_ENV", "ddi"),
    "MFSynDCP": os.environ.get("MFSYNDCP_TRAIN_ENV", "mf"),
    "MVCASyn": os.environ.get("MVCASYN_TRAIN_ENV", "mvc"),
    "MTLSynergy": os.environ.get("MTLSYNERGY_TRAIN_ENV", "mtl"),
}
ALL_MODELS = ["DualSyn", "MFSynDCP", "MVCASyn", "MTLSynergy"]
RUN_LOG_TAIL_SIZE = 80


class TrainingRunRequest(BaseModel):
    bundle_path: str
    selected_models: List[str] = ALL_MODELS
    profile: str = "quick"
    device: str = "auto"
    epochs: Optional[int] = None
    label_source: str = "threshold"
    label_threshold: float = 10.0
    fold_strategy: str = "pair_group"
    seed: int = 20260413
    version_note: str = ""


app = FastAPI(title="WSL model training service")
RUNS: Dict[str, Dict[str, object]] = {}
RUNS_LOCK = threading.Lock()


class TrainingCancelled(Exception):
    pass


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _translate_container_path(raw_path: str) -> Path:
    path_text = raw_path.strip()
    if path_text == RUNTIME_MOUNT_ROOT:
        return APP_ROOT.resolve()
    if path_text.startswith(f"{RUNTIME_MOUNT_ROOT}/"):
        rel = path_text.removeprefix(f"{RUNTIME_MOUNT_ROOT}/").lstrip("/")
        return (APP_ROOT / rel).resolve()
    return Path(path_text).expanduser().resolve()


def _run_json_command(command: list[str], timeout: int = 30) -> dict[str, object]:
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
    except Exception as exc:
        return {"ok": False, "detail": str(exc)}
    return {
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def _conda_python(env_name: str, code: str, timeout: int = 30) -> dict[str, object]:
    return _run_json_command([CONDA_EXE, "run", "-n", env_name, "python", "-c", code], timeout=timeout)


def _cuda_status() -> dict[str, object]:
    smi = _run_json_command(["nvidia-smi"], timeout=10)
    torch_probe = _run_json_command(
        [
            CONDA_EXE,
            "run",
            "-n",
            MODEL_ENVS["DualSyn"],
            "python",
            "-c",
            "import torch; print(torch.cuda.is_available())",
        ],
        timeout=30,
    )
    return {
        "nvidia_smi": smi["ok"],
        "torch_cuda_probe": torch_probe,
    }


def _env_status(env_name: str) -> dict[str, object]:
    probe = _conda_python(
        env_name,
        "import pandas, sklearn, torch; "
        "import importlib.util; "
        "print({'torch': torch.__version__, 'cuda': torch.cuda.is_available(), "
        "'pyg': importlib.util.find_spec('torch_geometric') is not None, "
        "'rdkit': importlib.util.find_spec('rdkit') is not None})",
    )
    return {"env_name": env_name, **probe}


def _append_log(run: dict[str, object], text: str) -> None:
    if not text:
        return
    full_log = str(run.get("full_log", ""))
    run["full_log"] = f"{full_log}\n{text}".strip()
    lines = list(run.get("log_lines", []))
    lines.extend(text.splitlines())
    run["log_lines"] = lines[-300:]


def _update_run(run_id: str, **updates: object) -> None:
    with RUNS_LOCK:
        run = RUNS.get(run_id)
        if not run:
            return
        log_message = str(updates.pop("log_message", "") or "")
        for key, value in updates.items():
            run[key] = value
        if log_message:
            _append_log(run, log_message)


def _serialize_run(run: dict[str, object]) -> dict[str, object]:
    return {
        "run_id": run["run_id"],
        "version_id": run.get("version_id", ""),
        "state": run["state"],
        "phase_label": run.get("phase_label", ""),
        "progress_percent": run.get("progress_percent", 0),
        "current_model": run.get("current_model", ""),
        "model_statuses": run.get("model_statuses", {}),
        "latest_log_lines": run.get("log_lines", [])[-RUN_LOG_TAIL_SIZE:],
        "full_log": run.get("full_log", "") if run["state"] in {"completed", "failed", "canceled"} else "",
        "error": run.get("error", ""),
        "started_at": run.get("started_at"),
        "finished_at": run.get("finished_at"),
        "version_dir": run.get("version_dir", ""),
        "selected_models": run.get("selected_models", []),
        "cancel_requested": bool(run.get("cancel_requested", False)),
    }


def _create_run_record(request: TrainingRunRequest, bundle_path: Path) -> dict[str, object]:
    run_id = uuid.uuid4().hex[:12]
    version_id = f"user_train_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{run_id[:6]}"
    return {
        "run_id": run_id,
        "version_id": version_id,
        "state": "running",
        "phase_label": "等待启动",
        "progress_percent": 1,
        "current_model": "",
        "model_statuses": {model_name: "waiting" for model_name in request.selected_models},
        "log_lines": [],
        "full_log": "",
        "error": "",
        "started_at": _now_iso(),
        "finished_at": None,
        "bundle_path": str(bundle_path),
        "selected_models": list(request.selected_models),
        "profile": request.profile,
        "device": request.device,
        "version_dir": str(TRAINED_MODEL_ROOT / version_id),
        "cancel_requested": False,
    }


def _check_cancel(run_id: str) -> None:
    with RUNS_LOCK:
        run = RUNS.get(run_id)
        if run and run.get("cancel_requested"):
            raise TrainingCancelled("训练任务已被用户取消。")


def _ignore_training_noise(_dir: str, names: list[str]) -> set[str]:
    ignored = {"__pycache__", ".pytest_cache"}
    ignored.update(name for name in names if name.endswith(".pyc"))
    return ignored


def _copy_project(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=_ignore_training_noise)


def _copy_data(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def _reset_training_outputs(source_root: Path) -> None:
    output_paths = [
        source_root / "DualSyn" / "DualSyn" / "save_model",
        source_root / "DualSyn" / "DualSyn" / "result",
        source_root / "MFSynDCP" / "MFSynDCP" / "result",
        source_root / "MVCASyn" / "results" / "training_run",
        source_root / "MTLSynergy" / "save",
        source_root / "MTLSynergy" / "save" / "AutoEncoder",
        source_root / "MTLSynergy" / "save" / "MTLSA",
        source_root / "MTLSynergy" / "save" / "MTLSynergy",
        source_root / "MTLSynergy" / "result",
    ]
    for output_path in output_paths:
        if output_path.exists():
            shutil.rmtree(output_path)
        output_path.mkdir(parents=True, exist_ok=True)


def _resolve_mtlsynergy_batch_size(sample_count: int) -> int:
    return max(1, min(32, sample_count // 4))


def _command_for_model(
    model_name: str,
    request: TrainingRunRequest,
    project_root: Path,
    version_id: str,
    sample_count: Optional[int] = None,
) -> list[list[str]]:
    env_name = MODEL_ENVS[model_name]
    device = request.device
    quick_epochs = int(request.epochs or (2 if request.profile == "quick" else 0))

    def conda_cmd(script: str, extra: list[str]) -> list[str]:
        return [CONDA_EXE, "run", "-n", env_name, "python", script, *extra]

    if model_name == "DualSyn":
        extra = ["--result-name", "DualSyn_transductive", "--device", device]
        if quick_epochs:
            extra.extend(["--epochs", str(quick_epochs)])
        return [conda_cmd("train_transductive.py", extra)]

    if model_name == "MFSynDCP":
        train_extra = ["--result-prefix", "MFSynDCP", "--result-tag", version_id, "--device", device]
        if quick_epochs:
            train_extra.extend(["--epochs", str(quick_epochs)])
        return [
            conda_cmd("creat_data.py", []),
            conda_cmd("training.py", train_extra),
        ]

    if model_name == "MVCASyn":
        extra = ["--result-name", "training_run", "--device", device]
        if quick_epochs:
            extra.extend(["--n_epochs", str(quick_epochs)])
        return [conda_cmd("cv_train.py", extra)]

    if model_name == "MTLSynergy":
        ae_extra = ["--device", device]
        train_extra = ["--device", device]
        if sample_count is not None:
            train_extra.extend(["--batch-size", str(_resolve_mtlsynergy_batch_size(sample_count))])
        if quick_epochs:
            ae_extra.extend(["--drug-epochs", str(quick_epochs), "--cell-epochs", str(quick_epochs), "--patience", str(quick_epochs)])
            train_extra.extend(["--epochs", str(quick_epochs), "--patience", str(quick_epochs)])
        return [
            conda_cmd("AEtrain.py", ae_extra),
            conda_cmd("MTLSynergytrain.py", train_extra),
        ]

    raise ValueError(f"Unsupported model: {model_name}")


def _stream_command(command: list[str], cwd: Path, run_id: str, model_name: str, log_path: Path) -> None:
    _update_run(run_id, log_message=f"[{model_name}] COMMAND: {' '.join(command)}")
    start_time = time.time()
    with log_path.open("a", encoding="utf-8", errors="replace") as handle:
        process = subprocess.Popen(
            command,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            start_new_session=True,
        )
        assert process.stdout is not None
        selector = selectors.DefaultSelector()
        selector.register(process.stdout, selectors.EVENT_READ)
        try:
            while process.poll() is None:
                _check_cancel(run_id)
                for key, _ in selector.select(timeout=1.0):
                    line = key.fileobj.readline()
                    if not line:
                        continue
                    handle.write(line)
                    handle.flush()
                    _update_run(run_id, log_message=f"[{model_name}] {line.rstrip()}")
            for line in process.stdout:
                handle.write(line)
                handle.flush()
                _update_run(run_id, log_message=f"[{model_name}] {line.rstrip()}")
        except TrainingCancelled:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait(timeout=10)
            raise
        except Exception:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            raise
        finally:
            selector.close()
        returncode = process.wait()
    elapsed = time.time() - start_time
    if returncode != 0:
        raise RuntimeError(f"{model_name} command failed with return code {returncode}: {' '.join(command)}")
    _update_run(run_id, log_message=f"[{model_name}] finished in {elapsed:.1f}s")


def _prepare_training_workspace(run_id: str, request: TrainingRunRequest, bundle_path: Path) -> tuple[Path, Path]:
    run_root = TRAINING_WORK_ROOT / run_id
    source_root = run_root / "source"
    exports_root = run_root / "exports"
    run_root.mkdir(parents=True, exist_ok=True)

    build_script = REPO_ROOT / "benchmark_factory" / "build_benchmark_dataset.py"
    dataset_name = "training_dataset"
    command = [
        "python3",
        str(build_script),
        "--input-root",
        str(bundle_path),
        "--output-root",
        str(exports_root),
        "--dataset-name",
        dataset_name,
        "--label-source",
        request.label_source,
        "--label-threshold",
        str(request.label_threshold),
        "--fold-strategy",
        request.fold_strategy,
        "--seed",
        str(request.seed),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    _update_run(run_id, log_message=completed.stdout.strip())
    if completed.returncode != 0:
        raise RuntimeError(f"训练数据导出失败: {completed.stderr or completed.stdout}")

    _copy_project(REPO_ROOT / "DualSyn" / "DualSyn", source_root / "DualSyn" / "DualSyn")
    _copy_project(REPO_ROOT / "MFSynDCP" / "MFSynDCP", source_root / "MFSynDCP" / "MFSynDCP")
    _copy_project(REPO_ROOT / "MVCASyn", source_root / "MVCASyn")
    _copy_project(REPO_ROOT / "MTLSynergy", source_root / "MTLSynergy")

    dataset_root = exports_root / dataset_name
    _copy_data(dataset_root / "dualsyn" / "data", source_root / "DualSyn" / "DualSyn" / "data")
    _copy_data(dataset_root / "mfsyndcp" / "data", source_root / "MFSynDCP" / "MFSynDCP" / "data")
    _copy_data(dataset_root / "mvcasyn" / "data", source_root / "MVCASyn" / "data")
    _copy_data(dataset_root / "mtlsynergy" / "data", source_root / "MTLSynergy" / "data")
    _reset_training_outputs(source_root)

    return source_root, exports_root


def _copy_artifacts(source_root: Path, version_dir: Path) -> None:
    artifacts_root = version_dir / "artifacts"
    artifacts_root.mkdir(parents=True, exist_ok=True)

    mappings = [
        (source_root / "DualSyn" / "DualSyn" / "save_model", artifacts_root / "DualSyn" / "save_model"),
        (source_root / "DualSyn" / "DualSyn" / "result", artifacts_root / "DualSyn" / "result"),
        (source_root / "MFSynDCP" / "MFSynDCP" / "result", artifacts_root / "MFSynDCP" / "result"),
        (source_root / "MVCASyn" / "results" / "training_run", artifacts_root / "MVCASyn" / "results"),
        (source_root / "MTLSynergy" / "save", artifacts_root / "MTLSynergy" / "save"),
        (source_root / "MTLSynergy" / "result", artifacts_root / "MTLSynergy" / "result"),
    ]
    for src, dst in mappings:
        if src.exists():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)


def _write_manifest(version_dir: Path, run: dict[str, object], request: TrainingRunRequest, exports_root: Path) -> None:
    manifest = {
        "version_id": run["version_id"],
        "created_at": _now_iso(),
        "source_bundle": run["bundle_path"],
        "selected_models": run["selected_models"],
        "profile": request.profile,
        "device": request.device,
        "epochs": request.epochs,
        "version_note": request.version_note,
        "exports_root": str(exports_root),
        "artifact_layout": {
            "DualSyn": "artifacts/DualSyn/save_model",
            "MFSynDCP": "artifacts/MFSynDCP/result",
            "MVCASyn": "artifacts/MVCASyn/results/model",
            "MTLSynergy": "artifacts/MTLSynergy/save/MTLSynergy",
        },
    }
    (version_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def _run_training_background(run_id: str, request: TrainingRunRequest) -> None:
    with RUNS_LOCK:
        run = RUNS[run_id]
    version_dir = Path(str(run["version_dir"]))
    log_dir = version_dir / "logs"
    version_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    try:
        bundle_path = Path(str(run["bundle_path"]))
        sample_count = len(pd.read_csv(bundle_path / "samples.csv"))
        _update_run(run_id, phase_label="导出训练数据", progress_percent=5, log_message=f"训练包: {bundle_path}")
        source_root, exports_root = _prepare_training_workspace(run_id, request, bundle_path)

        model_count = max(1, len(request.selected_models))
        for index, model_name in enumerate(request.selected_models):
            _check_cancel(run_id)
            progress_start = 10 + int(index / model_count * 75)
            progress_end = 10 + int((index + 1) / model_count * 75)
            _update_run(
                run_id,
                phase_label=f"{model_name} 训练中",
                progress_percent=progress_start,
                current_model=model_name,
                model_statuses={**dict(run.get("model_statuses", {})), model_name: "running"},
            )

            if model_name == "DualSyn":
                project_root = source_root / "DualSyn" / "DualSyn"
            elif model_name == "MFSynDCP":
                project_root = source_root / "MFSynDCP" / "MFSynDCP"
            else:
                project_root = source_root / model_name

            for step_command in _command_for_model(
                model_name,
                request,
                project_root,
                str(run["version_id"]),
                sample_count=sample_count,
            ):
                _stream_command(step_command, project_root, run_id, model_name, log_dir / f"{model_name}.log")

            statuses = dict(run.get("model_statuses", {}))
            statuses[model_name] = "completed"
            _update_run(run_id, progress_percent=progress_end, model_statuses=statuses)

        _update_run(run_id, phase_label="注册模型版本", progress_percent=92, current_model="")
        _copy_artifacts(source_root, version_dir)
        _write_manifest(version_dir, run, request, exports_root)

        _update_run(
            run_id,
            state="completed",
            phase_label="完成",
            progress_percent=100,
            finished_at=_now_iso(),
            log_message=f"训练版本已生成: {version_dir}",
        )
    except TrainingCancelled as exc:
        _update_run(
            run_id,
            state="canceled",
            phase_label="已取消",
            progress_percent=100,
            current_model="",
            error=str(exc),
            finished_at=_now_iso(),
            log_message=str(exc),
        )
    except Exception as exc:
        _update_run(
            run_id,
            state="failed",
            phase_label="失败",
            progress_percent=100,
            current_model="",
            error=str(exc),
            finished_at=_now_iso(),
            log_message=f"训练失败: {exc}",
        )


def _list_versions() -> list[dict[str, object]]:
    TRAINED_MODEL_ROOT.mkdir(parents=True, exist_ok=True)
    versions: list[dict[str, object]] = []
    for manifest_path in sorted(TRAINED_MODEL_ROOT.glob("*/manifest.json"), key=lambda path: path.stat().st_mtime, reverse=True):
        try:
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        payload["version_dir"] = str(manifest_path.parent)
        versions.append(payload)
    return versions


@app.get("/health")
def health() -> dict[str, object]:
    envs = {model_name: _env_status(env_name) for model_name, env_name in MODEL_ENVS.items()}
    return {
        "ready": all(entry.get("ok") for entry in envs.values()),
        "app_root": str(APP_ROOT),
        "repo_root": str(REPO_ROOT),
        "training_work_root": str(TRAINING_WORK_ROOT),
        "trained_model_root": str(TRAINED_MODEL_ROOT),
        "conda_exe": CONDA_EXE,
        "conda_exists": Path(CONDA_EXE).exists(),
        "cuda": _cuda_status(),
        "envs": envs,
    }


@app.get("/model-versions")
def model_versions() -> dict[str, object]:
    return {"versions": _list_versions()}


@app.post("/training-runs")
def create_training_run(request: TrainingRunRequest) -> dict[str, object]:
    unknown = [model_name for model_name in request.selected_models if model_name not in ALL_MODELS]
    if unknown:
        raise HTTPException(status_code=400, detail=f"未知模型: {unknown}")
    if not request.selected_models:
        raise HTTPException(status_code=400, detail="至少选择一个模型。")

    bundle_path = _translate_container_path(request.bundle_path)
    required_files = [
        "samples.csv",
        "drugs.csv",
        "cells_dualsyn.csv",
        "cells_mtl.csv",
        "cells_mvc_exp.csv",
        "cells_mvc_cn.csv",
    ]
    missing = [name for name in required_files if not (bundle_path / name).exists()]
    if missing:
        raise HTTPException(status_code=400, detail=f"训练包缺少文件: {missing}")

    run = _create_run_record(request, bundle_path)
    with RUNS_LOCK:
        RUNS[str(run["run_id"])] = run

    worker = threading.Thread(target=_run_training_background, args=(str(run["run_id"]), request), daemon=True)
    worker.start()
    return _serialize_run(run)


@app.get("/training-runs/{run_id}")
def get_training_run(run_id: str) -> dict[str, object]:
    with RUNS_LOCK:
        run = RUNS.get(run_id)
        if not run:
            raise HTTPException(status_code=404, detail=f"训练任务不存在: {run_id}")
        return _serialize_run(run)


@app.post("/training-runs/{run_id}/cancel")
def cancel_training_run(run_id: str) -> dict[str, object]:
    with RUNS_LOCK:
        run = RUNS.get(run_id)
        if not run:
            raise HTTPException(status_code=404, detail=f"训练任务不存在: {run_id}")
        if run["state"] in {"completed", "failed", "canceled"}:
            return _serialize_run(run)
        run["cancel_requested"] = True
        run["phase_label"] = "取消中"
        _append_log(run, "已收到取消请求，正在停止当前训练子进程。")
        return _serialize_run(run)
