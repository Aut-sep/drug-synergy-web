from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from shared.resource_monitor import ProcessResourceMonitor


MODEL_NAME = os.environ.get("MODEL_NAME", "unknown")
PROJECT_ROOT = Path(os.environ.get("PROJECT_ROOT", "")).resolve() if os.environ.get("PROJECT_ROOT") else Path()
INFER_SCRIPT = Path(os.environ.get("INFER_SCRIPT", "")).resolve() if os.environ.get("INFER_SCRIPT") else Path()


class PredictRequest(BaseModel):
    samples_csv: str
    output_csv: str
    run_id: Optional[str] = None
    artifact_root: Optional[str] = None


class CancelRequest(BaseModel):
    run_id: Optional[str] = None


app = FastAPI(title=f"{MODEL_NAME} inference service")
ACTIVE_PROCESS_LOCK = threading.Lock()
ACTIVE_PROCESS = None  # type: Optional[subprocess.Popen]
ACTIVE_RUN_ID = None  # type: Optional[str]


def _run_subprocess(command: List[str], cwd: Path, run_id: Optional[str] = None) -> Tuple[int, str, Dict[str, object]]:
    global ACTIVE_PROCESS, ACTIVE_RUN_ID

    process = subprocess.Popen(
        command,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )
    with ACTIVE_PROCESS_LOCK:
        ACTIVE_PROCESS = process
        ACTIVE_RUN_ID = run_id

    monitor = ProcessResourceMonitor(process.pid, interval_sec=1.0)
    monitor.start()

    try:
        stdout, _ = process.communicate()
        return process.returncode, stdout, monitor.stop(returncode=process.returncode)
    finally:
        with ACTIVE_PROCESS_LOCK:
            if ACTIVE_PROCESS is process:
                ACTIVE_PROCESS = None
                ACTIVE_RUN_ID = None


def _cancel_active_process(requested_run_id: Optional[str] = None) -> dict[str, object]:
    global ACTIVE_PROCESS, ACTIVE_RUN_ID

    with ACTIVE_PROCESS_LOCK:
        process = ACTIVE_PROCESS
        active_run_id = ACTIVE_RUN_ID
        if process is None:
            return {"canceled": False, "detail": "no active subprocess"}
        if requested_run_id and active_run_id and requested_run_id != active_run_id:
            return {"canceled": False, "detail": f"active subprocess belongs to another run: {active_run_id}"}

    try:
        process.terminate()
        process.wait(timeout=8)
        signal_used = "terminate"
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)
        signal_used = "kill"

    return {
        "canceled": True,
        "detail": f"{MODEL_NAME} subprocess stopped via {signal_used}",
        "run_id": active_run_id,
        "pid": process.pid,
    }


def _safe_persist_result(result_df: pd.DataFrame, output_csv: Path) -> tuple[bool, str | None]:
    try:
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        result_df.to_csv(output_csv, index=False, encoding="utf-8-sig")
        return True, None
    except Exception as exc:  # pragma: no cover - defensive filesystem boundary
        return False, str(exc)


@app.get("/health")
def health() -> Dict[str, object]:
    with ACTIVE_PROCESS_LOCK:
        active_pid = ACTIVE_PROCESS.pid if ACTIVE_PROCESS is not None else None
        active_run_id = ACTIVE_RUN_ID
    return {
        "model_name": MODEL_NAME,
        "project_root": str(PROJECT_ROOT),
        "project_root_exists": PROJECT_ROOT.exists(),
        "infer_script": str(INFER_SCRIPT),
        "infer_script_exists": INFER_SCRIPT.exists(),
        "python_executable": sys.executable,
        "active_pid": active_pid,
        "active_run_id": active_run_id,
        "ready": PROJECT_ROOT.exists() and INFER_SCRIPT.exists(),
    }


@app.post("/predict")
def predict(request: PredictRequest) -> Dict[str, object]:
    samples_csv = Path(request.samples_csv).resolve()
    output_csv = Path(request.output_csv).resolve()

    if not PROJECT_ROOT.exists():
        raise HTTPException(status_code=500, detail=f"Project root does not exist: {PROJECT_ROOT}")
    if not INFER_SCRIPT.exists():
        raise HTTPException(status_code=500, detail=f"Inference script does not exist: {INFER_SCRIPT}")
    if not samples_csv.exists():
        raise HTTPException(status_code=400, detail=f"Samples CSV does not exist: {samples_csv}")

    runtime_dir = Path(tempfile.mkdtemp(prefix=f"{MODEL_NAME.lower()}_service_"))
    temp_output_csv = runtime_dir / "predictions.csv"
    command = [
        sys.executable,
        str(INFER_SCRIPT),
        "--project-root",
        str(PROJECT_ROOT),
        "--samples-csv",
        str(samples_csv),
        "--output-csv",
        str(temp_output_csv),
    ]
    if request.artifact_root:
        command.extend(["--artifact-root", str(Path(request.artifact_root).resolve())])

    try:
        returncode, stdout, resource_report = _run_subprocess(command, cwd=PROJECT_ROOT, run_id=request.run_id)
        if returncode != 0:
            raise HTTPException(
                status_code=500,
                detail={
                    "model_name": MODEL_NAME,
                    "command": command,
                    "run_id": request.run_id,
                    "log": stdout,
                    "resource_report": resource_report,
                },
            )

        if not temp_output_csv.exists():
            raise HTTPException(
                status_code=500,
                detail=f"{MODEL_NAME} did not create output CSV: {temp_output_csv}",
            )

        result_df = pd.read_csv(temp_output_csv)
        persisted, persist_error = _safe_persist_result(result_df, output_csv)
        return {
            "model_name": MODEL_NAME,
            "output_csv": str(output_csv),
            "output_persisted": persisted,
            "persist_error": persist_error,
            "row_count": len(result_df),
            "rows": result_df.to_dict(orient="records"),
            "log": stdout,
            "resource_report": resource_report,
        }
    finally:
        shutil.rmtree(runtime_dir, ignore_errors=True)


@app.post("/cancel-current")
def cancel_current(request: CancelRequest) -> Dict[str, object]:
    return _cancel_active_process(request.run_id)
