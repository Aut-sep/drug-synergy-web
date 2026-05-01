from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
import os
from pathlib import Path
from typing import Iterable

import pandas as pd


ALL_MODELS = ["DualSyn", "MFSynDCP", "MVCASyn", "MTLSynergy"]
SAMPLE_REQUIRED_COLUMNS = {"sample_id", "drug_a_name", "drug_b_name", "cell_line"}
RUNTIME_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORKSPACE_ROOT = Path(os.environ.get("SYNERGY_WORKSPACE_ROOT", RUNTIME_ROOT.parent)).resolve()
DEFAULT_INTERSECTION_NAME = "oneil_intersection_38drug_29cell"


@dataclass
class SampleValidationResult:
    valid: bool
    detail: str
    sample_count: int = 0
    sample_columns: list[str] = field(default_factory=list)
    supported_drug_count: int = 0
    supported_cell_count: int = 0


@dataclass(frozen=True)
class ModelSupport:
    drugs: frozenset[str]
    cells: frozenset[str]


def clean_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def clean_values(values: Iterable[object]) -> set[str]:
    return {clean_text(value) for value in values if clean_text(value)}


def read_csv_safe(csv_path: Path) -> tuple[pd.DataFrame | None, str]:
    try:
        return pd.read_csv(csv_path), ""
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)


def _choose_column(columns: list[str], candidates: list[str]) -> str | None:
    lowered = {column.lower(): column for column in columns}
    for candidate in candidates:
        if candidate in lowered:
            return lowered[candidate]
    return None


def _csv_column_values(csv_path: Path, column_names: list[str]) -> set[str]:
    df = pd.read_csv(csv_path)
    column_name = _choose_column(list(df.columns), column_names)
    if not column_name:
        raise ValueError(f"{csv_path} 缺少列：{column_names}")
    return clean_values(df[column_name])


def _first_column_values(csv_path: Path, excluded_values: set[str]) -> set[str]:
    df = pd.read_csv(csv_path, usecols=[0])
    column_name = df.columns[0]
    return {value for value in clean_values(df[column_name]) if value not in excluded_values}


def _drugs_with_aliases(drugs_csv: Path) -> set[str]:
    df = pd.read_csv(drugs_csv)
    name_col = _choose_column(list(df.columns), ["drug_name", "name", "compound_name"])
    synonyms_col = _choose_column(list(df.columns), ["synonyms", "aliases"])
    if not name_col:
        raise ValueError(f"{drugs_csv} 缺少药物名称列")

    names = clean_values(df[name_col])
    if synonyms_col:
        for raw_synonyms in df[synonyms_col].dropna():
            for alias in str(raw_synonyms).split(";"):
                alias_text = alias.strip()
                if alias_text:
                    names.add(alias_text)
    return names


def default_intersection_bundle_dir(workspace_root: Path | None = None, samples_csv: Path | None = None) -> Path | None:
    candidates: list[Path] = []
    if samples_csv is not None:
        candidates.append(samples_csv.resolve().parent)
    root = (workspace_root or DEFAULT_WORKSPACE_ROOT).resolve()
    candidates.append(root / "benchmark_factory" / "input_bundles" / DEFAULT_INTERSECTION_NAME)
    for candidate in candidates:
        if (candidate / "samples.csv").exists() and (candidate / "drugs.csv").exists():
            return candidate
    return None


@lru_cache(maxsize=8)
def official_intersection_entities(workspace_root_key: str) -> tuple[set[str], set[str]]:
    bundle_dir = default_intersection_bundle_dir(Path(workspace_root_key))
    if bundle_dir is None:
        return set(), set()
    samples_df = pd.read_csv(bundle_dir / "samples.csv")
    drugs = clean_values(pd.concat([samples_df["drug_a_name"], samples_df["drug_b_name"]]))
    cells = clean_values(samples_df["cell_line"])
    return drugs, cells


