from __future__ import annotations

import csv
import json
import logging
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from requests import Response
from sqlalchemy.orm import Session

from ..core.config import from_storage_path, get_settings, to_storage_path
from ..models import DatasetBundle, RunTask
from .serializers import coerce_string_list, normalize_task_state


ALL_MODELS = ["DualSyn", "MFSynDCP", "MVCASyn", "MTLSynergy"]
TERMINAL_STATES = {"completed", "failed", "canceled"}
ACTIVE_STATES = {"running", "waiting", "canceling"}
SAMPLE_REQUIRED_COLUMNS = {"sample_id", "drug_a_name", "drug_b_name", "cell_line"}
TRAINING_REQUIRED_FILES = {
    "samples.csv",
    "drugs.csv",
    "cells_dualsyn.csv",
    "cells_mtl.csv",
    "cells_mvc_exp.csv",
    "cells_mvc_cn.csv",
}
HEALTHCHECK_TIMEOUT_SECONDS = 10
LIST_TIMEOUT_SECONDS = 10
LIGHTWEIGHT_TIMEOUT_SECONDS = 6
SUMMARY_HEALTHCHECK_TIMEOUT_SECONDS = 2
SUMMARY_LIGHTWEIGHT_TIMEOUT_SECONDS = 2
RUN_CREATE_TIMEOUT_SECONDS = 30
RUN_POLL_TIMEOUT_SECONDS = 12
RUN_CANCEL_TIMEOUT_SECONDS = 15

settings = get_settings()
logger = logging.getLogger(__name__)

try:
    import psutil
except ImportError:  # pragma: no cover - optional at runtime
    psutil = None  # type: ignore[assignment]


class LegacyBridgeError(RuntimeError):
    pass


class RemoteRunMissingError(LegacyBridgeError):
    pass


def _rewrite_legacy_runtime_host_path(path: Path) -> Path | None:
    """Resolve a legacy path relative to the current runtime or repo root.

    Tries to find the matching directory under runtime_root or repo_root
    by walking up from the given path until a known anchor is found.
    """
    resolved = path.expanduser().resolve(strict=False)

    # If the path is already under the current runtime root, return as-is
    try:
        resolved.relative_to(settings.runtime_root.resolve())
        return resolved
    except ValueError:
        pass

    # If the path is under the current repo root, return as-is
    try:
        resolved.relative_to(settings.repo_root.resolve())
        return resolved
    except ValueError:
        pass

    # Try to find a matching sub-path by matching directory names
    parts = resolved.parts
    for marker in ("web_system_runtime", "streamlit_system"):
        try:
            marker_index = next(index for index, part in enumerate(parts) if part.lower() == marker)
        except StopIteration:
            continue
        relative = Path(*parts[marker_index + 1:]) if marker_index + 1 < len(parts) else Path()

        if not relative.parts:
            return settings.runtime_root.resolve()

        head = relative.parts[0]
        if head == "workspace" and len(relative.parts) >= 2 and relative.parts[1] == "benchmark_factory":
            return (settings.repo_root / "benchmark_factory" / Path(*relative.parts[2:])).resolve()
        if head in {"outputs", "trained_model_versions", "training_bundles", "user_bundles"}:
            return (settings.runtime_root / relative).resolve()
        return (settings.runtime_root / relative).resolve()

    return None


def rewrite_legacy_storage_path(raw_path: str | None) -> str | None:
    if raw_path is None:
        return None

    text = str(raw_path).strip()
    if not text:
        return raw_path

    normalized = text.replace("\\", "/")

    # Handle old Docker mount paths (/workspace/streamlit_system, /workspace/web_system_runtime)
    for old_prefix in ("/workspace/streamlit_system", "/workspace/web_system_runtime"):
        if normalized == old_prefix:
            return str(settings.runtime_root.resolve())
        if normalized.startswith(f"{old_prefix}/"):
            relative = normalized.removeprefix(f"{old_prefix}/")
            return str(settings.runtime_root.resolve() / relative)

    # Handle WSL-style paths (/mnt/c/...) on any platform
    if normalized.startswith("/mnt/"):
        segments = [segment for segment in normalized.split("/") if segment]
        if len(segments) >= 3:
            drive = segments[1].upper()
            windows_path = Path(f"{drive}:/", *segments[2:])
            rewritten = _rewrite_legacy_runtime_host_path(windows_path)
            if rewritten is not None:
                return str(rewritten)

    try:
        candidate = Path(text).expanduser()
    except OSError:
        return raw_path

    rewritten = _rewrite_legacy_runtime_host_path(candidate)
    if rewritten is not None:
        return str(rewritten)
    return raw_path


