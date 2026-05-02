from __future__ import annotations

import argparse
from pathlib import Path

from adapter_core import (
    REQUIRED_DRUG_COLUMNS,
    REQUIRED_DUALSYN_CELL_COLUMNS,
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export one canonical dataset bundle into four model-specific layouts.")
    parser.add_argument("--input-root", required=True, help="Directory containing the canonical input bundle.")
    parser.add_argument("--output-root", required=True, help="Directory where exports will be written.")
    parser.add_argument("--dataset-name", default="benchmark_dataset", help="Folder name under output-root.")
    parser.add_argument("--label-source", choices=["threshold", "existing"], default="threshold")
    parser.add_argument("--label-threshold", type=float, default=10.0)
    parser.add_argument("--default-ri", type=float, default=0.0)
    parser.add_argument("--fold-count", type=int, default=5)
    parser.add_argument(
        "--fold-strategy",
        choices=["pair_group", "pair_cell_group", "sample_group"],
        default="pair_group",
        help="How to assign the shared 5-fold split. pair_group is recommended for fair thesis comparison.",
    )
    parser.add_argument("--seed", type=int, default=20260413)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    input_root = Path(args.input_root).resolve()
    output_root = Path(args.output_root).resolve()

    expected = {
        "samples.csv": REQUIRED_SAMPLE_COLUMNS,
        "drugs.csv": REQUIRED_DRUG_COLUMNS,
        "cells_dualsyn.csv": REQUIRED_DUALSYN_CELL_COLUMNS,
        "cells_mtl.csv": REQUIRED_MTL_CELL_COLUMNS,
        "cells_mvc_exp.csv": REQUIRED_MVC_CELL_COLUMNS,
        "cells_mvc_cn.csv": REQUIRED_MVC_CELL_COLUMNS,
    }
    for file_name in expected:
        file_path = input_root / file_name
        if not file_path.exists():
            raise FileNotFoundError(f"Missing input file: {file_path}")

    samples = load_samples(
        input_root / "samples.csv",
        label_source=args.label_source,
        label_threshold=args.label_threshold,
        default_ri=args.default_ri,
    )
    drugs = load_drugs(input_root / "drugs.csv")
    dualsyn_cells = load_feature_table(input_root / "cells_dualsyn.csv", REQUIRED_DUALSYN_CELL_COLUMNS)
    mtl_cells = load_feature_table(input_root / "cells_mtl.csv", REQUIRED_MTL_CELL_COLUMNS)
    mvc_exp_cells = load_feature_table(input_root / "cells_mvc_exp.csv", REQUIRED_MVC_CELL_COLUMNS)
    mvc_cn_cells = load_feature_table(input_root / "cells_mvc_cn.csv", REQUIRED_MVC_CELL_COLUMNS)

    validate_bundle(samples, drugs, dualsyn_cells, mtl_cells, mvc_exp_cells, mvc_cn_cells)
    assignments = build_protocol_assignments(samples, args.fold_count, args.seed, args.fold_strategy)

    export_dualsyn(args.dataset_name, output_root, assignments, drugs, dualsyn_cells, args.fold_count)
    export_mfsyndcp(args.dataset_name, output_root, assignments, drugs, dualsyn_cells, args.fold_count)
    export_mvcasyn(args.dataset_name, output_root, assignments, drugs, mvc_exp_cells, mvc_cn_cells, args.fold_count)
    export_mtlsynergy(args.dataset_name, output_root, assignments, drugs, mtl_cells)

    protocol_root = output_root / args.dataset_name / "protocol"
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
        dataset_name=args.dataset_name,
        assignments=assignments,
        drugs=drugs,
        dualsyn_cells=dualsyn_cells,
        mtl_cells=mtl_cells,
        mvc_exp_cells=mvc_exp_cells,
        mvc_cn_cells=mvc_cn_cells,
        fold_count=args.fold_count,
        label_source=args.label_source,
        label_threshold=args.label_threshold,
        default_ri=args.default_ri,
        seed=args.seed,
        fold_strategy=args.fold_strategy,
    )
    write_json(protocol_root / "manifest.json", manifest)

    print(f"dataset_name={args.dataset_name}")
    print(f"sample_count={manifest['sample_count']}")
    print(f"drug_count={manifest['drug_count']}")
    print(f"cell_count={manifest['cell_count']}")
    print(f"fold_strategy={manifest['fold_strategy']}")
    print(f"output_dir={output_root / args.dataset_name}")


if __name__ == "__main__":
    main()
