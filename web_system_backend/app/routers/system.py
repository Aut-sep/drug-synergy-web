from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import DatasetBundle, RunTask
from ..services.legacy_support import (
    SUMMARY_HEALTHCHECK_TIMEOUT_SECONDS,
    gateway_health,
    list_model_versions,
    system_resource_snapshot,
    training_health,
)


router = APIRouter(prefix="/api/system", tags=["system"])


def _summary_probe_timeout(service_name: str) -> dict[str, object]:
    return {
        "ready": False,
        "degraded": True,
        "probe_mode": "summary",
        "url": "",
        "detail": f"{service_name}摘要快照在 {SUMMARY_HEALTHCHECK_TIMEOUT_SECONDS} 秒内未完成，系统总览已按降级状态返回。",
    }


def _run_summary_probe(service_name: str, future) -> dict[str, object]:
    try:
        return future.result(timeout=SUMMARY_HEALTHCHECK_TIMEOUT_SECONDS + 0.25)
    except FuturesTimeoutError:
        return _summary_probe_timeout(service_name)
    except Exception as exc:  # noqa: BLE001
        return {
            "ready": False,
            "degraded": True,
            "probe_mode": "summary",
            "url": "",
            "detail": f"{service_name}摘要快照获取失败，系统总览已按降级状态返回。{exc}",
        }


@router.get("/summary")
def get_system_summary(db: Session = Depends(get_db)) -> dict[str, object]:
    dataset_count = db.query(DatasetBundle).count()
    inference_run_count = db.query(RunTask).filter(RunTask.task_type == "inference").count()
    training_run_count = db.query(RunTask).filter(RunTask.task_type == "training").count()
    running_run_count = db.query(RunTask).filter(RunTask.local_status.in_(["running", "waiting", "canceling"])).count()

    executor = ThreadPoolExecutor(max_workers=2)
    try:
        gateway_future = executor.submit(
            gateway_health,
            timeout_seconds=SUMMARY_HEALTHCHECK_TIMEOUT_SECONDS,
            summary_only=True,
        )
        training_future = executor.submit(
            training_health,
            timeout_seconds=SUMMARY_HEALTHCHECK_TIMEOUT_SECONDS,
            summary_only=True,
        )
        versions = list_model_versions(prefer_remote=False)
        gateway = _run_summary_probe("推理网关", gateway_future)
        training = _run_summary_probe("训练服务", training_future)
    finally:
        executor.shutdown(wait=False, cancel_futures=True)

    return {
        "dataset_count": dataset_count,
        "inference_run_count": inference_run_count,
        "training_run_count": training_run_count,
        "running_run_count": running_run_count,
        "latest_model_version_count": len(versions),
        "gateway_health": gateway,
        "training_health": training,
        "resource_snapshot": system_resource_snapshot(),
    }
