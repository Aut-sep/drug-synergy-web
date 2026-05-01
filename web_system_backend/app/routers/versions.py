from __future__ import annotations

from fastapi import APIRouter

from ..schemas.entities import ModelVersionRead
from ..services.legacy_support import list_model_versions
from ..services.serializers import coerce_string_list


router = APIRouter(prefix="/api/model-versions", tags=["model-versions"])


@router.get("", response_model=list[ModelVersionRead])
def get_model_versions() -> list[ModelVersionRead]:
    payload = list_model_versions()
    return [
        ModelVersionRead(
            version_id=str(item.get("version_id") or ""),
            created_at=str(item.get("created_at") or ""),
            selected_models=coerce_string_list(item.get("selected_models")),
            profile=str(item.get("profile") or ""),
            version_note=str(item.get("version_note") or ""),
            version_dir=str(item.get("version_dir") or ""),
            source_kind=str(item.get("source_kind") or ""),
            availability_note=str(item.get("availability_note") or ""),
        )
        for item in payload
    ]