def migrate_legacy_storage_paths(db: Session) -> int:
    """Convert legacy absolute paths in the database to relative storage paths."""
    changed = 0

    for dataset in db.query(DatasetBundle).all():
        current = dataset.bundle_path
        # Skip paths that are already relative (no drive letter, no leading /)
        path_obj = Path(current)
        if path_obj.is_absolute() or current.startswith("/"):
            # First try to resolve the old path to a local path
            rewritten = rewrite_legacy_storage_path(current)
            if rewritten and rewritten != current:
                resolved = Path(rewritten)
                if resolved.exists():
                    current = str(resolved)
            # Convert to relative storage path
            storage = to_storage_path(current)
            if storage != dataset.bundle_path:
                dataset.bundle_path = storage
                changed += 1

    for task in db.query(RunTask).all():
        if task.output_path:
            path_obj = Path(task.output_path)
            if path_obj.is_absolute() or task.output_path.startswith("/"):
                rewritten = rewrite_legacy_storage_path(task.output_path)
                if rewritten and rewritten != task.output_path:
                    storage = to_storage_path(rewritten)
                    if storage != task.output_path:
                        task.output_path = storage
                        changed += 1

    if changed:
        db.commit()
    return changed


def _ensure_repo_path() -> None:
    repo_root = str(settings.repo_root)
    runtime_root = str(settings.runtime_root)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    if runtime_root not in sys.path:
        sys.path.insert(0, runtime_root)


def _host_to_gateway_path(path: Path) -> str:
    """Translate a host path to the path expected by the inference gateway.

    Produces a path under gateway_runtime_root (typically a Docker container path
    like /workspace/web_system_runtime/...). The gateway resolves this relative to
    its own filesystem.
    """
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(settings.runtime_root.resolve())
    except ValueError:
        # Path is outside runtime_root; send the absolute path as fallback
        return str(resolved)
    mount_root = settings.legacy_gateway_runtime_root.rstrip("/")
    return f"{mount_root}/{relative.as_posix()}"


def _host_to_remote_path(path: Path) -> str:
    """Return the absolute path on the host filesystem (cross-platform).

    Used to send paths to training services running on the same machine.
    """
    return str(path.resolve())


def _safe_response_json(response: Response) -> dict[str, Any]:
    if not response.content:
        return {}
    try:
        payload = response.json()
    except ValueError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _response_error_text(response: Response) -> str:
    payload = _safe_response_json(response)
    detail = payload.get("detail") or payload.get("error") or response.text.strip()
    return str(detail).strip() or f"HTTP {response.status_code}"


