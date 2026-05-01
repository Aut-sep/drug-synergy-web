from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from ..models import DatasetBundle, RunTask
from ..schemas.entities import ArtifactFileRead, RunTaskDetailRead
from .serializers import dataset_to_schema, resolve_bridge_path, task_to_schema


def _read_csv_preview(csv_path: Path, *, limit: int = 20) -> tuple[list[str], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    columns: list[str] = []
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            with csv_path.open("r", encoding=encoding, newline="") as handle:
                reader = csv.DictReader(handle)
                columns = list(reader.fieldnames or [])
                for index, row in enumerate(reader):
                    rows.append({key: row.get(key, "") for key in columns})
                    if index + 1 >= limit:
                        break
            return columns, rows
        except UnicodeDecodeError:
            rows.clear()
            columns = []
            continue
    return columns, rows


def _list_artifact_files(root: Path, *, limit: int = 80) -> list[str]:
    if not root.exists():
        return []
    files: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        files.append(str(path.relative_to(root)).replace("\\", "/"))
        if len(files) >= limit:
            break
    return files


def _build_artifact_items(task: RunTask, root: Path, *, limit: int = 80) -> list[ArtifactFileRead]:
    if task.task_type != "training" or not root.exists():
        return []
    items: list[ArtifactFileRead] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = str(path.relative_to(root)).replace("\\", "/")
        items.append(
            ArtifactFileRead(
                path=relative,
                size_bytes=path.stat().st_size,
                download_endpoint=f"/api/training-runs/{task.id}/artifacts/{relative}",
            )
        )
        if len(items) >= limit:
            break
    return items


def _resolve_inference_preview_path(output_path_host: Path) -> Path | None:
    if output_path_host.is_file() and output_path_host.suffix.lower() == ".csv":
        return output_path_host
    if output_path_host.is_dir():
        return next((path for path in sorted(output_path_host.glob("*.csv")) if path.is_file()), None)
    return None


def _load_manifest(version_dir: Path) -> dict[str, Any] | None:
    manifest_path = version_dir / "manifest.json"
    if not manifest_path.exists():
        return None
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def build_task_detail(
    task: RunTask,
    *,
    dataset: DatasetBundle | None = None,
    remote_payload: dict[str, Any] | None = None,
) -> RunTaskDetailRead:
    base = task_to_schema(task)
    output_path_host = resolve_bridge_path(task.output_path)
    log_text = str(task.log_excerpt or "")
    log_full_available = False

    if isinstance(remote_payload, dict):
        full_log = str(remote_payload.get("full_log") or "").strip()
        if full_log:
            log_text = full_log
            log_full_available = True
        elif remote_payload.get("latest_log_lines"):
            log_text = "\n".join(str(item) for item in remote_payload.get("latest_log_lines") or [])

    result_preview_columns: list[str] = []
    result_preview_rows: list[dict[str, Any]] = []
    artifact_files: list[str] = []
    artifact_file_items: list[ArtifactFileRead] = []
    manifest: dict[str, Any] | None = None
    service_outputs: dict[str, Any] | None = None
    resource_reports: dict[str, Any] | None = None

    if isinstance(remote_payload, dict):
        service_outputs = remote_payload.get("service_outputs") if isinstance(remote_payload.get("service_outputs"), dict) else None
        resource_reports = remote_payload.get("resource_reports") if isinstance(remote_payload.get("resource_reports"), dict) else None

    if output_path_host and output_path_host.exists():
        if task.task_type == "inference":
            preview_path = _resolve_inference_preview_path(output_path_host)
            if preview_path is not None:
                result_preview_columns, result_preview_rows = _read_csv_preview(preview_path)
        elif task.task_type == "training" and output_path_host.is_dir():
            manifest = _load_manifest(output_path_host)
            artifact_files = _list_artifact_files(output_path_host)
            artifact_file_items = _build_artifact_items(task, output_path_host)

    return RunTaskDetailRead(
        **base.model_dump(),
        dataset=dataset_to_schema(dataset) if dataset is not None else None,
        log_text=log_text,
        log_full_available=log_full_available,
        result_preview_columns=result_preview_columns,
        result_preview_rows=result_preview_rows,
        artifact_files=artifact_files,
        artifact_file_items=artifact_file_items,
        manifest=manifest,
        service_outputs=service_outputs,
        resource_reports=resource_reports,
    )
