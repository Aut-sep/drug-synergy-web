from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    backend_root: Path
    repo_root: Path
    runtime_root: Path
    workspace_root: Path
    uploads_root: Path
    data_root: Path
    outputs_root: Path
    downloads_root: Path
    trained_model_root: Path
    training_bundles_root: Path
    database_url: str
    legacy_gateway_url: str
    legacy_training_url: str
    legacy_gateway_runtime_root: str
    cors_origins: list[str]
    backend_host: str = "0.0.0.0"
    backend_port: int = 9000


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    backend_root = Path(__file__).resolve().parents[2]

    default_repo = backend_root.parent
    repo_root = Path(os.environ.get("WEB_SYSTEM_REPO_ROOT", str(default_repo))).resolve()

    default_runtime = repo_root / "web_system_runtime"
    runtime_root = Path(os.environ.get("WEB_SYSTEM_RUNTIME_ROOT", str(default_runtime))).resolve()

    workspace_root = Path(os.environ.get("WEB_SYSTEM_WORKSPACE_ROOT", str(repo_root))).resolve()

    uploads_root = runtime_root / "user_bundles" / "web_system_uploads"
    data_root = backend_root / "data"
    outputs_root = runtime_root / "outputs" / "web_system_bridge"
    downloads_root = backend_root / "outputs" / "downloads"
    trained_model_root = runtime_root / "trained_model_versions"
    training_bundles_root = runtime_root / "training_bundles"

    uploads_root.mkdir(parents=True, exist_ok=True)
    data_root.mkdir(parents=True, exist_ok=True)
    outputs_root.mkdir(parents=True, exist_ok=True)
    downloads_root.mkdir(parents=True, exist_ok=True)
    trained_model_root.mkdir(parents=True, exist_ok=True)
    training_bundles_root.mkdir(parents=True, exist_ok=True)

    default_db = data_root / "web_system.db"

    gateway_runtime_root = os.environ.get(
        "WEB_SYSTEM_GATEWAY_RUNTIME_ROOT",
        "/workspace/web_system_runtime",
    ).strip()

    cors_raw = os.environ.get("WEB_SYSTEM_CORS_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173")
    cors_origins = [origin.strip() for origin in cors_raw.split(",") if origin.strip()]

    return Settings(
        backend_root=backend_root,
        repo_root=repo_root,
        runtime_root=runtime_root,
        workspace_root=workspace_root,
        uploads_root=uploads_root,
        data_root=data_root,
        outputs_root=outputs_root,
        downloads_root=downloads_root,
        trained_model_root=trained_model_root,
        training_bundles_root=training_bundles_root,
        database_url=os.environ.get("WEB_SYSTEM_DATABASE_URL", f"sqlite:///{default_db.as_posix()}"),
        legacy_gateway_url=os.environ.get("WEB_SYSTEM_GATEWAY_URL", "http://127.0.0.1:8000").strip(),
        legacy_training_url=os.environ.get("WEB_SYSTEM_TRAINING_URL", "http://127.0.0.1:8011").strip(),
        legacy_gateway_runtime_root=gateway_runtime_root,
        cors_origins=cors_origins,
        backend_host=os.environ.get("WEB_SYSTEM_BACKEND_HOST", "0.0.0.0"),
        backend_port=int(os.environ.get("WEB_SYSTEM_BACKEND_PORT", "9000")),
    )


def to_storage_path(absolute_path: str | Path) -> str:
    """Convert an absolute filesystem path to a relative storage path.

    Paths under repo_root are stored relative to repo_root.
    Paths outside repo_root are stored as-is.
    """
    settings = get_settings()
    try:
        rel = Path(absolute_path).resolve().relative_to(settings.repo_root)
        return rel.as_posix()
    except ValueError:
        return str(absolute_path)


def from_storage_path(stored: str | None) -> Path | None:
    """Convert a stored relative path back to an absolute filesystem path.

    Relative paths are resolved against the current repo_root.
    Absolute paths are returned as-is.
    """
    if not stored:
        return None
    path = Path(stored)
    if path.is_absolute():
        return path
    return (get_settings().repo_root / path).resolve()
