from __future__ import annotations

import csv
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..core.config import from_storage_path
from ..db import get_db
from ..models import DatasetBundle
from ..schemas.entities import DatasetBundleRead, DatasetPreviewRead
from ..services.legacy_support import persist_uploaded_bundle, upsert_dataset_bundle
from ..services.serializers import dataset_to_schema


router = APIRouter(prefix="/api/datasets", tags=["datasets"])


def _read_dataset_preview(sample_path: Path, *, limit: int = 12) -> tuple[list[str], list[dict[str, str]]]:
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            with sample_path.open("r", encoding=encoding, newline="") as handle:
                reader = csv.DictReader(handle)
                columns = list(reader.fieldnames or [])
                rows: list[dict[str, str]] = []
                for index, row in enumerate(reader):
                    rows.append({column: str(row.get(column, "")) for column in columns})
                    if index + 1 >= limit:
                        break
            return columns, rows
        except UnicodeDecodeError:
            continue

    raise HTTPException(status_code=400, detail=f"无法解析样本文件：{sample_path.name}")


@router.get("", response_model=list[DatasetBundleRead])
def list_datasets(db: Session = Depends(get_db)) -> list[DatasetBundleRead]:
    records = db.query(DatasetBundle).order_by(DatasetBundle.updated_at.desc(), DatasetBundle.id.desc()).all()
    return [dataset_to_schema(record) for record in records]


@router.get("/{dataset_id}", response_model=DatasetBundleRead)
def get_dataset(dataset_id: int, db: Session = Depends(get_db)) -> DatasetBundleRead:
    record = db.get(DatasetBundle, dataset_id)
    if record is None:
        raise HTTPException(status_code=404, detail="数据集不存在。")
    return dataset_to_schema(record)


@router.get("/{dataset_id}/preview", response_model=DatasetPreviewRead)
def get_dataset_preview(dataset_id: int, db: Session = Depends(get_db)) -> DatasetPreviewRead:
    record = db.get(DatasetBundle, dataset_id)
    if record is None:
        raise HTTPException(status_code=404, detail="数据集不存在。")
    if not record.sample_file:
        raise HTTPException(status_code=400, detail="当前数据集没有可预览的样本文件。")

    bundle_dir = from_storage_path(record.bundle_path)
    if bundle_dir is None:
        raise HTTPException(status_code=404, detail="数据集路径无效。")
    sample_path = bundle_dir / record.sample_file
    if not sample_path.exists():
        raise HTTPException(status_code=404, detail=f"样本文件不存在：{sample_path}")

    columns, rows = _read_dataset_preview(sample_path)
    return DatasetPreviewRead(
        dataset_id=record.id,
        sample_file=record.sample_file,
        columns=columns,
        preview_rows=rows,
        preview_row_count=len(rows),
        note=f"已显示前 {len(rows)} 行样本，用于快速核查字段结构和内容格式。",
    )


@router.post("/upload", response_model=DatasetBundleRead)
def upload_dataset(
    name: str = Form(...),
    description: str = Form(""),
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
) -> DatasetBundleRead:
    clean_name = name.strip()
    if not clean_name:
        raise HTTPException(status_code=400, detail="数据集名称不能为空。")
    if not files:
        raise HTTPException(status_code=400, detail="请至少上传一个文件。")

    try:
        bundle_path, _metadata = persist_uploaded_bundle(name=clean_name, description=description, file_items=files)
        record = upsert_dataset_bundle(
            db,
            name=clean_name,
            bundle_path=bundle_path,
            description=description,
            source_type="upload",
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"上传数据集失败：{exc}") from exc
    return dataset_to_schema(record)
