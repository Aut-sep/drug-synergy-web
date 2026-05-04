from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from ..core.config import from_storage_path, get_settings
from ..models import DatasetBundle, RunTask
from ..schemas.entities import DatasetBundleRead, ModelVersionRead, RunTaskRead


KNOWN_TASK_STATES = {
    "waiting",
    "running",
    "completed",
    "failed",
    "canceling",
    "canceled",
}
TRAINING_REQUIRED_FILES = {
    "samples.csv",
    "drugs.csv",
    "cells_dualsyn.csv",
    "cells_mtl.csv",
    "cells_mvc_exp.csv",
    "cells_mvc_cn.csv",
}

settings = get_settings()


def format_timestamp(value: object) -> str:
    if isinstance(value, datetime):
        return value.isoformat(sep=" ", timespec="seconds")
    return str(value or "")


def coerce_string_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, tuple):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str):
        raw_text = value.strip()
        if not raw_text:
            return []
        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, list):
            return [str(item) for item in parsed if str(item).strip()]
        return [item.strip() for item in raw_text.split(",") if item.strip()]
    return [str(value)]


def coerce_dict(value: object) -> dict[str, Any] | None:
    if value is None:
        return None
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        raw_text = value.strip()
        if not raw_text:
            return None
        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError:
            return {"message": raw_text}
        if isinstance(parsed, dict):
            return parsed
        return {"value": parsed}
    return {"value": value}


def coerce_string_mapping(value: object) -> dict[str, str]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return {
            str(key): str(item)
            for key, item in value.items()
            if str(key).strip() and str(item).strip()
        }
    if isinstance(value, str):
        raw_text = value.strip()
        if not raw_text:
            return {}
        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError:
            return {}
        if isinstance(parsed, dict):
            return coerce_string_mapping(parsed)
    return {}


def normalize_task_state(state: object, *, default: str = "waiting") -> str:
    raw_state = str(state or "").strip().lower()
    aliases = {
        "queued": "waiting",
        "pending": "waiting",
        "cancelled": "canceled",
        "success": "completed",
        "error": "failed",
    }
    normalized = aliases.get(raw_state, raw_state)
    if normalized in KNOWN_TASK_STATES:
        return normalized
    return default


def resolve_bridge_path(raw_path: str | None) -> Path | None:
    """Resolve a path that may come from a remote service to a local filesystem path.

    Handles:
    - Relative storage paths (relative to repo_root)
    - Docker/container paths mapped to local runtime_root
    - WSL paths (/mnt/c/...) on any platform
    - Regular absolute paths
    """
    if not raw_path:
        return None
    normalized = str(raw_path).strip().replace("\\", "/")
    if not normalized:
        return None

    # If path is under the gateway/container mount root, translate to local runtime_root
    gateway_root = settings.legacy_gateway_runtime_root.rstrip("/")
    if gateway_root:
        if normalized.startswith(f"{gateway_root}/"):
            relative = normalized.removeprefix(f"{gateway_root}/")
            return (settings.runtime_root / relative).resolve()
        if normalized == gateway_root:
            return settings.runtime_root.resolve()

    # Handle WSL-style paths (/mnt/c/...) on any platform
    if normalized.startswith("/mnt/"):
        segments = [segment for segment in normalized.split("/") if segment]
        if len(segments) >= 3:
            drive = segments[1].upper()
            try:
                return Path(f"{drive}:/", *segments[2:]).resolve()
            except OSError:
                pass

    # Handle old Docker mount paths
    for old_prefix in ("/workspace/streamlit_system", "/workspace/web_system_runtime"):
        if normalized.startswith(f"{old_prefix}/"):
            relative = normalized.removeprefix(f"{old_prefix}/")
            return (settings.runtime_root / relative).resolve()
        if normalized == old_prefix:
            return settings.runtime_root.resolve()

    # Try as a relative storage path first (relative to repo_root)
    from_storage = from_storage_path(raw_path)
    if from_storage is not None and from_storage.exists():
        return from_storage

    # Fallback: try as a regular filesystem path
    try:
        return Path(raw_path).expanduser().resolve()
    except OSError:
        return None


