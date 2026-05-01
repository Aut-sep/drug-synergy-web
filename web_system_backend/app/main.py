from __future__ import annotations

import logging
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .core.config import get_settings
from .db import Base, SessionLocal, engine
from .routers import datasets, inference, system, training, versions
from .services.legacy_support import migrate_legacy_storage_paths, seed_builtin_bundles


settings = get_settings()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Synergy Web System Backend",
    description="Standalone web backend for datasets, tasks, inference orchestration, and training orchestration.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(system.router)
app.include_router(datasets.router)
app.include_router(inference.router)
app.include_router(training.router)
app.include_router(versions.router)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        try:
            migrate_legacy_storage_paths(db)
        except Exception:  # noqa: BLE001
            logger.exception("Failed to migrate legacy runtime paths during startup.")
        try:
            seed_builtin_bundles(db)
        except Exception:  # noqa: BLE001
            logger.exception("Failed to seed built-in dataset bundles during startup.")

    # Serve frontend static files if dist directory exists (production mode)
    frontend_dist = (settings.repo_root / "web_system_frontend" / "dist").resolve()
    if frontend_dist.exists() and (frontend_dist / "index.html").exists():
        app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")
        app.mount("/favicon.svg", StaticFiles(directory=frontend_dist, html=True), name="static")

        @app.get("/{full_path:path}")
        async def serve_frontend(full_path: str):
            """Serve frontend SPA - catch-all route for production mode."""
            file_path = frontend_dist / full_path
            if file_path.exists() and file_path.is_file():
                return FileResponse(file_path)
            return FileResponse(frontend_dist / "index.html")

        logger.info("Frontend static files mounted from %s", frontend_dist)


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "service": "web_system_backend",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True,
    )
