from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base


class DatasetBundle(Base):
    __tablename__ = "dataset_bundles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    bundle_path: Mapped[str] = mapped_column(String(600), unique=True)
    sample_file: Mapped[str] = mapped_column(String(255), default="")
    source_type: Mapped[str] = mapped_column(String(60), default="upload")
    description: Mapped[str] = mapped_column(Text, default="")
    is_ready: Mapped[bool] = mapped_column(Boolean, default=False)
    sample_count: Mapped[int] = mapped_column(Integer, default=0)
    files: Mapped[list[str]] = mapped_column(JSON, default=list)
    validation_detail: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    tasks: Mapped[list["RunTask"]] = relationship(back_populates="dataset")


class RunTask(Base):
    __tablename__ = "run_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task_type: Mapped[str] = mapped_column(String(30), index=True)
    title: Mapped[str] = mapped_column(String(200))
    local_status: Mapped[str] = mapped_column(String(30), default="waiting")
    remote_state: Mapped[str] = mapped_column(String(30), default="")
    remote_run_id: Mapped[str] = mapped_column(String(120), default="")
    dataset_id: Mapped[int | None] = mapped_column(ForeignKey("dataset_bundles.id"), nullable=True)
    model_version_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    selected_models: Mapped[list[str]] = mapped_column(JSON, default=list)
    output_path: Mapped[str | None] = mapped_column(String(600), nullable=True)
    log_excerpt: Mapped[str] = mapped_column(Text, default="")
    error_message: Mapped[str] = mapped_column(Text, default="")
    summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    dataset: Mapped[DatasetBundle | None] = relationship(back_populates="tasks")