def _request_json(
    method: str,
    url: str,
    *,
    timeout: int,
    context: str,
    json_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    try:
        response = requests.request(method, url, json=json_payload, timeout=timeout)
    except requests.RequestException as exc:
        raise LegacyBridgeError(f"{context}: {exc}") from exc

    if response.status_code == 404:
        raise RemoteRunMissingError(f"{context}: {_response_error_text(response)}")
    if response.status_code >= 400:
        raise LegacyBridgeError(f"{context}: {_response_error_text(response)}")
    return _safe_response_json(response)


def _load_bundle_helpers() -> tuple[Any, list[str]]:
    _ensure_repo_path()
    from runtime_support.bundle import inspect_bundle  # type: ignore
    from shared.sample_validation import ALL_MODELS as legacy_models  # type: ignore

    return inspect_bundle, list(legacy_models)


def _probe_sample_file(sample_path: Path) -> tuple[int, list[str]]:
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            with sample_path.open("r", encoding=encoding, newline="") as handle:
                reader = csv.reader(handle)
                headers = next(reader, [])
                row_count = sum(1 for _ in reader)
            return row_count, [str(item).strip() for item in headers if str(item).strip()]
        except UnicodeDecodeError:
            continue
    with sample_path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        reader = csv.reader(handle)
        headers = next(reader, [])
        row_count = sum(1 for _ in reader)
    return row_count, [str(item).strip() for item in headers if str(item).strip()]


def _fallback_bundle_metadata(bundle_path: Path, *, detail: str) -> dict[str, Any]:
    csv_files = sorted(path.name for path in bundle_path.glob("*.csv"))
    preferred_sample = ""
    if "samples.csv" in csv_files:
        preferred_sample = "samples.csv"
    else:
        preferred_sample = next((name for name in csv_files if name.startswith("samples")), csv_files[0] if csv_files else "")

    sample_count = 0
    columns: list[str] = []
    if preferred_sample:
        try:
            sample_count, columns = _probe_sample_file(bundle_path / preferred_sample)
        except Exception as exc:  # noqa: BLE001
            detail = f"{detail}; failed to inspect {preferred_sample}: {exc}" if detail else str(exc)

    column_set = {item.strip() for item in columns}
    sample_ready = bool(preferred_sample) and SAMPLE_REQUIRED_COLUMNS.issubset(column_set)
    training_missing = sorted(name for name in TRAINING_REQUIRED_FILES if not (bundle_path / name).exists())

    messages: list[str] = []
    if sample_ready:
        messages.append("Fallback validation succeeded for the sample file headers.")
    elif preferred_sample:
        messages.append(f"Fallback validation found missing required columns in {preferred_sample}.")
    else:
        messages.append("No CSV sample file was found in the uploaded bundle.")
    if training_missing:
        messages.append(f"Training-required files still missing: {', '.join(training_missing)}.")
    if detail:
        messages.append(f"Advanced validation unavailable: {detail}")

    return {
        "sample_file": preferred_sample,
        "is_ready": sample_ready,
        "sample_count": sample_count,
        "files": csv_files,
        "validation_detail": " ".join(messages).strip(),
    }


def collect_bundle_metadata(bundle_path: Path) -> dict[str, Any]:
    try:
        inspect_bundle, legacy_models = _load_bundle_helpers()
        bundle_info = inspect_bundle(bundle_path, selected_models=legacy_models)
        files = sorted(path.name for path in bundle_path.glob("*.csv"))
        detail = "Bundle passed the runtime sample validation checks."
        missing = bundle_info.get("missing_requirements") or []
        if missing:
            detail = "; ".join(str(item) for item in missing)
        return {
            "sample_file": str(bundle_info.get("default_sample_file") or ""),
            "is_ready": bool(bundle_info.get("bundle_ready", False)),
            "sample_count": int(bundle_info.get("sample_count", 0) or 0),
            "files": files,
            "validation_detail": detail,
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning("Falling back to local bundle inspection for %s: %s", bundle_path, exc)
        return _fallback_bundle_metadata(bundle_path, detail=str(exc))


def slugify_name(raw_name: str) -> str:
    text = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in raw_name.strip())
    compact = "_".join(part for part in text.split("_") if part)
    return compact[:80] or "dataset_bundle"


def _sanitize_upload_filename(raw_name: str, *, index: int) -> str:
    candidate = Path(str(raw_name or "")).name
    suffix = Path(candidate).suffix[:16]
    stem = Path(candidate).stem or f"file_{index}"
    safe_stem = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in stem).strip("._")
    safe_stem = safe_stem[:100] or f"file_{index}"
    safe_suffix = "".join(ch if ch.isalnum() or ch in {".", "_"} else "_" for ch in suffix).strip()
    return f"{safe_stem}{safe_suffix}" if safe_suffix else safe_stem


