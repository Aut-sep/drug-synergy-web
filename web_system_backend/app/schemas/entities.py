from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DatasetBundleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    bundle_path: str
    sample_file: str
    source_type: str
    description: str
    is_ready: bool
    sample_count: int
    files: list[str]
    validation_detail: str
    bundle_kind: str = "invalid"
    supports_inference: bool = False
    supports_training: bool = False
    created_at: str
    updated_at: str


class DatasetPreviewRead(BaseModel):
    dataset_id: int
    sample_file: str
    columns: list[str] = Field(default_factory=list)
    preview_rows: list[dict[str, Any]] = Field(default_factory=list)
    preview_row_count: int = 0
    note: str = ""


class RunTaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_type: str
    title: str
    local_status: str
    remote_state: str
    remote_run_id: str
    dataset_id: int | None
    model_version_id: str | None
    model_version_ids: dict[str, str] = Field(default_factory=dict)
    version_group_id: str | None = None
    version_group_name: str | None = None
    selected_models: list[str]
    output_path: str | None
    output_path_host: str | None = None
    output_available: bool = False
    result_download_endpoint: str | None = None
    artifacts_download_endpoint: str | None = None
    log_excerpt: str
    error_message: str
    summary: dict[str, Any] | None = None
    detail_endpoint: str | None = None
    created_at: str
    updated_at: str


class ArtifactFileRead(BaseModel):
    path: str
    size_bytes: int
    download_endpoint: str


class RunTaskDetailRead(RunTaskRead):
    dataset: DatasetBundleRead | None = None
    log_text: str = ""
    log_full_available: bool = False
    result_preview_columns: list[str] = Field(default_factory=list)
    result_preview_rows: list[dict[str, Any]] = Field(default_factory=list)
    artifact_files: list[str] = Field(default_factory=list)
    artifact_file_items: list[ArtifactFileRead] = Field(default_factory=list)
    manifest: dict[str, Any] | None = None
    service_outputs: dict[str, Any] | None = None
    resource_reports: dict[str, Any] | None = None


class InferenceRunCreate(BaseModel):
    dataset_id: int
    selected_models: list[str] = Field(min_length=1)
    model_version_id: str = "__default__"
    model_version_ids: dict[str, str] = Field(default_factory=dict)


class TrainingRunCreate(BaseModel):
    dataset_id: int
    selected_models: list[str] = Field(min_length=1)
    profile: str = "quick"
    device: str = "auto"
    epochs: int | None = None
    label_threshold: float = 10.0
    version_group_name: str = ""
    version_note: str = ""


class ModelVersionRead(BaseModel):
    version_id: str
    base_version_id: str | None = None
    group_id: str | None = None
    group_name: str | None = None
    version_group_name: str | None = None
    model_name: str | None = None
    created_at: str | None = None
    selected_models: list[str] | None = None
    profile: str | None = None
    version_note: str | None = None
    version_dir: str | None = None
    artifact_root: str | None = None
    is_virtual_child: bool = False
    source_kind: str | None = None
    availability_note: str | None = None
