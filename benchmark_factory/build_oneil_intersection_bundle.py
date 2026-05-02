from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


DRUG_ALIASES = {
    "Carboplatinum": "CARBOPLATIN",
}

MVC_CELL_ALIASES = {
    "NIHOVCAR3": "OVCAR3",
}


def read_csv_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle))


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[list[object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)


def normalize_drug(name: str) -> str:
    return DRUG_ALIASES.get(name, name)


def normalize_mvc_cell(name: str) -> str:
    return MVC_CELL_ALIASES.get(name, name)


def assign_strict_label(synergy_score: float) -> int | None:
    if synergy_score > 10:
        return 1
    if synergy_score < 0:
        return 0
    return None


def load_full_oneil(repo_root: Path) -> dict[str, object]:
    summary_rows = read_csv_dicts(repo_root / "MTLSynergy" / "data" / "oneil_summary_idx_original_backup.csv")
    drug_rows = read_csv_dicts(repo_root / "MTLSynergy" / "data" / "drugs.csv")
    cell_rows = read_csv_dicts(repo_root / "MTLSynergy" / "data" / "cell_lines.csv")

    idx2drug = {row["id"]: row for row in drug_rows}
    idx2cell = {row["id"]: row for row in cell_rows}

    full_drug_names = sorted(
        {
            normalize_drug(idx2drug[row["drug_row_idx"]]["name"])
            for row in summary_rows
        }
        | {
            normalize_drug(idx2drug[row["drug_col_idx"]]["name"])
            for row in summary_rows
        }
    )
    full_cell_names = sorted({idx2cell[row["cell_line_idx"]]["name"] for row in summary_rows})

    return {
        "summary_rows": summary_rows,
        "drug_rows": drug_rows,
        "cell_rows": cell_rows,
        "idx2drug": idx2drug,
        "idx2cell": idx2cell,
        "full_drug_names": full_drug_names,
        "full_cell_names": full_cell_names,
    }


def load_common_drugs(repo_root: Path, full_drug_names: list[str]) -> tuple[list[str], dict[str, str]]:
    common_drugs = set(full_drug_names)
    smiles_map: dict[str, str] = {}

    for path, name_key, smiles_key in [
        (repo_root / "DualSyn" / "DualSyn" / "data" / "smiles.csv", "name", "smile"),
        (repo_root / "MFSynDCP" / "MFSynDCP" / "data" / "smiles.csv", "name", "smile"),
        (repo_root / "MVCASyn" / "data" / "oneil_drug_two_smiles.csv", "drug_name", "smiles"),
    ]:
        rows = read_csv_dicts(path)
        normalized = {}
        for row in rows:
            drug_name = normalize_drug(row[name_key].strip())
            normalized[drug_name] = row[smiles_key].strip()
            smiles_map.setdefault(drug_name, row[smiles_key].strip())
        common_drugs &= set(normalized)

    return sorted(common_drugs), smiles_map


def load_common_cells(repo_root: Path, full_cell_names: list[str]) -> list[str]:
    full_cells = set(full_cell_names)

    dual_rows = read_csv_rows(repo_root / "DualSyn" / "DualSyn" / "data" / "cell_features_954.csv")
    dual_cells = {row[0].split("_")[0] for row in dual_rows[2:] if row and row[0]}

    mfs_rows = read_csv_rows(repo_root / "MFSynDCP" / "MFSynDCP" / "data" / "cell_features.csv")
    mfs_cells = {row[0] for row in mfs_rows[2:] if row and row[0]}

    mvc_exp_rows = read_csv_dicts(repo_root / "MVCASyn" / "data" / "exp.csv")
    mvc_cn_rows = read_csv_dicts(repo_root / "MVCASyn" / "data" / "cn.csv")
    mvc_exp_cells = {normalize_mvc_cell(row["cell_line_name"].strip()) for row in mvc_exp_rows}
    mvc_cn_cells = {normalize_mvc_cell(row["cell_line_name"].strip()) for row in mvc_cn_rows}
    mvc_cells = mvc_exp_cells & mvc_cn_cells

    return sorted(full_cells & dual_cells & mfs_cells & mvc_cells)


def build_samples(
    full_oneil: dict[str, object],
    common_drugs: list[str],
    common_cells: list[str],
    label_policy: str,
) -> list[list[object]]:
    allowed_drugs = set(common_drugs)
    allowed_cells = set(common_cells)

    header = ["sample_id", "drug_a_name", "drug_b_name", "cell_line", "synergy_score", "ri_row", "ri_col"]
    if label_policy == "strict_gt10_lt0":
        header.append("label")
    rows = [header]
    sample_count = 0
    for raw_row in full_oneil["summary_rows"]:
        drug_a = normalize_drug(full_oneil["idx2drug"][raw_row["drug_row_idx"]]["name"])
        drug_b = normalize_drug(full_oneil["idx2drug"][raw_row["drug_col_idx"]]["name"])
        cell_line = full_oneil["idx2cell"][raw_row["cell_line_idx"]]["name"]
        if drug_a not in allowed_drugs or drug_b not in allowed_drugs or cell_line not in allowed_cells:
            continue
        synergy_score = float(raw_row["synergy_loewe"])
        label = None
        if label_policy == "strict_gt10_lt0":
            label = assign_strict_label(synergy_score)
            if label is None:
                continue
        sample_count += 1
        sample_row: list[object] = [
            f"oneil_{sample_count:05d}",
            drug_a,
            drug_b,
            cell_line,
            raw_row["synergy_loewe"],
            raw_row["ri_row"],
            raw_row["ri_col"],
        ]
        if label_policy == "strict_gt10_lt0":
            sample_row.append(label)
        rows.append(sample_row)
    return rows


def build_drugs(
    repo_root: Path,
    full_oneil: dict[str, object],
    common_drugs: list[str],
    smiles_map: dict[str, str],
) -> list[list[object]]:
    drug_feature_rows = read_csv_rows(repo_root / "MTLSynergy" / "data" / "drug_features.csv")
    drug_feature_header = [f"mtl_drug_feat_{index + 1}" for index in range(len(drug_feature_rows[0]))]

    summary_used_ids = {
        row["drug_row_idx"] for row in full_oneil["summary_rows"]
    } | {
        row["drug_col_idx"] for row in full_oneil["summary_rows"]
    }
    canonical_to_lookup_row: dict[str, dict[str, str]] = {}
    for raw_row in full_oneil["drug_rows"]:
        canonical_name = normalize_drug(raw_row["name"])
        raw_id = raw_row["id"]
        if raw_id in summary_used_ids:
            canonical_to_lookup_row[canonical_name] = raw_row
        elif canonical_name not in canonical_to_lookup_row:
            canonical_to_lookup_row[canonical_name] = raw_row

    rows = [["drug_name", "smiles", "synonyms", *drug_feature_header]]
    for drug_name in common_drugs:
        lookup_row = canonical_to_lookup_row[drug_name]
        feature_row = drug_feature_rows[int(lookup_row["id"]) + 1]
        rows.append(
            [
                drug_name,
                smiles_map[drug_name],
                lookup_row["synonyms"],
                *feature_row,
            ]
        )
    return rows


def build_dualsyn_cells(repo_root: Path, common_cells: list[str]) -> list[list[object]]:
    raw_rows = read_csv_rows(repo_root / "DualSyn" / "DualSyn" / "data" / "cell_features_954.csv")
    feature_header = [f"dualsyn_feat_{index + 1}" for index in range(len(raw_rows[0]) - 1)]
    cell_map: dict[str, list[str]] = {}
    for row in raw_rows[2:]:
        if not row or not row[0]:
            continue
        cell_name = row[0].split("_")[0]
        cell_map[cell_name] = row[1:]

    rows = [["cell_line", *feature_header]]
    for cell_name in common_cells:
        rows.append([cell_name, *cell_map[cell_name]])
    return rows


def build_mtl_cells(repo_root: Path, full_oneil: dict[str, object], common_cells: list[str]) -> list[list[object]]:
    feature_rows = read_csv_rows(repo_root / "MTLSynergy" / "data" / "cell_line_features.csv")
    feature_header = [f"mtl_cell_feat_{index + 1}" for index in range(len(feature_rows[0]))]
    lookup = {row["name"]: int(row["id"]) for row in full_oneil["cell_rows"]}

    rows = [["cell_line", *feature_header]]
    for cell_name in common_cells:
        rows.append([cell_name, *feature_rows[lookup[cell_name] + 1]])
    return rows


def build_mvc_cells(repo_root: Path, common_cells: list[str], file_name: str, prefix: str) -> list[list[object]]:
    raw_rows = read_csv_rows(repo_root / "MVCASyn" / "data" / file_name)
    feature_header = [f"{prefix}_{index + 1}" for index in range(len(raw_rows[0]) - 1)]
    keep = set(common_cells)

    cell_map: dict[str, list[str]] = {}
    for row in raw_rows[1:]:
        if not row or not row[0]:
            continue
        cell_name = normalize_mvc_cell(row[0])
        if cell_name in keep:
            cell_map[cell_name] = row[1:]

    rows = [["cell_line", *feature_header]]
    for cell_name in common_cells:
        rows.append([cell_name, *cell_map[cell_name]])
    return rows


def build_manifest(
    dataset_name: str,
    common_drugs: list[str],
    common_cells: list[str],
    sample_rows: list[list[object]],
    label_policy: str,
) -> dict[str, object]:
    labels = []
    if "label" in sample_rows[0]:
        label_idx = sample_rows[0].index("label")
        labels = [int(row[label_idx]) for row in sample_rows[1:]]
    return {
        "dataset_name": dataset_name,
        "description": "Four-model O'Neil intersection bundle in canonical benchmark_factory input format.",
        "sample_count": len(sample_rows) - 1,
        "drug_count": len(common_drugs),
        "cell_count": len(common_cells),
        "label_policy": label_policy,
        "class_distribution": {
            "0": sum(1 for label in labels if label == 0),
            "1": sum(1 for label in labels if label == 1),
        } if labels else {},
        "drug_aliases": DRUG_ALIASES,
        "mvc_cell_aliases": MVC_CELL_ALIASES,
        "source_summary": "MTLSynergy/data/oneil_summary_idx_original_backup.csv",
        "source_drug_lookup": "MTLSynergy/data/drugs.csv",
        "source_cell_lookup": "MTLSynergy/data/cell_lines.csv",
        "notes": [
            "Drug names are normalized so Carboplatinum is exported as CARBOPLATIN.",
            "MVCASyn cell names are normalized so NIHOVCAR3 is exported as OVCAR3.",
            "This bundle keeps only samples whose drugs and cells are available across all four model input systems.",
            "The shared 954-d cell matrix is exported from DualSyn/cell_features_954.csv to avoid the suspicious NCIH23 row found in local MFSynDCP/cell_features.csv.",
            "MTLSynergy drug metadata/features are taken from the actual O'Neil-used row when a normalized drug name has multiple aliases.",
        ],
    }


def main() -> None:
    default_repo_root = Path(__file__).resolve().parent.parent
    default_output_root = Path(__file__).resolve().parent / "input_bundles" / "oneil_intersection_38drug_29cell"

    parser = argparse.ArgumentParser(description="Build the four-model common O'Neil intersection bundle.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--output-root", type=Path, default=default_output_root)
    parser.add_argument(
        "--label-policy",
        choices=["raw", "strict_gt10_lt0"],
        default="raw",
        help="raw keeps all intersection samples; strict_gt10_lt0 keeps synergy>10 as positive and synergy<0 as negative.",
    )
    parser.add_argument(
        "--dataset-name",
        default=None,
        help="Optional dataset name written into bundle_manifest.json.",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    full_oneil = load_full_oneil(repo_root)
    common_drugs, smiles_map = load_common_drugs(repo_root, full_oneil["full_drug_names"])
    common_cells = load_common_cells(repo_root, full_oneil["full_cell_names"])

    sample_rows = build_samples(full_oneil, common_drugs, common_cells, args.label_policy)
    drug_rows = build_drugs(repo_root, full_oneil, common_drugs, smiles_map)
    dualsyn_cell_rows = build_dualsyn_cells(repo_root, common_cells)
    mtl_cell_rows = build_mtl_cells(repo_root, full_oneil, common_cells)
    mvc_exp_rows = build_mvc_cells(repo_root, common_cells, "exp.csv", "mvc_exp")
    mvc_cn_rows = build_mvc_cells(repo_root, common_cells, "cn.csv", "mvc_cn")
    dataset_name = args.dataset_name or output_root.name
    manifest = build_manifest(dataset_name, common_drugs, common_cells, sample_rows, args.label_policy)

    write_csv(output_root / "samples.csv", sample_rows)
    write_csv(output_root / "drugs.csv", drug_rows)
    write_csv(output_root / "cells_dualsyn.csv", dualsyn_cell_rows)
    write_csv(output_root / "cells_mtl.csv", mtl_cell_rows)
    write_csv(output_root / "cells_mvc_exp.csv", mvc_exp_rows)
    write_csv(output_root / "cells_mvc_cn.csv", mvc_cn_rows)
    write_json(output_root / "bundle_manifest.json", manifest)

    print(f"output_root={output_root}")
    print(f"sample_count={manifest['sample_count']}")
    print(f"drug_count={manifest['drug_count']}")
    print(f"cell_count={manifest['cell_count']}")


if __name__ == "__main__":
    main()