def persist_uploaded_bundle(
    name: str,
    description: str,
    file_items: list[Any],
    source_type: str = "upload",
) -> tuple[Path, dict[str, Any]]:
    bundle_dir = settings.uploads_root / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{slugify_name(name)}"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    used_names: set[str] = set()

    try:
        for index, upload in enumerate(file_items, start=1):
            sanitized = _sanitize_upload_filename(getattr(upload, "filename", ""), index=index)
            stem = Path(sanitized).stem
            suffix = Path(sanitized).suffix
            final_name = sanitized
            counter = 2
            while final_name.lower() in used_names:
                final_name = f"{stem}_{counter}{suffix}"
                counter += 1
            used_names.add(final_name.lower())

            target_path = bundle_dir / final_name
            with target_path.open("wb") as buffer:
                shutil.copyfileobj(upload.file, buffer)

        metadata = collect_bundle_metadata(bundle_dir)
        metadata["description"] = description
        metadata["source_type"] = source_type
        return bundle_dir, metadata
    except Exception:
        shutil.rmtree(bundle_dir, ignore_errors=True)
        raise
    finally:
        for upload in file_items:
            try:
                upload.file.close()
            except Exception:
                continue


def upsert_dataset_bundle(
    db: Session,
    *,
    name: str,
    bundle_path: Path,
    description: str,
    source_type: str,
) -> DatasetBundle:
    metadata = collect_bundle_metadata(bundle_path)
    storage_path = to_storage_path(bundle_path)
    record = db.query(DatasetBundle).filter(DatasetBundle.bundle_path == storage_path).first()
    if record is None:
        record = DatasetBundle(
            name=name,
            bundle_path=storage_path,
            description=description,
            source_type=source_type,
        )
        db.add(record)

    record.name = name
    record.description = description
    record.source_type = source_type
    record.sample_file = str(metadata["sample_file"] or "")
    record.is_ready = bool(metadata["is_ready"])
    record.sample_count = int(metadata["sample_count"] or 0)
    record.files = coerce_string_list(metadata["files"])
    record.validation_detail = str(metadata["validation_detail"] or "")
    db.commit()
    db.refresh(record)
    return record


def seed_builtin_bundles(db: Session) -> None:
    candidates = [
        (
            "system_demo_inference_bundle",
            settings.repo_root / "benchmark_factory" / "demo_bundles" / "system_showcase_unseen_pair_inference",
            "built_in_demo",
            "Inference demo bundle provided by the standalone web runtime.",
        ),
        (
            "smoke_training_bundle",
            settings.training_bundles_root / "smoke_train_10_samples",
            "built_in_training",
            "Small built-in bundle for training smoke checks.",
        ),
    ]
    for name, path, source_type, description in candidates:
        if not path.exists():
            continue
        try:
            upsert_dataset_bundle(db, name=name, bundle_path=path, description=description, source_type=source_type)
        except Exception:  # noqa: BLE001
            logger.exception("Failed to seed built-in dataset bundle: %s", path)


def _summary_health_failure_detail(service_name: str, timeout_seconds: int, exc: Exception) -> dict[str, Any]:
    return {
        "ready": False,
        "detail": f"{service_name}摘要快照在 {timeout_seconds} 秒内未完成，系统总览已按降级状态返回。",
        "url": "",
        "probe_mode": "summary",
        "degraded": True,
    }


