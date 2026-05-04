from __future__ import annotations

from fastapi import APIRouter

from ..schemas.entities import ModelVersionRead
from ..services.legacy_support import list_model_versions
from ..services.serializers import model_version_to_schema


router = APIRouter(prefix="/api/model-versions", tags=["model-versions"])


@router.get("", response_model=list[ModelVersionRead])
def get_model_versions() -> list[ModelVersionRead]:
    payload = list_model_versions()
    return [model_version_to_schema(item) for item in payload]
