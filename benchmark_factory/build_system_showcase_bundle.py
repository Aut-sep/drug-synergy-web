from __future__ import annotations

import argparse
import csv
import json
import shutil
from itertools import combinations
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Set, Tuple


FEATURE_FILE_NAMES = [
    "drugs.csv",
    "cells_dualsyn.csv",
    "cells_mtl.csv",
    "cells_mvc_exp.csv",
    "cells_mvc_cn.csv",
]

MINI_DEMO_CELLS = ["A375", "HT29", "NCIH460", "SKOV3"]
MINI_DEMO_PAIR_COUNT = 30


def read_csv_dicts(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: Sequence[str], rows: Iterable[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)


def canonical_pair(drug_a: str, drug_b: str) -> Tuple[str, str]:
    return tuple(sorted((drug_a, drug_b)))


def build_demo_rows(
    drug_names: Sequence[str],
    cell_lines: Sequence[str],
    seen_triples: Set[Tuple[str, str, str]],
) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    row_index = 1
    for drug_a, drug_b in combinations(sorted(drug_names), 2):
        for cell_line in sorted(cell_lines):
            triple = (drug_a, drug_b, cell_line)
            if triple in seen_triples:
                continue
            rows.append(
                {
                    "sample_id": f"demo_unseen_pair_{row_index:06d}",
                    "drug_a_name": drug_a,
                    "drug_b_name": drug_b,
                    "cell_line": cell_line,
                    "synergy_score": "",
                    "ri_row": "",
                    "ri_col": "",
                    "demo_group": "unseen_drug_pair_known_cell",
                    "demo_note": "inference_only_no_ground_truth",
                }
            )
            row_index += 1
    return rows


def build_mini_rows(all_rows: Sequence[Dict[str, str]]) -> List[Dict[str, str]]:
    selected_rows: List[Dict[str, str]] = []
    selected_pairs = []
    pair_seen = set()
    for row in all_rows:
        pair = canonical_pair(row["drug_a_name"], row["drug_b_name"])
        if pair in pair_seen:
            continue
        pair_seen.add(pair)
        selected_pairs.append(pair)
        if len(selected_pairs) == MINI_DEMO_PAIR_COUNT:
            break

    selected_pair_set = set(selected_pairs)
    for row in all_rows:
        pair = canonical_pair(row["drug_a_name"], row["drug_b_name"])
        if pair not in selected_pair_set:
            continue
        if row["cell_line"] not in MINI_DEMO_CELLS:
            continue
        selected_rows.append(dict(row))

    for index, row in enumerate(selected_rows, start=1):
        row["sample_id"] = f"demo_live_{index:04d}"

    return selected_rows


def collect_seen_info(
    sample_rows: Sequence[Dict[str, str]],
) -> Tuple[Set[Tuple[str, str, str]], Set[Tuple[str, str]]]:
    seen_triples: Set[Tuple[str, str, str]] = set()
    seen_pairs: Set[Tuple[str, str]] = set()
    for row in sample_rows:
        pair = canonical_pair(row["drug_a_name"], row["drug_b_name"])
        triple = (pair[0], pair[1], row["cell_line"])
        seen_pairs.add(pair)
        seen_triples.add(triple)
    return seen_triples, seen_pairs


def copy_feature_files(source_root: Path, output_root: Path) -> None:
    for file_name in FEATURE_FILE_NAMES:
        shutil.copy2(source_root / file_name, output_root / file_name)


def main() -> None:
    default_source_root = Path(__file__).resolve().parent / "input_bundles" / "oneil_intersection_38drug_29cell"
    default_output_root = Path(__file__).resolve().parent / "demo_bundles" / "system_showcase_unseen_pair_inference"

    parser = argparse.ArgumentParser(
        description="Build an inference-only showcase bundle that does not overlap the existing benchmark samples."
    )
    parser.add_argument("--source-root", type=Path, default=default_source_root)
    parser.add_argument("--output-root", type=Path, default=default_output_root)
    parser.add_argument("--dataset-name", default="system_showcase_unseen_pair_inference")
    args = parser.parse_args()

    source_root = args.source_root.resolve()
    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    source_samples = read_csv_dicts(source_root / "samples.csv")
    source_drugs = read_csv_dicts(source_root / "drugs.csv")
    source_cells = read_csv_dicts(source_root / "cells_dualsyn.csv")

    drug_names = sorted(row["drug_name"] for row in source_drugs)
    cell_lines = sorted(row["cell_line"] for row in source_cells)
    seen_triples, seen_pairs = collect_seen_info(source_samples)
    all_pair_count = len(drug_names) * (len(drug_names) - 1) // 2
    unseen_pair_count = all_pair_count - len(seen_pairs)

    demo_rows = build_demo_rows(drug_names, cell_lines, seen_triples)
    mini_rows = build_mini_rows(demo_rows)

    copy_feature_files(source_root, output_root)

    sample_fieldnames = [
        "sample_id",
        "drug_a_name",
        "drug_b_name",
        "cell_line",
        "synergy_score",
        "ri_row",
        "ri_col",
        "demo_group",
        "demo_note",
    ]
    write_csv(output_root / "samples.csv", sample_fieldnames, demo_rows)
    write_csv(output_root / "samples_live_demo_120.csv", sample_fieldnames, mini_rows)

    manifest = {
        "dataset_name": args.dataset_name,
        "description": "Inference-only showcase bundle built from novel drug-pair candidates over the 38-drug x 29-cell shared space.",
        "source_bundle": str(source_root),
        "sample_count": len(demo_rows),
        "mini_demo_sample_count": len(mini_rows),
        "drug_count": len(drug_names),
        "cell_count": len(cell_lines),
        "all_unordered_pair_count": all_pair_count,
        "seen_pair_count": len(seen_pairs),
        "unseen_pair_count": unseen_pair_count,
        "raw_seen_sample_count": len(source_samples),
        "overlap_with_source_sample_count": 0,
        "demo_group": "unseen_drug_pair_known_cell",
        "mini_demo_cells": MINI_DEMO_CELLS,
        "mini_demo_pair_count": MINI_DEMO_PAIR_COUNT,
        "notes": [
            "This bundle is for inference showcase only and does not contain ground-truth labels.",
            "All candidate rows are excluded from the raw 16907-sample four-model intersection bundle.",
            "Because the main experiment and both sub-experiments are derived from the same raw intersection universe, this showcase bundle is also disjoint from those experiment samples.",
            "The recommended deployment policy is to use the saved 5-fold models as an ensemble and average their predictions on this bundle.",
        ],
    }
    write_json(output_root / "demo_manifest.json", manifest)

    print(f"output_root={output_root}")
    print(f"sample_count={len(demo_rows)}")
    print(f"mini_demo_sample_count={len(mini_rows)}")
    print(f"unseen_pair_count={unseen_pair_count}")


if __name__ == "__main__":
    main()