def gateway_health(*, timeout_seconds: int = HEALTHCHECK_TIMEOUT_SECONDS, summary_only: bool = False) -> dict[str, Any]:
    url = settings.legacy_gateway_url
    if not url:
        return {"ready": False, "detail": "推理网关地址未配置。", "url": "", "probe_mode": "disabled", "degraded": True}
    try:
        payload = _request_json(
            "get",
            f"{url.rstrip('/')}/health",
            timeout=timeout_seconds,
            context="Legacy inference gateway health check failed",
        )
        all_ready = bool(payload.get("all_ready"))
        return {
            "ready": all_ready,
            "detail": "推理网关可用。" if all_ready else "推理网关已响应，但当前状态未完全就绪。",
            "url": url,
            "probe_mode": "summary" if summary_only else "full",
            "degraded": not all_ready,
        }
    except LegacyBridgeError as exc:
        if summary_only:
            failure = _summary_health_failure_detail("推理网关", timeout_seconds, exc)
            failure["url"] = url
            return failure
        return {"ready": False, "detail": "推理网关健康检查失败。", "url": url, "probe_mode": "failed", "degraded": True}


def training_health(
    *,
    timeout_seconds: int = HEALTHCHECK_TIMEOUT_SECONDS,
    summary_only: bool = False,
) -> dict[str, Any]:
    url = settings.legacy_training_url
    if not url:
        return {"ready": False, "detail": "训练服务地址未配置。", "url": "", "probe_mode": "disabled", "degraded": True}
    try:
        payload = _request_json(
            "get",
            f"{url.rstrip('/')}/health",
            timeout=timeout_seconds,
            context="Legacy training service health check failed",
        )
        ready = bool(payload.get("ready"))
        return {
            "ready": ready,
            "detail": "训练服务可用。" if ready else "训练服务已响应，但当前状态未完全就绪。",
            "url": url,
            "probe_mode": "summary" if summary_only else "full",
            "degraded": not ready,
        }
    except LegacyBridgeError as exc:
        if summary_only:
            failure = _summary_health_failure_detail("训练服务", timeout_seconds, exc)
            failure["url"] = url
            return failure
        try:
            _request_json(
                "get",
                f"{url.rstrip('/')}/model-versions",
                timeout=LIGHTWEIGHT_TIMEOUT_SECONDS,
                context="Legacy training service lightweight probe failed",
            )
            return {
                "ready": True,
                "detail": "训练服务已响应轻量探测，但完整健康检查未完全稳定。",
                "url": url,
                "probe_mode": "lightweight",
                "degraded": True,
            }
        except LegacyBridgeError:
            return {"ready": False, "detail": "训练服务健康检查失败。", "url": url, "probe_mode": "failed", "degraded": True}


def system_resource_snapshot() -> dict[str, Any]:
    if psutil is None:
        return {
            "monitoring_available": False,
            "detail": "psutil is not installed in the backend environment.",
        }

    try:
        vm = psutil.virtual_memory()
        disk = psutil.disk_usage(str(settings.repo_root))
        load_avg = os.getloadavg() if hasattr(os, "getloadavg") else None
        return {
            "monitoring_available": True,
            "detail": "",
            "cpu_percent": round(float(psutil.cpu_percent(interval=0.2)), 2),
            "memory_percent": round(float(vm.percent), 2),
            "memory_used_gb": round(float(vm.used) / (1024 ** 3), 2),
            "memory_total_gb": round(float(vm.total) / (1024 ** 3), 2),
            "disk_percent": round(float(disk.percent), 2),
            "disk_used_gb": round(float(disk.used) / (1024 ** 3), 2),
            "disk_total_gb": round(float(disk.total) / (1024 ** 3), 2),
            "load_average": [round(float(item), 2) for item in load_avg] if load_avg else [],
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "monitoring_available": False,
            "detail": f"Failed to collect backend resource metrics: {exc}",
        }


