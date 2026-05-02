import argparse
import csv
from pathlib import Path


DRUG_ALIASES = {
    "Carboplatinum": "CARBOPLATIN",
}

MVC_CELL_ALIASES = {
    "NIHOVCAR3": "OVCAR3",
}


def read_csv_dicts(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def read_csv_rows(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.reader(handle))


def normalize_drug(name: str) -> str:
    return DRUG_ALIASES.get(name, name)


def normalize_mvc_cell(name: str) -> str:
    return MVC_CELL_ALIASES.get(name, name)


def load_full_oneil(repo_root: Path):
    summary_backup = repo_root / "MTLSynergy" / "data" / "oneil_summary_idx_original_backup.csv"
    summary_reduced = repo_root / "MTLSynergy" / "data" / "oneil_summary_idx.csv"
    drug_lookup = repo_root / "MTLSynergy" / "data" / "drugs.csv"
    cell_lookup = repo_root / "MTLSynergy" / "data" / "cell_lines.csv"

    summary_rows = read_csv_dicts(summary_backup)
    reduced_rows = read_csv_dicts(summary_reduced)
    drug_rows = read_csv_dicts(drug_lookup)
    cell_rows = read_csv_dicts(cell_lookup)

    idx2drug = {row["id"]: row["name"] for row in drug_rows}
    idx2cell = {row["id"]: row["name"] for row in cell_rows}

    full_drugs_raw = {
        idx2drug[row["drug_row_idx"]] for row in summary_rows
    } | {
        idx2drug[row["drug_col_idx"]] for row in summary_rows
    }
    full_cells = {idx2cell[row["cell_line_idx"]] for row in summary_rows}

    full_drugs = {normalize_drug(name) for name in full_drugs_raw}
    max_drug_idx = max(max(int(row["drug_row_idx"]), int(row["drug_col_idx"])) for row in summary_rows)
    max_cell_idx = max(int(row["cell_line_idx"]) for row in summary_rows)

    return {
        "summary_backup": summary_backup,
        "summary_reduced": summary_reduced,
        "drug_lookup": drug_lookup,
        "cell_lookup": cell_lookup,
        "summary_rows": summary_rows,
        "backup_row_count": len(summary_rows),
        "reduced_row_count": len(reduced_rows),
        "full_drugs_raw": sorted(full_drugs_raw),
        "full_drugs": sorted(full_drugs),
        "full_cells": sorted(full_cells),
        "max_drug_idx": max_drug_idx,
        "max_cell_idx": max_cell_idx,
    }


def load_dualsyn(repo_root: Path):
    drug_rows = read_csv_dicts(repo_root / "DualSyn" / "DualSyn" / "data" / "smiles.csv")
    cell_rows = read_csv_rows(repo_root / "DualSyn" / "DualSyn" / "data" / "cell_features_954.csv")

    drugs = {normalize_drug(row["name"]) for row in drug_rows}
    cells = {row[0].split("_")[0] for row in cell_rows[2:] if row and row[0]}

    return {
        "name": "DualSyn",
        "drugs": drugs,
        "cells": cells,
        "drug_file": repo_root / "DualSyn" / "DualSyn" / "data" / "smiles.csv",
        "cell_file": repo_root / "DualSyn" / "DualSyn" / "data" / "cell_features_954.csv",
        "notes": ["细胞特征首列带组织后缀，核对时需要先去掉下划线后的组织名。"],
    }


def load_mfsyndcp(repo_root: Path):
    drug_rows = read_csv_dicts(repo_root / "MFSynDCP" / "MFSynDCP" / "data" / "smiles.csv")
    cell_rows = read_csv_rows(repo_root / "MFSynDCP" / "MFSynDCP" / "data" / "cell_features.csv")

    drugs = {normalize_drug(row["name"]) for row in drug_rows}
    cells = {row[0] for row in cell_rows[2:] if row and row[0]}

    return {
        "name": "MFSynDCP",
        "drugs": drugs,
        "cells": cells,
        "drug_file": repo_root / "MFSynDCP" / "MFSynDCP" / "data" / "smiles.csv",
        "cell_file": repo_root / "MFSynDCP" / "MFSynDCP" / "data" / "cell_features.csv",
        "notes": [],
    }


def load_mvcasyn(repo_root: Path):
    drug_rows = read_csv_dicts(repo_root / "MVCASyn" / "data" / "oneil_drug_two_smiles.csv")
    exp_rows = read_csv_dicts(repo_root / "MVCASyn" / "data" / "exp.csv")
    cn_rows = read_csv_dicts(repo_root / "MVCASyn" / "data" / "cn.csv")

    drugs = {normalize_drug(row["drug_name"]) for row in drug_rows}
    exp_cells = {normalize_mvc_cell(row["cell_line_name"]) for row in exp_rows}
    cn_cells = {normalize_mvc_cell(row["cell_line_name"]) for row in cn_rows}
    cells = exp_cells & cn_cells

    return {
        "name": "MVCASyn",
        "drugs": drugs,
        "cells": cells,
        "drug_file": repo_root / "MVCASyn" / "data" / "oneil_drug_two_smiles.csv",
        "cell_file": [
            repo_root / "MVCASyn" / "data" / "exp.csv",
            repo_root / "MVCASyn" / "data" / "cn.csv",
        ],
        "notes": [
            "MVCASyn 必须同时具备表达谱 exp.csv 和拷贝数 cn.csv。",
            "本地文件中的 NIHOVCAR3 需要映射回 OVCAR3 才能和 O'Neil 名称对齐。",
        ],
    }


def load_mtlsynergy(repo_root: Path, full_oneil):
    drug_feature_path = repo_root / "MTLSynergy" / "data" / "drug_features.csv"
    cell_feature_path = repo_root / "MTLSynergy" / "data" / "cell_line_features.csv"

    with drug_feature_path.open(encoding="utf-8-sig") as handle:
        drug_feature_rows = sum(1 for _ in handle) - 1
    with cell_feature_path.open(encoding="utf-8-sig") as handle:
        cell_feature_rows = sum(1 for _ in handle) - 1

    supported = drug_feature_rows > full_oneil["max_drug_idx"] and cell_feature_rows > full_oneil["max_cell_idx"]

    return {
        "name": "MTLSynergy",
        "drugs": set(full_oneil["full_drugs"]),
        "cells": set(full_oneil["full_cells"]),
        "drug_file": drug_feature_path,
        "cell_file": cell_feature_path,
        "notes": [
            "MTLSynergy 通过 summary 中的整数索引直接读取药物和细胞特征，而不是靠名字匹配。",
            f"drug_features.csv 行数 = {drug_feature_rows}，summary 最大 drug_idx = {full_oneil['max_drug_idx']}。",
            f"cell_line_features.csv 行数 = {cell_feature_rows}，summary 最大 cell_idx = {full_oneil['max_cell_idx']}。",
            "就本地这套原始文件来说，MTLSynergy 不缺运行所需特征，但做跨模型统一时仍应把 Carboplatinum 规范成 CARBOPLATIN。",
        ],
        "index_supported": supported,
    }


def compute_report(repo_root: Path):
    full_oneil = load_full_oneil(repo_root)
    models = [
        load_dualsyn(repo_root),
        load_mfsyndcp(repo_root),
        load_mvcasyn(repo_root),
        load_mtlsynergy(repo_root, full_oneil),
    ]

    full_drugs = set(full_oneil["full_drugs"])
    full_cells = set(full_oneil["full_cells"])

    for model in models:
        model["missing_drugs"] = sorted(full_drugs - model["drugs"])
        model["missing_cells"] = sorted(full_cells - model["cells"])

    common_drugs = sorted(set.intersection(*(model["drugs"] for model in models)))
    common_cells = sorted(set.intersection(*(model["cells"] for model in models)))

    retained_rows = 0
    idx2drug = {
        row["id"]: normalize_drug(row["name"])
        for row in read_csv_dicts(repo_root / "MTLSynergy" / "data" / "drugs.csv")
    }
    idx2cell = {
        row["id"]: row["name"]
        for row in read_csv_dicts(repo_root / "MTLSynergy" / "data" / "cell_lines.csv")
    }
    for row in full_oneil["summary_rows"]:
        d1 = idx2drug[row["drug_row_idx"]]
        d2 = idx2drug[row["drug_col_idx"]]
        c = idx2cell[row["cell_line_idx"]]
        if d1 in common_drugs and d2 in common_drugs and c in common_cells:
            retained_rows += 1

    return {
        "full_oneil": full_oneil,
        "models": models,
        "common_drugs": common_drugs,
        "common_cells": common_cells,
        "retained_rows": retained_rows,
    }


def print_report(report):
    full_oneil = report["full_oneil"]

    print("O'Neil local source audit")
    print(f"summary backup: {full_oneil['summary_backup']}")
    print(f"summary reduced: {full_oneil['summary_reduced']}")
    print(f"backup rows: {full_oneil['backup_row_count']}")
    print(f"reduced rows: {full_oneil['reduced_row_count']}")
    print(f"full drugs after alias normalization: {len(full_oneil['full_drugs'])}")
    print(f"full cells: {len(full_oneil['full_cells'])}")
    print("")

    for model in report["models"]:
        print(model["name"])
        print(f"  missing drugs ({len(model['missing_drugs'])}): {model['missing_drugs']}")
        print(f"  missing cells ({len(model['missing_cells'])}): {model['missing_cells']}")
        for note in model["notes"]:
            print(f"  note: {note}")
        print("")

    print(f"all-four common drugs: {len(report['common_drugs'])}")
    print(report["common_drugs"])
    print(f"all-four common cells: {len(report['common_cells'])}")
    print(report["common_cells"])
    print(f"retained O'Neil samples on common subset: {report['retained_rows']}")


def main():
    default_repo_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="Audit local O'Neil source coverage for the four original models.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root, help="Project root that contains DualSyn, MFSynDCP, MVCASyn, and MTLSynergy.")
    args = parser.parse_args()

    report = compute_report(args.repo_root)
    print_report(report)


if __name__ == "__main__":
    main()
