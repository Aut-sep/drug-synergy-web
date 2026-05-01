from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List

import pandas as pd

from shared.sample_validation import (
    ALL_MODELS,
    SAMPLE_REQUIRED_COLUMNS,
    read_csv_safe,
    validate_samples_csv,
)


SAMPLE_REQUIREMENT = {
    "key": "samples",
    "label": "待预测样本表",
    "purpose": "告诉系统要在哪个细胞系上预测哪一对药物。",
    "minimum": "必须填写药物名称，不需要填写 SMILES。列名为 sample_id、drug_a_name、drug_b_name、cell_line。",
    "system_check": "系统会检查样本表能否读取、4 个必需列是否存在、sample_id 是否唯一，以及药物和细胞系是否能被当前所选模型识别。",
}

RUNTIME_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_ROOT = Path(os.environ.get("SYNERGY_WORKSPACE_ROOT", RUNTIME_ROOT.parent)).resolve()


def _read_csv_safe(csv_path: Path) -> tuple[pd.DataFrame | None, str]:
    return read_csv_safe(csv_path)


def available_sample_files(bundle_path: Path) -> List[str]:
    if not bundle_path.exists():
        return []
    csv_files = sorted(path.name for path in bundle_path.glob("*.csv"))
    preferred = [name for name in csv_files if name.startswith("samples")]
    if preferred:
        return preferred

    valid_files: List[str] = []
    for name in csv_files:
        sample_df, _ = _read_csv_safe(bundle_path / name)
        if sample_df is None:
            continue
        if all(column in sample_df.columns for column in SAMPLE_REQUIRED_COLUMNS):
            valid_files.append(name)
    return valid_files


def bundle_file_status(bundle_path: Path) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for sample_name in available_sample_files(bundle_path):
        sample_path = bundle_path / sample_name
        rows.append(
            {
                "requirement_key": SAMPLE_REQUIREMENT["key"],
                "label": SAMPLE_REQUIREMENT["label"],
                "file_name": sample_name,
                "exists": sample_path.exists(),
                "path": str(sample_path),
            }
        )
    return rows


def bundle_requirement_status(
    bundle_path: Path,
    model_root: Path | None = None,
    sample_file_name: str | None = None,
    selected_models: list[str] | None = None,
) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    sample_files = available_sample_files(bundle_path)
    sample_exists = bool(sample_files)
    sample_valid = False
    validation_detail = "还未提供样本表。"
    sample_source = ", ".join(sample_files) if sample_files else "samples*.csv"
    selected_sample = sample_file_name if sample_file_name in sample_files else (sample_files[0] if sample_files else None)
    sample_source = selected_sample or "samples*.csv"
    sample_path = str(bundle_path / selected_sample) if selected_sample else ""
    if selected_sample:
        validation = validate_samples_csv(
            bundle_path / selected_sample,
            workspace_root=model_root or DEFAULT_MODEL_ROOT,
            selected_models=selected_models or ALL_MODELS,
        )
        sample_valid = validation.valid
        validation_detail = validation.detail
    rows.append(
        {
            "requirement_key": SAMPLE_REQUIREMENT["key"],
            "label": SAMPLE_REQUIREMENT["label"],
            "purpose": SAMPLE_REQUIREMENT["purpose"],
            "minimum": SAMPLE_REQUIREMENT["minimum"],
            "system_check": SAMPLE_REQUIREMENT["system_check"],
            "exists": sample_exists,
            "valid": sample_valid,
            "validation_detail": validation_detail,
            "status_label": "推理前检查通过" if sample_valid else ("已上传，待修正" if sample_exists else "未提供"),
            "path": sample_path,
            "source_file": sample_source,
        }
    )
    return rows


def inspect_bundle(
    bundle_path: Path,
    model_root: Path | None = None,
    sample_file_name: str | None = None,
    selected_models: list[str] | None = None,
) -> Dict[str, object]:
    sample_files = available_sample_files(bundle_path)
    status_rows = bundle_file_status(bundle_path)
    selected_sample = sample_file_name if sample_file_name in sample_files else (sample_files[0] if sample_files else None)
    requirement_rows = bundle_requirement_status(bundle_path, model_root, selected_sample, selected_models)
    missing_files: List[str] = []
    missing_requirements = [
        f"{row['label']}：{row['validation_detail']}" for row in requirement_rows if not row["valid"]
    ]
    sample_count = 0
    sample_columns: List[str] = []
    if selected_sample:
        sample_df, _ = _read_csv_safe(bundle_path / selected_sample)
        if sample_df is not None:
            sample_count = len(sample_df)
            sample_columns = list(sample_df.columns)
    return {
        "bundle_exists": bundle_path.exists(),
        "status_rows": status_rows,
        "requirement_rows": requirement_rows,
        "missing_files": missing_files,
        "missing_requirements": missing_requirements,
        "sample_files": sample_files,
        "default_sample_file": selected_sample,
        "sample_count": sample_count,
        "sample_columns": sample_columns,
        "bundle_ready": bundle_path.exists() and all(bool(row["valid"]) for row in requirement_rows),
    }


def load_samples(bundle_path: Path, sample_file_name: str) -> pd.DataFrame:
    return pd.read_csv(bundle_path / sample_file_name)


def discover_bundle_paths(*roots: Path) -> List[Path]:
    discovered: List[Path] = []
    seen = set()
    for root in roots:
        if not root.exists():
            continue
        pattern = "*.csv" if root.name == "user_bundles" else "samples*.csv"
        for sample_path in sorted(root.rglob(pattern)):
            resolved = sample_path.parent.resolve()
            if resolved not in seen:
                discovered.append(resolved)
                seen.add(resolved)
    return discovered


def summarize_samples(samples_df: pd.DataFrame) -> Dict[str, object]:
    has_synergy_column = "synergy_score" in samples_df.columns
    if has_synergy_column:
        synergy_series = pd.to_numeric(samples_df["synergy_score"], errors="coerce")
        all_missing = bool(synergy_series.isna().all())
    else:
        all_missing = True

    drug_a_column = "drug_a_name" if "drug_a_name" in samples_df.columns else None
    drug_b_column = "drug_b_name" if "drug_b_name" in samples_df.columns else None
    if drug_a_column is None and "drug1" in samples_df.columns:
        drug_a_column = "drug1"
    if drug_b_column is None and "drug2" in samples_df.columns:
        drug_b_column = "drug2"

    if drug_a_column and drug_b_column:
        drug_pair_count = len(
            {
                tuple(sorted((str(row[drug_a_column]), str(row[drug_b_column]))))
                for _, row in samples_df[[drug_a_column, drug_b_column]].iterrows()
            }
        )
    else:
        drug_pair_count = 0

    cell_line_column = "cell_line" if "cell_line" in samples_df.columns else ("cell" if "cell" in samples_df.columns else None)
    return {
        "sample_count": len(samples_df),
        "column_count": len(samples_df.columns),
        "all_synergy_missing": all_missing,
        "drug_pair_count": drug_pair_count,
        "cell_line_count": int(samples_df[cell_line_column].nunique()) if cell_line_column else 0,
    }