def infer_dataset_capabilities(record: DatasetBundle) -> tuple[str, bool, bool]:
    files = {item.lower() for item in coerce_string_list(record.files)}
    supports_inference = bool(record.is_ready and str(record.sample_file or "").strip())
    supports_training = supports_inference and TRAINING_REQUIRED_FILES.issubset(files)
    source_type = str(record.source_type or "").lower()

    if "training" in source_type and supports_training:
        bundle_kind = "training"
    elif "demo" in source_type or "inference" in source_type:
        bundle_kind = "inference" if supports_inference else "invalid"
    elif supports_training and supports_inference:
        bundle_kind = "hybrid"
    elif supports_training:
        bundle_kind = "training"
    elif supports_inference:
        bundle_kind = "inference"
    else:
        bundle_kind = "invalid"
    return bundle_kind, supports_inference, supports_training


def dataset_to_schema(record: DatasetBundle) -> DatasetBundleRead:
    bundle_kind, supports_inference, supports_training = infer_dataset_capabilities(record)
    return DatasetBundleRead(
        id=record.id,
        name=record.name,
        bundle_path=record.bundle_path,
        sample_file=record.sample_file,
        source_type=record.source_type,
        description=record.description,
        is_ready=bool(record.is_ready),
        sample_count=int(record.sample_count or 0),
        files=coerce_string_list(record.files),
        validation_detail=record.validation_detail,
        bundle_kind=bundle_kind,
        supports_inference=supports_inference,
        supports_training=supports_training,
        created_at=format_timestamp(record.created_at),
        updated_at=format_timestamp(record.updated_at),
    )


def task_to_schema(task: RunTask) -> RunTaskRead:
    output_path_host = resolve_bridge_path(task.output_path)
    result_download_endpoint = None
    artifacts_download_endpoint = None
    summary = coerce_dict(task.summary) or {}
    model_version_ids = coerce_string_mapping(summary.get("model_version_ids"))
    if task.task_type == "inference" and output_path_host and output_path_host.exists() and output_path_host.is_file():
        result_download_endpoint = f"/api/inference-runs/{task.id}/download"
    if task.task_type == "training" and output_path_host and output_path_host.exists() and output_path_host.is_dir():
        artifacts_download_endpoint = f"/api/training-runs/{task.id}/artifacts/archive"
    return RunTaskRead(
        id=task.id,
        task_type=task.task_type,
        title=task.title,
        local_status=normalize_task_state(task.local_status, default="failed"),
        remote_state=str(task.remote_state or ""),
        remote_run_id=str(task.remote_run_id or ""),
        dataset_id=task.dataset_id,
        model_version_id=task.model_version_id,
        model_version_ids=model_version_ids,
        version_group_id=str(summary.get("version_group_id") or summary.get("version_id") or task.model_version_id or ""),
        version_group_name=str(summary.get("version_group_name") or summary.get("group_name") or summary.get("version_note") or ""),
        selected_models=coerce_string_list(task.selected_models),
        output_path=task.output_path,
        output_path_host=str(output_path_host) if output_path_host else None,
        output_available=bool(output_path_host and output_path_host.exists()),
        result_download_endpoint=result_download_endpoint,
        artifacts_download_endpoint=artifacts_download_endpoint,
        log_excerpt=task.log_excerpt,
        error_message=task.error_message,
        summary=summary or None,
        detail_endpoint=f"/api/{task.task_type}-runs/{task.id}/detail",
        created_at=format_timestamp(task.created_at),
        updated_at=format_timestamp(task.updated_at),
    )


def model_version_to_schema(payload: dict[str, Any]) -> ModelVersionRead:
    version_group_name = str(
        payload.get("version_group_name")
        or payload.get("group_name")
        or payload.get("version_note")
        or ""
    )
    return ModelVersionRead(
        version_id=str(payload.get("version_id") or ""),
        base_version_id=str(payload.get("base_version_id") or "") or None,
        group_id=str(payload.get("group_id") or payload.get("base_version_id") or payload.get("version_id") or "") or None,
        group_name=version_group_name or None,
        version_group_name=version_group_name or None,
        model_name=str(payload.get("model_name") or "") or None,
        created_at=str(payload.get("created_at") or "") or None,
        selected_models=coerce_string_list(payload.get("selected_models")),
        profile=str(payload.get("profile") or "") or None,
        version_note=str(payload.get("version_note") or "") or None,
        version_dir=str(payload.get("version_dir") or "") or None,
        artifact_root=str(payload.get("artifact_root") or "") or None,
        is_virtual_child=bool(payload.get("is_virtual_child", False)),
        source_kind=str(payload.get("source_kind") or "") or None,
        availability_note=str(payload.get("availability_note") or "") or None,
    )
