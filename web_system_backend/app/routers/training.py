from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..core.config import get_settings
from ..db import get_db
from ..models import DatasetBundle, RunTask
from ..schemas.entities import RunTaskDetailRead, RunTaskRead, TrainingRunCreate
from ..services.legacy_support import cancel_task, create_training_task, fetch_task_payload, refresh_task
from ..services.serializers import task_to_schema
from ..services.task_details import build_task_detail


router = APIRouter(prefix="/api/training-runs", tags=["training"])
settings = get_settings()


@router.get("", response_model=list[RunTaskRead])
def list_training_runs(db: Session = Depends(get_db)) -> list[RunTaskRead]:
    tasks = db.query(RunTask).filter(RunTask.task_type == "training").order_by(RunTask.updated_at.desc(), RunTask.id.desc()).all()
    refreshed: list[RunTask] = []
    for task in tasks:
        try:
            refreshed.append(refresh_task(db, task))
        except Exception:
            refreshed.append(task)
    return [task_to_schema(task) for task in refreshed]


@router.post("", response_model=RunTaskRead)
def create_run(payload: TrainingRunCreate, db: Session = Depends(get_db)) -> RunTaskRead:
    dataset = db.get(DatasetBundle, payload.dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="训练数据集不存在。")
    try:
        task = create_training_task(
            db,
            dataset,
            selected_models=payload.selected_models,
            profile=payload.profile,
            device=payload.device,
            epochs=payload.epochs,
            label_threshold=payload.label_threshold,
            version_note=payload.version_note,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"训练服务调用失败: {exc}") from exc
    return task_to_schema(task)


@router.get("/{task_id}/detail", response_model=RunTaskDetailRead)
def get_run_detail(task_id: int, db: Session = Depends(get_db)) -> RunTaskDetailRead:
    task = db.get(RunTask, task_id)
    if task is None or task.task_type != "training":
        raise HTTPException(status_code=404, detail="训练任务不存在。")

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
    if task is None or task.task_type != "training":
        raise HTTPException(status_code=404, detail="训练任务不存在。")
    try:
        task = refresh_task(db, task, force=True)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"训练任务状态刷新失败: {exc}") from exc
    return task_to_schema(task)


@router.post("/{task_id}/cancel", response_model=RunTaskRead)
def cancel_run_endpoint(task_id: int, db: Session = Depends(get_db)) -> RunTaskRead:
    task = db.get(RunTask, task_id)
    if task is None or task.task_type != "training":
        raise HTTPException(status_code=404, detail="训练任务不存在。")
    try:
        task = cancel_task(db, task)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"训练任务取消失败: {exc}") from exc
    return task_to_schema(task)


@router.get("/{task_id}/artifacts/archive")
def download_training_artifacts(task_id: int, db: Session = Depends(get_db)) -> FileResponse:
    task = db.get(RunTask, task_id)
    if task is None or task.task_type != "training":
        raise HTTPException(status_code=404, detail="训练任务不存在。")

    task_schema = task_to_schema(task)
    if not task_schema.output_path_host:
        raise HTTPException(status_code=404, detail="当前任务还没有可打包的训练产物目录。")

    output_dir = Path(task_schema.output_path_host)
    if not output_dir.exists() or not output_dir.is_dir():
        raise HTTPException(status_code=404, detail="训练产物目录不存在，可能尚未生成或已被清理。")

    archive_base = settings.downloads_root / f"training_task_{task.id}_artifacts"
    archive_path = Path(shutil.make_archive(str(archive_base), "zip", root_dir=str(output_dir)))
    return FileResponse(path=archive_path, filename=archive_path.name, media_type="application/zip")


@router.get("/{task_id}/artifacts/{artifact_path:path}")
def download_training_artifact_file(task_id: int, artifact_path: str, db: Session = Depends(get_db)) -> FileResponse:
    task = db.get(RunTask, task_id)
    if task is None or task.task_type != "training":
        raise HTTPException(status_code=404, detail="训练任务不存在。")

    task_schema = task_to_schema(task)
    if not task_schema.output_path_host:
        raise HTTPException(status_code=404, detail="当前任务还没有可下载的训练产物。")

    output_dir = Path(task_schema.output_path_host).resolve()
    candidate = (output_dir / artifact_path).resolve()
    try:
        candidate.relative_to(output_dir)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="非法的产物文件路径。") from exc

    if not candidate.exists() or not candidate.is_file():
        raise HTTPException(status_code=404, detail="请求的产物文件不存在。")

    return FileResponse(path=candidate, filename=candidate.name)
