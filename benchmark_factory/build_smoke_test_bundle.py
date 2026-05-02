from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

import pandas as pd

from adapter_core import (
    REQUIRED_DUALSYN_CELL_COLUMNS,
    REQUIRED_DRUG_COLUMNS,
    REQUIRED_MTL_CELL_COLUMNS,
    REQUIRED_MVC_CELL_COLUMNS,
    REQUIRED_SAMPLE_COLUMNS,
    build_manifest,
    build_protocol_assignments,
    export_dualsyn,
    export_mfsyndcp,
    export_mtlsynergy,
    export_mvcasyn,
    load_drugs,
    load_feature_table,
    load_samples,
    validate_bundle,
    write_csv,
    write_json,
)


REPO_ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = REPO_ROOT / "input_bundles" / "oneil_intersection_38drug_29cell"
EXAMPLE_BUNDLE_ROOT = REPO_ROOT / "example_bundle"
EXPORT_ROOT = REPO_ROOT / "exports"
SEED = 20260413
LABEL_THRESHOLD = 10.0
DEFAULT_RI = 0.0
FOLD_COUNT = 5

# These source samples were selected from the real O'Neil intersection bundle so
# that the smoke exports keep the original feature dimensions, avoid bondless
# toy molecules, and keep every fold non-empty with both classes present.
SMOKE_SOURCE_SAMPLE_IDS = [
    "oneil_14550",
    "oneil_07001",
    "oneil_07408",
    "oneil_07446",
    "oneil_01636",
    "oneil_14526",
    "oneil_01702",
    "oneil_06411",
    "oneil_01713",
    "oneil_14188",
    "oneil_01518",
    "oneil_01707",
    "oneil_01338",
    "oneil_11038",
    "oneil_11016",
    "oneil_07442",
    "oneil_14182",
    "oneil_10715",
    "oneil_07400",
    "oneil_14523",
]


def unordered_pair_key(row: pd.Series) -> str:
    return "|".join(sorted([str(row["drug_a_name"]), str(row["drug_b_name"])]))


def safe_rmtree(path: Path) -> None:
    resolved = path.resolve()
    repo_root = REPO_ROOT.resolve()
    if repo_root not in resolved.parents:
        raise ValueError(f"Refusing to delete outside benchmark_factory: {resolved}")
    if path.exists():
        shutil.rmtree(path)


