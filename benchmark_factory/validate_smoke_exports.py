from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parent
EXPORT_ROOT = REPO_ROOT / "exports"
EXAMPLE_BUNDLE_ROOT = REPO_ROOT / "example_bundle"

EXPECTED_SAMPLE_COUNT = 20
EXPECTED_FOLD_COUNT = 5
EXPECTED_TEST_ROWS = 4
EXPECTED_TRAIN_ROWS = 16
EXPECTED_DIMS = {
    "drug_mtlsynergy": 1213,
    "cell_dualsyn": 954,
    "cell_mtlsynergy": 5000,
    "cell_mvc_exp": 4004,
    "cell_mvc_cn": 3895,
}


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_manifest(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv_width(path: Path) -> tuple[int, int]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    return len(rows), len(rows[0]) if rows else 0


def validate_example_bundle() -> None:
    samples = pd.read_csv(EXAMPLE_BUNDLE_ROOT / "samples.csv")
    drugs = pd.read_csv(EXAMPLE_BUNDLE_ROOT / "drugs.csv")
    dualsyn = pd.read_csv(EXAMPLE_BUNDLE_ROOT / "cells_dualsyn.csv")
    mtl = pd.read_csv(EXAMPLE_BUNDLE_ROOT / "cells_mtl.csv")
    mvc_exp = pd.read_csv(EXAMPLE_BUNDLE_ROOT / "cells_mvc_exp.csv")
    mvc_cn = pd.read_csv(EXAMPLE_BUNDLE_ROOT / "cells_mvc_cn.csv")

    assert_true(len(samples) == EXPECTED_SAMPLE_COUNT, "example_bundle sample count mismatch")
    assert_true(samples["sample_id"].is_unique, "example_bundle sample_id must be unique")
    assert_true("source_sample_id" in samples.columns, "example_bundle must retain source_sample_id")
    assert_true((samples["synergy_score"] >= 30).any(), "example_bundle needs positive smoke rows for MTLSynergy")
    assert_true((samples["synergy_score"] <= 0).any(), "example_bundle needs negative smoke rows for graph models")
    assert_true(drugs.shape[1] - 3 == EXPECTED_DIMS["drug_mtlsynergy"], "example_bundle drug dim mismatch")
    assert_true(dualsyn.shape[1] - 1 == EXPECTED_DIMS["cell_dualsyn"], "example_bundle DualSyn cell dim mismatch")
    assert_true(mtl.shape[1] - 1 == EXPECTED_DIMS["cell_mtlsynergy"], "example_bundle MTLSynergy cell dim mismatch")
    assert_true(mvc_exp.shape[1] - 1 == EXPECTED_DIMS["cell_mvc_exp"], "example_bundle MVC exp dim mismatch")
    assert_true(mvc_cn.shape[1] - 1 == EXPECTED_DIMS["cell_mvc_cn"], "example_bundle MVC cn dim mismatch")


def validate_dualsyn(dataset_root: Path) -> None:
    data_root = dataset_root / "dualsyn" / "data"
    _, cell_width = read_csv_width(data_root / "cell_features_954.csv")
    assert_true(cell_width == EXPECTED_DIMS["cell_dualsyn"] + 1, f"{dataset_root.name} DualSyn cell width mismatch")

    for fold in range(EXPECTED_FOLD_COUNT):
        train_df = pd.read_csv(data_root / f"fold{fold}" / "train.csv")
        test_df = pd.read_csv(data_root / f"fold{fold}" / "test.csv")
        assert_true(len(train_df) == EXPECTED_TRAIN_ROWS, f"{dataset_root.name} DualSyn fold{fold} train size mismatch")
        assert_true(len(test_df) == EXPECTED_TEST_ROWS, f"{dataset_root.name} DualSyn fold{fold} test size mismatch")
        assert_true(train_df["label"].nunique() == 2, f"{dataset_root.name} DualSyn fold{fold} train needs both classes")
        assert_true(test_df["label"].nunique() == 2, f"{dataset_root.name} DualSyn fold{fold} test needs both classes")


def validate_mfsyndcp(dataset_root: Path) -> None:
    data_root = dataset_root / "mfsyndcp" / "data"
    _, cell_width = read_csv_width(data_root / "cell_features.csv")
    assert_true(cell_width == EXPECTED_DIMS["cell_dualsyn"] + 1, f"{dataset_root.name} MFSynDCP cell width mismatch")

    labels_df = pd.read_csv(data_root / "labels.csv")
    assert_true(len(labels_df) == EXPECTED_SAMPLE_COUNT, f"{dataset_root.name} MFSynDCP labels row count mismatch")

    for fold in range(EXPECTED_FOLD_COUNT):
        train_df = pd.read_csv(data_root / "fold" / f"fold{fold}" / "train.csv")
        test_df = pd.read_csv(data_root / "fold" / f"fold{fold}" / "test.csv")
        assert_true(len(train_df) == EXPECTED_TRAIN_ROWS, f"{dataset_root.name} MFSynDCP fold{fold} train size mismatch")
        assert_true(len(test_df) == EXPECTED_TEST_ROWS, f"{dataset_root.name} MFSynDCP fold{fold} test size mismatch")
        assert_true(train_df["label"].nunique() == 2, f"{dataset_root.name} MFSynDCP fold{fold} train needs both classes")
        assert_true(test_df["label"].nunique() == 2, f"{dataset_root.name} MFSynDCP fold{fold} test needs both classes")


def validate_mvcasyn(dataset_root: Path) -> None:
    data_root = dataset_root / "mvcasyn" / "data"
    exp_df = pd.read_csv(data_root / "exp.csv")
    cn_df = pd.read_csv(data_root / "cn.csv")
    assert_true(exp_df.shape[1] - 1 == EXPECTED_DIMS["cell_mvc_exp"], f"{dataset_root.name} MVC exp dim mismatch")
    assert_true(cn_df.shape[1] - 1 == EXPECTED_DIMS["cell_mvc_cn"], f"{dataset_root.name} MVC cn dim mismatch")

    for fold in range(EXPECTED_FOLD_COUNT):
        train_df = pd.read_csv(data_root / "folds" / f"folds{fold}" / "train.csv")
        test_df = pd.read_csv(data_root / "folds" / f"folds{fold}" / "test.csv")
        assert_true(len(train_df) == EXPECTED_TRAIN_ROWS, f"{dataset_root.name} MVC fold{fold} train size mismatch")
        assert_true(len(test_df) == EXPECTED_TEST_ROWS, f"{dataset_root.name} MVC fold{fold} test size mismatch")
        assert_true(train_df["label"].nunique() == 2, f"{dataset_root.name} MVC fold{fold} train needs both classes")
        assert_true(test_df["label"].nunique() == 2, f"{dataset_root.name} MVC fold{fold} test needs both classes")


def validate_mtlsynergy(dataset_root: Path) -> None:
    data_root = dataset_root / "mtlsynergy" / "data"
    drug_features = pd.read_csv(data_root / "drug_features.csv")
    cell_features = pd.read_csv(data_root / "cell_line_features.csv")
    summary = pd.read_csv(data_root / "oneil_summary_idx.csv")

    assert_true(drug_features.shape[1] == EXPECTED_DIMS["drug_mtlsynergy"], f"{dataset_root.name} MTL drug dim mismatch")
    assert_true(cell_features.shape[1] == EXPECTED_DIMS["cell_mtlsynergy"], f"{dataset_root.name} MTL cell dim mismatch")
    assert_true(len(summary) == EXPECTED_SAMPLE_COUNT, f"{dataset_root.name} MTL summary row count mismatch")

    fold_sizes = summary["syn_fold"].value_counts().sort_index().to_dict()
    assert_true(fold_sizes == {fold: EXPECTED_TEST_ROWS for fold in range(EXPECTED_FOLD_COUNT)}, f"{dataset_root.name} MTL syn_fold sizes mismatch")

    for fold in range(EXPECTED_FOLD_COUNT):
        fold_df = summary[summary["syn_fold"] == fold]
        synergy_classes = {int(value > 30) for value in fold_df["synergy_loewe"]}
        sensitivity_classes = {int(value > 50) for value in fold_df["ri_row"]} | {int(value > 50) for value in fold_df["ri_col"]}
        assert_true(len(synergy_classes) == 2, f"{dataset_root.name} MTL fold{fold} needs both synergy classes at threshold 30")
        assert_true(len(sensitivity_classes) == 2, f"{dataset_root.name} MTL fold{fold} needs both sensitivity classes at threshold 50")


def validate_dataset(dataset_name: str, expected_strategy: str) -> None:
    dataset_root = EXPORT_ROOT / dataset_name
    manifest = load_manifest(dataset_root / "protocol" / "manifest.json")

    assert_true(manifest["sample_count"] == EXPECTED_SAMPLE_COUNT, f"{dataset_name} sample count mismatch")
    assert_true(manifest["fold_count"] == EXPECTED_FOLD_COUNT, f"{dataset_name} fold count mismatch")
    assert_true(manifest["fold_strategy"] == expected_strategy, f"{dataset_name} fold strategy mismatch")
    assert_true(manifest["feature_dimensions"] == EXPECTED_DIMS, f"{dataset_name} feature dimensions mismatch")

    fold_sizes = {int(key): value for key, value in manifest["transductive_fold_sizes"].items()}
    assert_true(fold_sizes == {fold: EXPECTED_TEST_ROWS for fold in range(EXPECTED_FOLD_COUNT)}, f"{dataset_name} manifest fold sizes mismatch")

    validate_dualsyn(dataset_root)
    validate_mfsyndcp(dataset_root)
    validate_mvcasyn(dataset_root)
    validate_mtlsynergy(dataset_root)


def main() -> None:
    validate_example_bundle()
    validate_dataset("smoke_test", "sample_group")
    validate_dataset("smoke_test_pair_group", "pair_group")
    print("Smoke datasets validated successfully.")


if __name__ == "__main__":
    main()
