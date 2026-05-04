from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import DatasetBundle, RunTask
from ..schemas.entities import InferenceRunCreate, RunTaskDetailRead, RunTaskRead
from ..services.legacy_support import cancel_task, create_inference_task, fetch_task_payload, refresh_task
from ..services.serializers import task_to_schema
from ..services.task_details import build_task_detail


router = APIRouter(prefix="/api/inference-runs", tags=["inference"])


@router.get("", response_model=list[RunTaskRead])
def list_inference_runs(db: Session = Depends(get_db)) -> list[RunTaskRead]:
    tasks = db.query(RunTask).filter(RunTask.task_type == "inference").order_by(RunTask.updated_at.desc(), RunTask.id.desc()).all()
    refreshed: list[RunTask] = []
    for task in tasks:
        try:
            refreshed.append(refresh_task(db, task))
        except Exception:
            refreshed.append(task)
    return [task_to_schema(task) for task in refreshed]


@router.post("", response_model=RunTaskRead)
def create_run(payload: InferenceRunCreate, db: Session = Depends(get_db)) -> RunTaskRead:
    dataset = db.get(DatasetBundle, payload.dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="推理数据集不存在。")
    try:
        task = create_inference_task(
            db,
            dataset,
            selected_models=payload.selected_models,
            model_version_id=payload.model_version_id,
            model_version_ids=payload.model_version_ids,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"推理服务调用失败: {exc}") from exc
    return task_to_schema(task)


@router.get("/{task_id}/detail", response_model=RunTaskDetailRead)
def get_run_detail(task_id: int, db: Session = Depends(get_db)) -> RunTaskDetailRead:
    task = db.get(RunTask, task_id)
    if task is None or task.task_type != "inference":
        raise HTTPException(status_code=404, detail="推理任务不存在。")

    remote_payload = None
    try:
        task = refresh_task(db, task, force=True)
    except Exception:
        pass
    try:
        remote_payload = fetch_task_payload(task)
    except Exception:
        remote_payload = None

    dataset = db.get(DatasetBundle, task.dataset_id) if task.dataset_id else None
    return build_task_detail(task, dataset=dataset, remote_payload=remote_payload)


@router.get("/{task_id}", response_model=RunTaskRead)
def get_run(task_id: int, db: Session = Depends(get_db)) -> RunTaskRead:
    task = db.get(RunTask, task_id)
    if task is None or task.task_type != "inference":
        raise HTTPException(status_code=404, detail="推理任务不存在。")
    try:
        task = refresh_task(db, task, force=True)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"推理任务状态刷新失败: {exc}") from exc
    return task_to_schema(task)


@router.post("/{task_id}/cancel", response_model=RunTaskRead)
def cancel_run_endpoint(task_id: int, db: Session = Depends(get_db)) -> RunTaskRead:
    task = db.get(RunTask, task_id)
    if task is None or task.task_type != "inference":
        raise HTTPException(status_code=404, detail="推理任务不存在。")
    try:
        task = cancel_task(db, task)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"推理任务取消失败: {exc}") from exc
    return task_to_schema(task)


@router.get("/{task_id}/download")
def download_run_result(task_id: int, db: Session = Depends(get_db)) -> FileResponse:
    task = db.get(RunTask, task_id)
    if task is None or task.task_type != "inference":
        raise HTTPException(status_code=404, detail="推理任务不存在。")

    task_schema = task_to_schema(task)
    if not task_schema.output_path_host:
        raise HTTPException(status_code=404, detail="当前任务还没有可下载的结果文件。")

    output_path = Path(task_schema.output_path_host)
    if not output_path.exists() or not output_path.is_file():
        raise HTTPException(status_code=404, detail="结果文件不存在，可能尚未生成或已被清理。")

    return FileResponse(path=output_path, filename=output_path.name, media_type="text/csv")