def list_model_versions(*, prefer_remote: bool = True, remote_timeout: int = LIST_TIMEOUT_SECONDS) -> list[dict[str, Any]]:
    if prefer_remote and settings.legacy_training_url:
        try:
            payload = _request_json(
                "get",
                f"{settings.legacy_training_url.rstrip('/')}/model-versions",
                timeout=remote_timeout,
                context="Failed to fetch model versions from the legacy training service",
            )
            versions = payload.get("versions")
            if isinstance(versions, list) and versions:
                return [item for item in versions if isinstance(item, dict)]
        except LegacyBridgeError:
            pass

    trained_root = settings.trained_model_root
    if not trained_root.exists():
        return []

    versions: list[dict[str, Any]] = []
    for version_dir in sorted(
        [path for path in trained_root.iterdir() if path.is_dir()],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    ):
        manifest_path = version_dir / "manifest.json"
        payload: dict[str, Any] | None = None
        if manifest_path.exists():
            try:
                raw_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            except Exception:
                raw_payload = None
            if isinstance(raw_payload, dict):
                payload = raw_payload

        if payload is None:
            selected_models = sorted(
                {
                    path.stem
                    for path in (version_dir / "logs").glob("*.log")
                    if path.is_file() and path.stem in ALL_MODELS
                }
            )
            payload = {
                "version_id": version_dir.name,
                "created_at": datetime.fromtimestamp(version_dir.stat().st_mtime).isoformat(timespec="seconds"),
                "selected_models": selected_models,
                "profile": "",
                "version_note": "",
                "source_kind": "directory_fallback",
                "availability_note": "This historical version was reconstructed from the training output directory because manifest.json is missing.",
            }
        else:
            payload["source_kind"] = payload.get("source_kind") or "manifest"
            payload["availability_note"] = payload.get("availability_note") or ""

        payload["version_dir"] = str(version_dir)
        versions.append(payload)
    return versions


def _extract_log(payload: dict[str, Any]) -> str:
    full_log = str(payload.get("full_log") or "").strip()
    if full_log:
        return "\n".join(full_log.splitlines()[-20:])
    lines = payload.get("latest_log_lines") or []
    return "\n".join(str(item) for item in list(lines)[-20:])


def _parse_remote_datetime(raw_value: object) -> datetime | None:
    text = str(raw_value or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def _build_training_summary(payload: dict[str, Any], fallback_models: list[str]) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "version_id": payload.get("version_id"),
        "selected_models": payload.get("selected_models", fallback_models),
    }
    for key in ("phase_label", "progress_percent", "current_model", "started_at", "finished_at"):
        value = payload.get(key)
        if value not in (None, "", []):
            summary[key] = value

    started_at = _parse_remote_datetime(payload.get("started_at"))
    if payload.get("state") == "running" and started_at is not None:
        now = datetime.now(started_at.tzinfo) if started_at.tzinfo else datetime.now()
        elapsed_seconds = max((now - started_at).total_seconds(), 0.0)
        summary["elapsed_minutes"] = round(elapsed_seconds / 60.0, 1)
        if elapsed_seconds >= 90:
            summary["execution_note"] = (
                "训练任务已持续较长时间。当前设备环境可能不支持完整训练，"
                "建议将其视为受限执行状态，并结合日志与产物目录判断。"
            )
    return summary


def validate_selected_models(selected_models: list[str]) -> None:
    unknown = [model_name for model_name in selected_models if model_name not in ALL_MODELS]
    if unknown:
        raise ValueError(f"Unsupported models: {unknown}")
    if not selected_models:
        raise ValueError("At least one model must be selected.")


def validate_inference_dataset(dataset: DatasetBundle) -> None:
    bundle_path = from_storage_path(dataset.bundle_path)
    if bundle_path is None or not bundle_path.exists():
        raise ValueError(f"Dataset bundle path does not exist: {dataset.bundle_path}")
    if not dataset.is_ready:
        detail = dataset.validation_detail or "The dataset bundle has not passed validation yet."
        raise ValueError(detail)
    sample_file = (dataset.sample_file or "").strip()
    if not sample_file:
        raise ValueError("The dataset bundle does not have a usable sample file.")
    sample_path = bundle_path / sample_file
    if not sample_path.exists():
        raise ValueError(f"Sample file does not exist: {sample_path}")


def validate_training_dataset(dataset: DatasetBundle) -> None:
    validate_inference_dataset(dataset)
    bundle_path = from_storage_path(dataset.bundle_path)
    if bundle_path is None:
        raise ValueError(f"Dataset bundle path is invalid: {dataset.bundle_path}")
    missing = sorted(name for name in TRAINING_REQUIRED_FILES if not (bundle_path / name).exists())
    if missing:
        raise ValueError(f"Training bundle is missing required files: {missing}")