@lru_cache(maxsize=8)
def model_entity_support(workspace_root_key: str) -> dict[str, ModelSupport]:
    workspace_root = Path(workspace_root_key)
    official_bundle = default_intersection_bundle_dir(workspace_root)

    dualsyn_drugs = _csv_column_values(workspace_root / "DualSyn/DualSyn/data/smiles.csv", ["name", "drug_name"])
    dualsyn_cells = _first_column_values(
        workspace_root / "DualSyn/DualSyn/data/cell_features_954.csv",
        {"gene_id", "transcript_id"},
    )
    if official_bundle is not None:
        dualsyn_drugs.update(_drugs_with_aliases(official_bundle / "drugs.csv"))
        dualsyn_cells = _first_column_values(official_bundle / "cells_dualsyn.csv", {"gene_id", "transcript_id"})

    mfsyndcp_drugs = _csv_column_values(workspace_root / "MFSynDCP/MFSynDCP/data/smiles.csv", ["name", "drug_name"])
    if official_bundle is not None:
        mfsyndcp_drugs.update(_drugs_with_aliases(official_bundle / "drugs.csv"))
    mfsyndcp_cells = _first_column_values(
        workspace_root / "MFSynDCP/MFSynDCP/data/cell_features.csv",
        {"gene_id", "transcript_id"},
    )

    mvc_drugs = _csv_column_values(workspace_root / "MVCASyn/data/oneil_drug_two_smiles.csv", ["drug_name", "name"])
    mvc_exp_cells = _first_column_values(workspace_root / "MVCASyn/data/exp.csv", {"cell_line_name"})
    mvc_cn_cells = _first_column_values(workspace_root / "MVCASyn/data/cn.csv", {"cell_line_name"})

    mtl_drugs = _csv_column_values(workspace_root / "MTLSynergy/data/drugs.csv", ["name", "drug_name"])
    mtl_cells = _csv_column_values(workspace_root / "MTLSynergy/data/cell_lines.csv", ["name", "cell_line_name", "cell_line"])

    return {
        "DualSyn": ModelSupport(frozenset(dualsyn_drugs), frozenset(dualsyn_cells)),
        "MFSynDCP": ModelSupport(frozenset(mfsyndcp_drugs), frozenset(mfsyndcp_cells)),
        "MVCASyn": ModelSupport(frozenset(mvc_drugs), frozenset(mvc_exp_cells.intersection(mvc_cn_cells))),
        "MTLSynergy": ModelSupport(frozenset(mtl_drugs), frozenset(mtl_cells)),
    }


def effective_model_entity_support(workspace_root: Path, samples_csv: Path) -> dict[str, ModelSupport]:
    supports = dict(model_entity_support(str(workspace_root.resolve())))
    bundle_dir = default_intersection_bundle_dir(workspace_root, samples_csv)
    samples_dir = samples_csv.resolve().parent
    supplemental_drugs_csv = samples_dir / "drugs.csv"
    dualsyn_cells_csv = samples_dir / "cells_dualsyn.csv"

    if not supplemental_drugs_csv.exists() and bundle_dir is not None:
        supplemental_drugs_csv = bundle_dir / "drugs.csv"
    if supplemental_drugs_csv.exists():
        supplemental_drugs = _drugs_with_aliases(supplemental_drugs_csv)
        for model_name in ("DualSyn", "MFSynDCP"):
            support = supports[model_name]
            supports[model_name] = ModelSupport(frozenset(set(support.drugs).union(supplemental_drugs)), support.cells)

    if not dualsyn_cells_csv.exists() and bundle_dir is not None:
        dualsyn_cells_csv = bundle_dir / "cells_dualsyn.csv"
    if dualsyn_cells_csv.exists():
        support = supports["DualSyn"]
        supports["DualSyn"] = ModelSupport(
            support.drugs,
            frozenset(_first_column_values(dualsyn_cells_csv, {"gene_id", "transcript_id"})),
        )

    return supports


def _model_scope_counts(workspace_root: Path) -> tuple[int, int]:
    official_drugs, official_cells = official_intersection_entities(str(workspace_root.resolve()))
    if official_drugs and official_cells:
        return len(official_drugs), len(official_cells)

    supports = model_entity_support(str(workspace_root.resolve()))
    common_drugs = set.intersection(*(set(support.drugs) for support in supports.values()))
    common_cells = set.intersection(*(set(support.cells) for support in supports.values()))
    return len(common_drugs), len(common_cells)