def write_dataframe(path: Path, df: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")


def build_example_bundle() -> Path:
    samples = pd.read_csv(SOURCE_ROOT / "samples.csv")
    sample_subset = samples[samples["sample_id"].isin(SMOKE_SOURCE_SAMPLE_IDS)].copy()
    if len(sample_subset) != len(SMOKE_SOURCE_SAMPLE_IDS):
        missing = sorted(set(SMOKE_SOURCE_SAMPLE_IDS) - set(sample_subset["sample_id"]))
        raise ValueError(f"Missing source smoke samples: {missing}")

    source_order = {sample_id: index for index, sample_id in enumerate(SMOKE_SOURCE_SAMPLE_IDS)}
    sample_subset = sample_subset.sort_values(
        by="sample_id",
        key=lambda series: series.map(source_order),
    ).reset_index(drop=True)

    sample_subset.insert(1, "source_sample_id", sample_subset["sample_id"])
    sample_subset["sample_id"] = sample_subset.apply(unordered_pair_key, axis=1)
    if sample_subset["sample_id"].duplicated().any():
        duplicates = sample_subset.loc[sample_subset["sample_id"].duplicated(), "sample_id"].tolist()
        raise ValueError(f"Smoke sample_ids must stay unique unordered pairs: {duplicates}")

    used_drugs = set(sample_subset["drug_a_name"]) | set(sample_subset["drug_b_name"])
    used_cells = set(sample_subset["cell_line"])

    drugs = pd.read_csv(SOURCE_ROOT / "drugs.csv")
    dualsyn_cells = pd.read_csv(SOURCE_ROOT / "cells_dualsyn.csv")
    mtl_cells = pd.read_csv(SOURCE_ROOT / "cells_mtl.csv")
    mvc_exp_cells = pd.read_csv(SOURCE_ROOT / "cells_mvc_exp.csv")
    mvc_cn_cells = pd.read_csv(SOURCE_ROOT / "cells_mvc_cn.csv")

    drugs_subset = drugs[drugs["drug_name"].isin(used_drugs)].copy()
    dualsyn_subset = dualsyn_cells[dualsyn_cells["cell_line"].isin(used_cells)].copy()
    mtl_subset = mtl_cells[mtl_cells["cell_line"].isin(used_cells)].copy()
    mvc_exp_subset = mvc_exp_cells[mvc_exp_cells["cell_line"].isin(used_cells)].copy()
    mvc_cn_subset = mvc_cn_cells[mvc_cn_cells["cell_line"].isin(used_cells)].copy()

    write_dataframe(EXAMPLE_BUNDLE_ROOT / "samples.csv", sample_subset)
    write_dataframe(EXAMPLE_BUNDLE_ROOT / "drugs.csv", drugs_subset)
    write_dataframe(EXAMPLE_BUNDLE_ROOT / "cells_dualsyn.csv", dualsyn_subset)
    write_dataframe(EXAMPLE_BUNDLE_ROOT / "cells_mtl.csv", mtl_subset)
    write_dataframe(EXAMPLE_BUNDLE_ROOT / "cells_mvc_exp.csv", mvc_exp_subset)
    write_dataframe(EXAMPLE_BUNDLE_ROOT / "cells_mvc_cn.csv", mvc_cn_subset)

    bundle_manifest = {
        "dataset_name": "example_bundle",
        "description": "Real-dimension smoke-test bundle for all four projects.",
        "source_bundle": str(SOURCE_ROOT),
        "sample_count": int(len(sample_subset)),
        "drug_count": int(len(drugs_subset)),
        "cell_count": int(len(used_cells)),
        "feature_dimensions": {
            "drug_mtlsynergy": int(drugs_subset.shape[1] - len(REQUIRED_DRUG_COLUMNS) - 1),
            "cell_dualsyn": int(dualsyn_subset.shape[1] - len(REQUIRED_DUALSYN_CELL_COLUMNS)),
            "cell_mtlsynergy": int(mtl_subset.shape[1] - len(REQUIRED_MTL_CELL_COLUMNS)),
            "cell_mvc_exp": int(mvc_exp_subset.shape[1] - len(REQUIRED_MVC_CELL_COLUMNS)),
            "cell_mvc_cn": int(mvc_cn_subset.shape[1] - len(REQUIRED_MVC_CELL_COLUMNS)),
        },
        "source_sample_ids": SMOKE_SOURCE_SAMPLE_IDS,
        "notes": [
            "sample_id is normalized to the unordered drug pair so sample_group and pair_group smoke splits stay aligned",
            "only real source rows are used, so the smoke bundle keeps the original feature dimensions",
            "selected samples keep clear class separation for both benchmark threshold 10 and MTLSynergy threshold 30",
        ],
    }
    write_json(EXAMPLE_BUNDLE_ROOT / "bundle_manifest.json", bundle_manifest)
    return EXAMPLE_BUNDLE_ROOT


def export_dataset(bundle_root: Path, dataset_name: str, fold_strategy: str) -> None:
    output_dir = EXPORT_ROOT / dataset_name
    safe_rmtree(output_dir)

    samples = load_samples(
        bundle_root / "samples.csv",
        label_source="threshold",
        label_threshold=LABEL_THRESHOLD,
        default_ri=DEFAULT_RI,
    )
    drugs = load_drugs(bundle_root / "drugs.csv")
    dualsyn_cells = load_feature_table(bundle_root / "cells_dualsyn.csv", REQUIRED_DUALSYN_CELL_COLUMNS)
    mtl_cells = load_feature_table(bundle_root / "cells_mtl.csv", REQUIRED_MTL_CELL_COLUMNS)
    mvc_exp_cells = load_feature_table(bundle_root / "cells_mvc_exp.csv", REQUIRED_MVC_CELL_COLUMNS)
    mvc_cn_cells = load_feature_table(bundle_root / "cells_mvc_cn.csv", REQUIRED_MVC_CELL_COLUMNS)

    validate_bundle(samples, drugs, dualsyn_cells, mtl_cells, mvc_exp_cells, mvc_cn_cells)
    assignments = build_protocol_assignments(samples, FOLD_COUNT, SEED, fold_strategy)

    export_dualsyn(dataset_name, EXPORT_ROOT, assignments, drugs, dualsyn_cells, FOLD_COUNT)
    export_mfsyndcp(dataset_name, EXPORT_ROOT, assignments, drugs, dualsyn_cells, FOLD_COUNT)
    export_mvcasyn(dataset_name, EXPORT_ROOT, assignments, drugs, mvc_exp_cells, mvc_cn_cells, FOLD_COUNT)
    export_mtlsynergy(dataset_name, EXPORT_ROOT, assignments, drugs, mtl_cells)

    protocol_root = EXPORT_ROOT / dataset_name / "protocol"
    write_csv(
        protocol_root / "fold_assignments.csv",
        [
            "sample_id",
            "drug_a_name",
            "drug_b_name",
            "cell_line",
            "synergy_score",
            "label",
            "ri_row",
            "ri_col",
            "transductive_group",
            "transductive_fold",
            "cell_fold",
            "drug_a_fold",
            "drug_b_fold",
        ],
        assignments,
    )
    manifest = build_manifest(
        dataset_name=dataset_name,
        assignments=assignments,
        drugs=drugs,
        dualsyn_cells=dualsyn_cells,
        mtl_cells=mtl_cells,
        mvc_exp_cells=mvc_exp_cells,
        mvc_cn_cells=mvc_cn_cells,
        fold_count=FOLD_COUNT,
        label_source="threshold",
        label_threshold=LABEL_THRESHOLD,
        default_ri=DEFAULT_RI,
        seed=SEED,
        fold_strategy=fold_strategy,
    )
    write_json(protocol_root / "manifest.json", manifest)


def main() -> None:
    bundle_root = build_example_bundle()
    export_dataset(bundle_root, "smoke_test", "sample_group")
    export_dataset(bundle_root, "smoke_test_pair_group", "pair_group")

    summary = {
        "example_bundle": str(bundle_root),
        "exports": {
            "smoke_test": str(EXPORT_ROOT / "smoke_test"),
            "smoke_test_pair_group": str(EXPORT_ROOT / "smoke_test_pair_group"),
        },
        "sample_count": len(SMOKE_SOURCE_SAMPLE_IDS),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