def _task_log_with_note(task: RunTask, note: str) -> str:
    previous = str(task.log_excerpt or "").strip()
    if not previous:
        return note
    if note in previous:
        return previous
    return f"{previous}\n{note}"


def _finalize_missing_remote_task(db: Session, task: RunTask, *, detail: str, canceled: bool = False) -> RunTask:
    task.remote_state = "not_found"
    task.local_status = "canceled" if canceled or task.local_status == "canceling" else "failed"
    note = (
        "The legacy service no longer tracks this run, so it was marked canceled locally."
        if task.local_status == "canceled"
        else "The legacy service no longer tracks this run, so it was marked failed locally."
    )
    task.log_excerpt = _task_log_with_note(task, note)
    if not task.error_message:
        task.error_message = detail
    db.commit()
    db.refresh(task)
    return task


def create_inference_task(
    db: Session,
    dataset: DatasetBundle,
    *,
    selected_models: list[str],
    model_version_id: str,
) -> RunTask:
    validate_selected_models(selected_models)
    validate_inference_dataset(dataset)

    payload = {
        "samples_csv": _host_to_gateway_path(from_storage_path(dataset.bundle_path) / dataset.sample_file),
        "selected_models": selected_models,
        "output_root": _host_to_gateway_path(settings.outputs_root / "inference"),
        "model_version_id": model_version_id,
    }
    remote = _request_json(
        "post",
        f"{settings.legacy_gateway_url.rstrip('/')}/runs",
        json_payload=payload,
        timeout=RUN_CREATE_TIMEOUT_SECONDS,
        context="Failed to create an inference run in the legacy gateway",
    )

    task = RunTask(
        task_type="inference",
        title=f"Inference - {dataset.name}",
        local_status=normalize_task_state(remote.get("state"), default="waiting"),
        remote_state=str(remote.get("state") or ""),
        remote_run_id=str(remote.get("run_id") or ""),
        dataset_id=dataset.id,
        model_version_id=model_version_id,
        selected_models=list(selected_models),
        output_path=remote.get("output_path"),
        log_excerpt=_extract_log(remote),
        error_message=str(remote.get("error") or ""),
        summary=remote.get("summary") if isinstance(remote.get("summary"), dict) else None,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def create_training_task(
    db: Session,
    dataset: DatasetBundle,
    *,
    selected_models: list[str],
    profile: str,
    device: str,
    epochs: int | None,
    label_threshold: float,
    version_note: str,
) -> RunTask:
    validate_selected_models(selected_models)
    validate_training_dataset(dataset)

    payload = {
        "bundle_path": _host_to_remote_path(from_storage_path(dataset.bundle_path)),
        "selected_models": selected_models,
        "profile": profile,
        "device": device,
        "epochs": epochs,
        "label_source": "threshold",
        "label_threshold": label_threshold,
        "fold_strategy": "pair_group",
        "version_note": version_note,
    }
    remote = _request_json(
        "post",
        f"{settings.legacy_training_url.rstrip('/')}/training-runs",
        json_payload=payload,
        timeout=RUN_CREATE_TIMEOUT_SECONDS,
        context="Failed to create a training run in the legacy training service",
    )

    task = RunTask(
        task_type="training",
        title=f"Training - {dataset.name}",
        local_status=normalize_task_state(remote.get("state"), default="waiting"),
        remote_state=str(remote.get("state") or ""),
        remote_run_id=str(remote.get("run_id") or ""),
        dataset_id=dataset.id,
        model_version_id=None,
        selected_models=list(selected_models),
        output_path=remote.get("version_dir"),
        log_excerpt=_extract_log(remote),
        error_message=str(remote.get("error") or ""),
        summary=_build_training_summary(remote, list(selected_models)),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def refresh_task(db: Session, task: RunTask, *, force: bool = False) -> RunTask:
    if not task.remote_run_id:
        return task
    if not force and task.local_status in TERMINAL_STATES:
        return task

    if task.task_type == "inference":
        url = f"{settings.legacy_gateway_url.rstrip('/')}/runs/{task.remote_run_id}"
        context = f"Failed to refresh inference run {task.remote_run_id}"
    else:
        url = f"{settings.legacy_training_url.rstrip('/')}/training-runs/{task.remote_run_id}"
        context = f"Failed to refresh training run {task.remote_run_id}"

    try:
        payload = _request_json("get", url, timeout=RUN_POLL_TIMEOUT_SECONDS, context=context)
    except RemoteRunMissingError as exc:
        if task.local_status in TERMINAL_STATES:
            return task
        return _finalize_missing_remote_task(db, task, detail=str(exc))
    except LegacyBridgeError:
        if task.local_status in TERMINAL_STATES:
            return task
        raise

    task.local_status = normalize_task_state(payload.get("state"), default=task.local_status or "waiting")
    task.remote_state = str(payload.get("state") or task.remote_state or "")
    task.log_excerpt = _extract_log(payload)
    task.error_message = str(payload.get("error") or "")
    task.output_path = str(payload.get("output_path") or payload.get("version_dir") or task.output_path or "")
    summary = payload.get("summary")
    if task.task_type == "training":
        summary = _build_training_summary(payload, coerce_string_list(task.selected_models))
    task.summary = summary if isinstance(summary, dict) else task.summary
    db.commit()
    db.refresh(task)
    return task


def fetch_task_payload(task: RunTask) -> dict[str, Any] | None:
    if not task.remote_run_id:
        return None

    if task.task_type == "inference":
        url = f"{settings.legacy_gateway_url.rstrip('/')}/runs/{task.remote_run_id}"
        context = f"Failed to fetch inference run details for {task.remote_run_id}"
    else:
        url = f"{settings.legacy_training_url.rstrip('/')}/training-runs/{task.remote_run_id}"
        context = f"Failed to fetch training run details for {task.remote_run_id}"

    return _request_json("get", url, timeout=RUN_POLL_TIMEOUT_SECONDS, context=context)


def cancel_task(db: Session, task: RunTask) -> RunTask:
    if not task.remote_run_id or task.local_status in TERMINAL_STATES:
        return task

    if task.task_type == "inference":
        url = f"{settings.legacy_gateway_url.rstrip('/')}/runs/{task.remote_run_id}/cancel"
        context = f"Failed to cancel inference run {task.remote_run_id}"
    else:
        url = f"{settings.legacy_training_url.rstrip('/')}/training-runs/{task.remote_run_id}/cancel"
        context = f"Failed to cancel training run {task.remote_run_id}"

    try:
        payload = _request_json("post", url, timeout=RUN_CANCEL_TIMEOUT_SECONDS, context=context)
    except RemoteRunMissingError as exc:
        return _finalize_missing_remote_task(db, task, detail=str(exc), canceled=True)

    task.local_status = normalize_task_state(payload.get("state"), default="canceling")
    task.remote_state = str(payload.get("state") or task.remote_state or "")
    task.log_excerpt = _extract_log(payload)
    task.error_message = str(payload.get("error") or "")
    db.commit()
    db.refresh(task)
    return task


def refresh_active_tasks(db: Session, *, limit: int = 20) -> list[RunTask]:
    tasks = (
        db.query(RunTask)
        .filter(RunTask.local_status.in_(sorted(ACTIVE_STATES)))
        .order_by(RunTask.updated_at.desc(), RunTask.id.desc())
        .limit(limit)
        .all()
    )
    refreshed: list[RunTask] = []
    for task in tasks:
        try:
            refreshed.append(refresh_task(db, task, force=True))
        except LegacyBridgeError as exc:
            logger.warning("Skipping task refresh for %s/%s: %s", task.task_type, task.id, exc)
            refreshed.append(task)
    return refreshed
