from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple


REQUIRED_SAMPLE_COLUMNS = ["drug_a_name", "drug_b_name", "cell_line", "synergy_score"]
REQUIRED_DRUG_COLUMNS = ["drug_name", "smiles"]
REQUIRED_MTL_CELL_COLUMNS = ["cell_line"]
REQUIRED_MVC_CELL_COLUMNS = ["cell_line"]
REQUIRED_DUALSYN_CELL_COLUMNS = ["cell_line"]


@dataclass(frozen=True)
class SampleRecord:
    sample_id: str
    drug_a_name: str
    drug_b_name: str
    cell_line: str
    synergy_score: float
    label: int
    ri_row: float
    ri_col: float


@dataclass(frozen=True)
class DrugRecord:
    drug_name: str
    smiles: str
    synonyms: str
    feature_values: Tuple[float, ...]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_csv_rows(path: Path) -> List[List[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle))


def read_csv_dicts(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: Sequence[str], rows: Iterable[Dict[str, object]]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_csv_rows(path: Path, rows: Iterable[Sequence[object]]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        for row in rows:
            writer.writerow(row)


def write_json(path: Path, payload: Dict[str, object]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)


def require_columns(path: Path, header: Sequence[str], required: Sequence[str]) -> None:
    missing = [name for name in required if name not in header]
    if missing:
        raise ValueError(f"{path} is missing required columns: {missing}")


def parse_float(value: str, field_name: str, path: Path) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{path} has non-numeric value in {field_name}: {value!r}") from exc


def parse_int(value: str, field_name: str, path: Path) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{path} has non-integer value in {field_name}: {value!r}") from exc


def stable_hash(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest(), 16)


def load_samples(
    path: Path,
    label_source: str,
    label_threshold: float,
    default_ri: float,
) -> List[SampleRecord]:
    rows = read_csv_dicts(path)
    if not rows:
        raise ValueError(f"{path} is empty")
    require_columns(path, rows[0].keys(), REQUIRED_SAMPLE_COLUMNS)

    records: List[SampleRecord] = []
    seen_ids: set[str] = set()
    for index, row in enumerate(rows):
        sample_id = (row.get("sample_id") or "").strip() or f"sample_{index}"
        if sample_id in seen_ids:
            raise ValueError(f"{path} has duplicate sample_id: {sample_id}")
        seen_ids.add(sample_id)

        synergy_score = parse_float(row["synergy_score"], "synergy_score", path)
        if label_source == "existing":
            if "label" not in row or row["label"] == "":
                raise ValueError(f"{path} is missing label for sample_id={sample_id}")
            label = parse_int(row["label"], "label", path)
        else:
            label = 1 if synergy_score >= label_threshold else 0

        ri_row = parse_float(row.get("ri_row", default_ri), "ri_row", path)
        ri_col = parse_float(row.get("ri_col", default_ri), "ri_col", path)
        records.append(
            SampleRecord(
                sample_id=sample_id,
                drug_a_name=row["drug_a_name"].strip(),
                drug_b_name=row["drug_b_name"].strip(),
                cell_line=row["cell_line"].strip(),
                synergy_score=synergy_score,
                label=label,
                ri_row=ri_row,
                ri_col=ri_col,
            )
        )
    return records


def load_drugs(path: Path) -> Dict[str, DrugRecord]:
    rows = read_csv_dicts(path)
    if not rows:
        raise ValueError(f"{path} is empty")
    require_columns(path, rows[0].keys(), REQUIRED_DRUG_COLUMNS)

    fixed_columns = {"drug_name", "smiles", "synonyms"}
    feature_columns = [name for name in rows[0].keys() if name not in fixed_columns]
    records: Dict[str, DrugRecord] = {}
    for row in rows:
        drug_name = row["drug_name"].strip()
        if drug_name in records:
            raise ValueError(f"{path} has duplicate drug_name: {drug_name}")
        feature_values = tuple(parse_float(row[column], column, path) for column in feature_columns)
        records[drug_name] = DrugRecord(
            drug_name=drug_name,
            smiles=row["smiles"].strip(),
            synonyms=(row.get("synonyms") or "").strip(),
            feature_values=feature_values,
        )
    return records


def load_feature_table(path: Path, required: Sequence[str]) -> Dict[str, Tuple[float, ...]]:
    rows = read_csv_dicts(path)
    if not rows:
        raise ValueError(f"{path} is empty")
    require_columns(path, rows[0].keys(), required)

    feature_columns = [name for name in rows[0].keys() if name != "cell_line"]
    if not feature_columns:
        raise ValueError(f"{path} must include at least one numeric feature column")

    records: Dict[str, Tuple[float, ...]] = {}
    for row in rows:
        cell_line = row["cell_line"].strip()
        if cell_line in records:
            raise ValueError(f"{path} has duplicate cell_line: {cell_line}")
        records[cell_line] = tuple(parse_float(row[column], column, path) for column in feature_columns)
    return records


def validate_bundle(
    samples: Sequence[SampleRecord],
    drugs: Dict[str, DrugRecord],
    dualsyn_cells: Dict[str, Tuple[float, ...]],
    mtl_cells: Dict[str, Tuple[float, ...]],
    mvc_exp_cells: Dict[str, Tuple[float, ...]],
    mvc_cn_cells: Dict[str, Tuple[float, ...]],
) -> None:
    missing_drugs = set()
    missing_cells = defaultdict(set)
    for sample in samples:
        for drug_name in (sample.drug_a_name, sample.drug_b_name):
            if drug_name not in drugs:
                missing_drugs.add(drug_name)
        if sample.cell_line not in dualsyn_cells:
            missing_cells["cells_dualsyn.csv"].add(sample.cell_line)
        if sample.cell_line not in mtl_cells:
            missing_cells["cells_mtl.csv"].add(sample.cell_line)
        if sample.cell_line not in mvc_exp_cells:
            missing_cells["cells_mvc_exp.csv"].add(sample.cell_line)
        if sample.cell_line not in mvc_cn_cells:
            missing_cells["cells_mvc_cn.csv"].add(sample.cell_line)

    problems: List[str] = []
    if missing_drugs:
        problems.append(f"missing drugs: {sorted(missing_drugs)[:10]}")
    for file_name, cell_names in missing_cells.items():
        if cell_names:
            problems.append(f"{file_name} missing cells: {sorted(cell_names)[:10]}")
    if problems:
        raise ValueError("Bundle validation failed: " + "; ".join(problems))


def unordered_pair_key(sample: SampleRecord) -> str:
    pair = sorted([sample.drug_a_name, sample.drug_b_name])
    return "|".join(pair)


def pair_cell_group_key(sample: SampleRecord) -> str:
    return "|".join([unordered_pair_key(sample), sample.cell_line])


def sample_group_key(sample: SampleRecord) -> str:
    return sample.sample_id


def build_entity_fold_map(names: Sequence[str], fold_count: int, seed: int) -> Dict[str, int]:
    ordered = sorted(set(names), key=lambda value: (stable_hash(f"{seed}|{value}"), value))
    return {name: index % fold_count for index, name in enumerate(ordered)}


def assign_groups_to_folds(groups: Dict[str, List[SampleRecord]], fold_count: int, seed: int) -> Dict[str, int]:
    ordered_groups = sorted(
        groups.items(),
        key=lambda item: (-len(item[1]), stable_hash(f"{seed}|{item[0]}"), item[0]),
    )
    fold_sizes = [0] * fold_count
    assignments: Dict[str, int] = {}
    for group_key, members in ordered_groups:
        target_fold = min(range(fold_count), key=lambda fold_idx: (fold_sizes[fold_idx], fold_idx))
        assignments[group_key] = target_fold
        fold_sizes[target_fold] += len(members)
    return assignments


def build_transductive_groups(
    samples: Sequence[SampleRecord],
    fold_strategy: str,
) -> Dict[str, List[SampleRecord]]:
    grouped: Dict[str, List[SampleRecord]] = defaultdict(list)
    for sample in samples:
        if fold_strategy == "pair_group":
            group_key = unordered_pair_key(sample)
        elif fold_strategy == "pair_cell_group":
            group_key = pair_cell_group_key(sample)
        elif fold_strategy == "sample_group":
            group_key = sample_group_key(sample)
        else:
            raise ValueError(f"Unsupported fold_strategy: {fold_strategy}")
        grouped[group_key].append(sample)
    return grouped


def build_protocol_assignments(
    samples: Sequence[SampleRecord],
    fold_count: int,
    seed: int,
    fold_strategy: str,
) -> List[Dict[str, object]]:
    grouped = build_transductive_groups(samples, fold_strategy)

    transductive_map = assign_groups_to_folds(grouped, fold_count, seed)
    cell_map = build_entity_fold_map([sample.cell_line for sample in samples], fold_count, seed + 17)
    drug_map = build_entity_fold_map(
        [sample.drug_a_name for sample in samples] + [sample.drug_b_name for sample in samples],
        fold_count,
        seed + 29,
    )

    assignments: List[Dict[str, object]] = []
    for sample in samples:
        if fold_strategy == "pair_group":
            transductive_group = unordered_pair_key(sample)
        elif fold_strategy == "pair_cell_group":
            transductive_group = pair_cell_group_key(sample)
        else:
            transductive_group = sample_group_key(sample)
        assignments.append(
            {
                "sample_id": sample.sample_id,
                "drug_a_name": sample.drug_a_name,
                "drug_b_name": sample.drug_b_name,
                "cell_line": sample.cell_line,
                "synergy_score": sample.synergy_score,
                "label": sample.label,
                "ri_row": sample.ri_row,
                "ri_col": sample.ri_col,
                "transductive_group": transductive_group,
                "transductive_fold": transductive_map[transductive_group],
                "cell_fold": cell_map[sample.cell_line],
                "drug_a_fold": drug_map[sample.drug_a_name],
                "drug_b_fold": drug_map[sample.drug_b_name],
            }
        )
    return assignments


def export_dualsyn(
    dataset_name: str,
    output_root: Path,
    assignments: Sequence[Dict[str, object]],
    drugs: Dict[str, DrugRecord],
    dualsyn_cells: Dict[str, Tuple[float, ...]],
    fold_count: int,
) -> None:
    data_root = output_root / dataset_name / "dualsyn" / "data"
    used_drugs = sorted({row["drug_a_name"] for row in assignments} | {row["drug_b_name"] for row in assignments})
    used_cells = sorted({row["cell_line"] for row in assignments})
    used_dim = len(dualsyn_cells[used_cells[0]]) if used_cells else 0

    write_csv(
        data_root / "smiles.csv",
        ["name", "smile"],
        ({"name": drug_name, "smile": drugs[drug_name].smiles} for drug_name in used_drugs),
    )

    cell_rows: List[List[object]] = []
    cell_rows.append(["gene_id"] + [f"feature_{index + 1}" for index in range(used_dim)])
    cell_rows.append(["transcript_id"] + [f"transcript_{index + 1}" for index in range(used_dim)])
    for cell_name in used_cells:
        cell_rows.append([cell_name] + list(dualsyn_cells[cell_name]))
    write_csv_rows(data_root / "cell_features_954.csv", cell_rows)

    for fold in range(fold_count):
        fold_dir = data_root / f"fold{fold}"
        train_rows = []
        test_rows = []
        for row in assignments:
            export_row = {
                "drug1": drugs[str(row["drug_a_name"])].smiles,
                "drug2": drugs[str(row["drug_b_name"])].smiles,
                "cell": row["cell_line"],
                "label": row["label"],
            }
            if row["transductive_fold"] == fold:
                test_rows.append(export_row)
            else:
                train_rows.append(export_row)
        write_csv(fold_dir / "train.csv", ["drug1", "drug2", "cell", "label"], train_rows)
        write_csv(fold_dir / "test.csv", ["drug1", "drug2", "cell", "label"], test_rows)


def export_mfsyndcp(
    dataset_name: str,
    output_root: Path,
    assignments: Sequence[Dict[str, object]],
    drugs: Dict[str, DrugRecord],
    dualsyn_cells: Dict[str, Tuple[float, ...]],
    fold_count: int,
) -> None:
    data_root = output_root / dataset_name / "mfsyndcp" / "data"
    used_drugs = sorted({row["drug_a_name"] for row in assignments} | {row["drug_b_name"] for row in assignments})
    used_cells = sorted({row["cell_line"] for row in assignments})
    used_dim = len(dualsyn_cells[used_cells[0]]) if used_cells else 0

    write_csv(
        data_root / "smiles.csv",
        ["name", "smile"],
        ({"name": drug_name, "smile": drugs[drug_name].smiles} for drug_name in used_drugs),
    )

    cell_rows: List[List[object]] = []
    cell_rows.append(["gene_id"] + [f"feature_{index + 1}" for index in range(used_dim)])
    cell_rows.append(["transcript_id"] + [f"transcript_{index + 1}" for index in range(used_dim)])
    for cell_name in used_cells:
        cell_rows.append([cell_name] + list(dualsyn_cells[cell_name]))
    write_csv_rows(data_root / "cell_features.csv", cell_rows)

    labels_rows = [
        {
            "drug1": drugs[str(row["drug_a_name"])].smiles,
            "drug2": drugs[str(row["drug_b_name"])].smiles,
            "cell": row["cell_line"],
            "label": row["label"],
        }
        for row in assignments
    ]
    write_csv(data_root / "labels.csv", ["drug1", "drug2", "cell", "label"], labels_rows)

    for fold in range(fold_count):
        fold_dir = data_root / "fold" / f"fold{fold}"
        train_rows = []
        test_rows = []
        for row in assignments:
            export_row = {
                "drug1": drugs[str(row["drug_a_name"])].smiles,
                "drug2": drugs[str(row["drug_b_name"])].smiles,
                "cell": row["cell_line"],
                "label": row["label"],
            }
            if row["transductive_fold"] == fold:
                test_rows.append(export_row)
            else:
                train_rows.append(export_row)
        write_csv(fold_dir / "train.csv", ["drug1", "drug2", "cell", "label"], train_rows)
        write_csv(fold_dir / "test.csv", ["drug1", "drug2", "cell", "label"], test_rows)


def export_mvcasyn(
    dataset_name: str,
    output_root: Path,
    assignments: Sequence[Dict[str, object]],
    drugs: Dict[str, DrugRecord],
    mvc_exp_cells: Dict[str, Tuple[float, ...]],
    mvc_cn_cells: Dict[str, Tuple[float, ...]],
    fold_count: int,
) -> None:
    data_root = output_root / dataset_name / "mvcasyn" / "data"
    used_drugs = sorted({row["drug_a_name"] for row in assignments} | {row["drug_b_name"] for row in assignments})
    used_cells = sorted({row["cell_line"] for row in assignments})

    write_csv(
        data_root / "oneil_drug_two_smiles.csv",
        ["drug_name", "smiles"],
        ({"drug_name": drug_name, "smiles": drugs[drug_name].smiles} for drug_name in used_drugs),
    )

    exp_dim = len(mvc_exp_cells[used_cells[0]]) if used_cells else 0
    cn_dim = len(mvc_cn_cells[used_cells[0]]) if used_cells else 0
    write_csv(
        data_root / "exp.csv",
        ["cell_line_name"] + [f"exp_{index + 1}" for index in range(exp_dim)],
        ({"cell_line_name": cell_name, **{f"exp_{i + 1}": value for i, value in enumerate(mvc_exp_cells[cell_name])}} for cell_name in used_cells),
    )
    write_csv(
        data_root / "cn.csv",
        ["cell_line_name"] + [f"cn_{index + 1}" for index in range(cn_dim)],
        ({"cell_line_name": cell_name, **{f"cn_{i + 1}": value for i, value in enumerate(mvc_cn_cells[cell_name])}} for cell_name in used_cells),
    )

    for fold in range(fold_count):
        fold_dir = data_root / "folds" / f"folds{fold}"
        train_rows = []
        test_rows = []
        for row in assignments:
            export_row = {
                "drug_a_name": row["drug_a_name"],
                "drug_b_name": row["drug_b_name"],
                "cell_line": row["cell_line"],
                "synergy": row["synergy_score"],
                "label": row["label"],
            }
            if row["transductive_fold"] == fold:
                test_rows.append(export_row)
            else:
                train_rows.append(export_row)
        write_csv(
            fold_dir / "train.csv",
            ["drug_a_name", "drug_b_name", "cell_line", "synergy", "label"],
            train_rows,
        )
        write_csv(
            fold_dir / "test.csv",
            ["drug_a_name", "drug_b_name", "cell_line", "synergy", "label"],
            test_rows,
        )


def export_mtlsynergy(
    dataset_name: str,
    output_root: Path,
    assignments: Sequence[Dict[str, object]],
    drugs: Dict[str, DrugRecord],
    mtl_cells: Dict[str, Tuple[float, ...]],
) -> None:
    data_root = output_root / dataset_name / "mtlsynergy" / "data"
    used_drugs = sorted({row["drug_a_name"] for row in assignments} | {row["drug_b_name"] for row in assignments})
    used_cells = sorted({row["cell_line"] for row in assignments})

    drug_index = {drug_name: index for index, drug_name in enumerate(used_drugs)}
    cell_index = {cell_name: index for index, cell_name in enumerate(used_cells)}

    write_csv(
        data_root / "drugs.csv",
        ["id", "name", "synonyms", "from_oneil"],
        (
            {
                "id": drug_index[drug_name],
                "name": drug_name,
                "synonyms": drugs[drug_name].synonyms,
                "from_oneil": "Yes",
            }
            for drug_name in used_drugs
        ),
    )

    drug_dim = len(drugs[used_drugs[0]].feature_values) if used_drugs else 0
    write_csv(
        data_root / "drug_features.csv",
        [str(index) for index in range(drug_dim)],
        ({str(index): value for index, value in enumerate(drugs[drug_name].feature_values)} for drug_name in used_drugs),
    )

    write_csv(
        data_root / "cell_lines.csv",
        ["id", "name", "synonyms", "from_oneil"],
        (
            {
                "id": cell_index[cell_name],
                "name": cell_name,
                "synonyms": cell_name,
                "from_oneil": "Yes",
            }
            for cell_name in used_cells
        ),
    )

    cell_dim = len(mtl_cells[used_cells[0]]) if used_cells else 0
    write_csv(
        data_root / "cell_line_features.csv",
        [str(index) for index in range(cell_dim)],
        ({str(index): value for index, value in enumerate(mtl_cells[cell_name])} for cell_name in used_cells),
    )

    summary_rows = []
    leave_cell_rows = []
    for row in assignments:
        summary_row = {
            "drug_row_idx": drug_index[str(row["drug_a_name"])],
            "drug_col_idx": drug_index[str(row["drug_b_name"])],
            "cell_line_idx": cell_index[str(row["cell_line"])],
            "ri_row": row["ri_row"],
            "ri_col": row["ri_col"],
            "synergy_loewe": row["synergy_score"],
            "syn_fold": row["transductive_fold"],
            "sen_fold_1": row["drug_a_fold"],
            "sen_fold_2": row["drug_b_fold"],
        }
        summary_rows.append(summary_row)
        leave_cell_rows.append({**summary_row, "fold": row["cell_fold"]})

    summary_header = [
        "drug_row_idx",
        "drug_col_idx",
        "cell_line_idx",
        "ri_row",
        "ri_col",
        "synergy_loewe",
        "syn_fold",
        "sen_fold_1",
        "sen_fold_2",
    ]
    leave_cell_header = summary_header + ["fold"]
    write_csv(data_root / "oneil_summary_idx.csv", summary_header, summary_rows)
    write_csv(data_root / "oneil_summary_idx_original_backup.csv", leave_cell_header, leave_cell_rows)
    write_csv(data_root / "oneil_summary_idx_leave_cell.csv", leave_cell_header, leave_cell_rows)


def build_manifest(
    dataset_name: str,
    assignments: Sequence[Dict[str, object]],
    drugs: Dict[str, DrugRecord],
    dualsyn_cells: Dict[str, Tuple[float, ...]],
    mtl_cells: Dict[str, Tuple[float, ...]],
    mvc_exp_cells: Dict[str, Tuple[float, ...]],
    mvc_cn_cells: Dict[str, Tuple[float, ...]],
    fold_count: int,
    label_source: str,
    label_threshold: float,
    default_ri: float,
    seed: int,
    fold_strategy: str,
) -> Dict[str, object]:
    label_counter = Counter(int(row["label"]) for row in assignments)
    fold_counter = Counter(int(row["transductive_fold"]) for row in assignments)
    used_drugs = sorted({str(row["drug_a_name"]) for row in assignments} | {str(row["drug_b_name"]) for row in assignments})
    used_cells = sorted({str(row["cell_line"]) for row in assignments})

    return {
        "dataset_name": dataset_name,
        "sample_count": len(assignments),
        "drug_count": len(used_drugs),
        "cell_count": len(used_cells),
        "fold_count": fold_count,
        "fold_strategy": fold_strategy,
        "seed": seed,
        "label_source": label_source,
        "label_threshold": label_threshold,
        "default_ri": default_ri,
        "class_distribution": {str(key): value for key, value in sorted(label_counter.items())},
        "transductive_fold_sizes": {str(key): value for key, value in sorted(fold_counter.items())},
        "feature_dimensions": {
            "drug_mtlsynergy": len(next(iter(drugs.values())).feature_values) if drugs else 0,
            "cell_dualsyn": len(next(iter(dualsyn_cells.values()))) if dualsyn_cells else 0,
            "cell_mtlsynergy": len(next(iter(mtl_cells.values()))) if mtl_cells else 0,
            "cell_mvc_exp": len(next(iter(mvc_exp_cells.values()))) if mvc_exp_cells else 0,
            "cell_mvc_cn": len(next(iter(mvc_cn_cells.values()))) if mvc_cn_cells else 0,
        },
        "exports": ["dualsyn", "mfsyndcp", "mvcasyn", "mtlsynergy"],
        "notes": [
            "transductive_fold is shared across all four models for fair comparison",
            "pair_group keeps the same unordered drug pair in one fold, which is the recommended thesis protocol",
            "pair_cell_group keeps the same unordered drug pair plus cell line in one fold",
            "sample_group is a random sample-level split and is the loosest protocol",
            "MTLSynergy ri_row and ri_col come from input samples.csv or the configured default_ri",
            "MTLSynergy leave-cell files are exported separately with fold=cell_fold",
        ],
    }