def validate_samples_csv(
    csv_path: Path,
    *,
    workspace_root: Path | None = None,
    selected_models: list[str] | None = None,
) -> SampleValidationResult:
    model_names = selected_models or ALL_MODELS
    root = (workspace_root or DEFAULT_WORKSPACE_ROOT).resolve()

    df, error = read_csv_safe(csv_path)
    if error:
        return SampleValidationResult(False, f"无法读取该文件：{error}")
    if df is None or df.empty:
        return SampleValidationResult(False, "文件已上传，但样本表中没有数据。")

    sample_columns = list(df.columns)
    missing_columns = sorted(SAMPLE_REQUIRED_COLUMNS.difference(df.columns))
    if missing_columns:
        return SampleValidationResult(False, "缺少必需列：" + "、".join(missing_columns), len(df), sample_columns)

    required_df = df[list(SAMPLE_REQUIRED_COLUMNS)].apply(lambda column: column.map(clean_text))
    empty_columns = sorted(column for column in SAMPLE_REQUIRED_COLUMNS if (required_df[column] == "").any())
    if empty_columns:
        return SampleValidationResult(False, "以下列存在空值：" + "、".join(empty_columns), len(df), sample_columns)

    duplicated_ids = sorted(required_df.loc[required_df["sample_id"].duplicated(), "sample_id"].unique())
    if duplicated_ids:
        return SampleValidationResult(
            False,
            f"sample_id 存在重复：{duplicated_ids[:10]}",
            len(df),
            sample_columns,
        )

    try:
        supports = effective_model_entity_support(root, csv_path)
        scope_drug_count, scope_cell_count = _model_scope_counts(root)
    except Exception as exc:  # noqa: BLE001
        return SampleValidationResult(False, f"无法读取内置模型资产：{exc}", len(df), sample_columns)

    unknown_models = [model_name for model_name in model_names if model_name not in supports]
    if unknown_models:
        return SampleValidationResult(False, f"未知模型：{unknown_models}", len(df), sample_columns)

    sample_drugs = clean_values(pd.concat([required_df["drug_a_name"], required_df["drug_b_name"]]))
    sample_cells = clean_values(required_df["cell_line"])
    problems: list[str] = []
    for model_name in model_names:
        support = supports[model_name]
        missing_drugs = sorted(sample_drugs.difference(support.drugs))
        missing_cells = sorted(sample_cells.difference(support.cells))
        if missing_drugs:
            problems.append(f"{model_name} 不支持药物：{missing_drugs[:10]}")
        if missing_cells:
            problems.append(f"{model_name} 不支持细胞系：{missing_cells[:10]}")

    if problems:
        problems.append(f"当前展示系统正式支持 {scope_drug_count} 个药物、{scope_cell_count} 个细胞系。")
        return SampleValidationResult(False, "；".join(problems), len(df), sample_columns, scope_drug_count, scope_cell_count)

    return SampleValidationResult(
        True,
        f"推理前检查通过：当前展示系统正式支持 {scope_drug_count} 个药物、{scope_cell_count} 个细胞系，本样本表均在支持范围内。",
        len(df),
        sample_columns,
        scope_drug_count,
        scope_cell_count,
    )


def validate_model_output(
    model_df: pd.DataFrame,
    samples_df: pd.DataFrame,
    *,
    model_name: str,
) -> tuple[bool, str]:
    required_columns = {"sample_id", f"{model_name}_score", f"{model_name}_label"}
    missing_columns = sorted(required_columns.difference(model_df.columns))
    if missing_columns:
        return False, f"{model_name} 输出缺少列：{missing_columns}"

    expected_ids = set(samples_df["sample_id"].map(clean_text))
    output_ids = set(model_df["sample_id"].map(clean_text))
    missing_ids = sorted(expected_ids.difference(output_ids))
    extra_ids = sorted(output_ids.difference(expected_ids))
    if missing_ids:
        return False, f"{model_name} 输出缺少样本：{missing_ids[:10]}"
    if extra_ids:
        return False, f"{model_name} 输出包含未知样本：{extra_ids[:10]}"
    if len(model_df) != len(samples_df):
        return False, f"{model_name} 输出行数 {len(model_df)} 与输入样本数 {len(samples_df)} 不一致。"
    return True, ""
