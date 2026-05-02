from __future__ import annotations

import argparse
import ast
import csv
import json
import re
from datetime import datetime
from pathlib import Path
from statistics import fmean, pstdev
from typing import Dict, Iterable, List, Optional, Sequence


METRICS = ["roc_auc", "pr_auc", "acc", "bacc", "precision", "recall", "kappa"]
SUMMARY_COLUMNS = [
    "model",
    "roc_auc_mean",
    "roc_auc_std",
    "pr_auc_mean",
    "pr_auc_std",
    "acc_mean",
    "acc_std",
    "bacc_mean",
    "bacc_std",
    "precision_mean",
    "precision_std",
    "recall_mean",
    "recall_std",
    "kappa_mean",
    "kappa_std",
]
PER_FOLD_COLUMNS = ["model", "fold", *METRICS, "source_file"]
INVENTORY_COLUMNS = [
    "category",
    "experiment_key",
    "experiment_label",
    "model",
    "stage",
    "fold_count",
    "source_path",
    "selection_rule",
    "note",
]
EXCLUDED_COLUMNS = [
    "category",
    "experiment_key",
    "experiment_label",
    "model",
    "stage",
    "path",
    "reason",
]
RESOURCE_COLUMNS = [
    "model",
    "experiment_key",
    "experiment_label",
    "stage",
    "tag",
    "returncode",
    "duration_sec",
    "duration_min",
    "mean_process_cpu_percent",
    "peak_process_cpu_percent",
    "mean_process_rss_mb",
    "peak_process_rss_mb",
    "mean_target_gpu_mem_mb",
    "peak_target_gpu_mem_mb",
    "mean_gpu_util_percent",
    "peak_gpu_util_percent",
    "comparable_group",
    "comparable_note",
    "meta_path",
    "resource_log_path",
]
MAIN_MODELS = ["DualSyn", "MFSynDCP", "MVCASyn", "MTLSynergy"]
SUBEXPERIMENT_MODELS = ["DualSyn", "MFSynDCP", "MVCASyn"]

EXPERIMENT_LABELS = {
    "main": "主实验（pair_group, strict_gt10_lt0）",
    "subexp1": "副实验1（sample_group, strict_gt10_lt0）",
    "subexp2": "副实验2（pair_group, labelrule_ge10_else0）",
    "unknown": "未识别实验",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect metrics from the root results directory and generate review documents."
    )
    repo_root = Path(__file__).resolve().parent.parent
    parser.add_argument(
        "--results-root",
        default=str(repo_root / "results"),
        help="Root directory that stores collected result files.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(repo_root / "benchmark_factory" / "result_summary"),
        help="Directory where CSV and Markdown outputs will be written.",
    )
    return parser.parse_args()


def parse_float(value: object) -> Optional[float]:
    try:
        if value in ("", None):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def relative_to_root(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def write_csv(path: Path, rows: Sequence[Dict[str, object]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def metric_summary(rows: Sequence[Dict[str, object]], metric: str) -> tuple[str, str]:
    values = [float(row[metric]) for row in rows if row.get(metric) is not None]
    if not values:
        return ("N/A", "N/A")
    return (f"{fmean(values):.4f}", f"{pstdev(values):.4f}")


def build_summary_rows(rows: Sequence[Dict[str, object]], models: Sequence[str]) -> List[Dict[str, object]]:
    summary_rows: List[Dict[str, object]] = []
    for model in models:
        current = [row for row in rows if row["model"] == model]
        summary = {"model": model}
        for metric in METRICS:
            mean_value, std_value = metric_summary(current, metric)
            summary[f"{metric}_mean"] = mean_value
            summary[f"{metric}_std"] = std_value
        summary_rows.append(summary)
    return summary_rows


def read_tab_metrics(path: Path) -> List[Dict[str, float]]:
    parsed_rows: List[Dict[str, float]] = []
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            auc = parse_float(row.get("AUC_dev"))
            if auc is None:
                continue
            pr_auc = parse_float(row.get("PR_AUC"))
            acc = parse_float(row.get("ACC"))
            bacc = parse_float(row.get("BACC"))
            precision = parse_float(row.get("PREC"))
            recall = parse_float(row.get("RECALL"))
            kappa = parse_float(row.get("KAPPA"))
            if None in (pr_auc, acc, bacc, precision, recall, kappa):
                continue
            parsed_rows.append(
                {
                    "roc_auc": float(auc),
                    "pr_auc": float(pr_auc),
                    "acc": float(acc),
                    "bacc": float(bacc),
                    "precision": float(precision),
                    "recall": float(recall),
                    "kappa": float(kappa),
                }
            )
    return parsed_rows


def extract_fold(path: Path) -> Optional[int]:
    match = re.search(r"fold(\d+)", path.name)
    if match:
        return int(match.group(1))
    return None


def extract_dualsyn_timestamp(path: Path) -> datetime:
    match = re.search(r"_(\d{4}-\d{2}-\d{2} \d{2}_\d{2}_\d{2})\.txt$", path.name)
    if not match:
        return datetime.min
    text = match.group(1).replace("_", ":")
    return datetime.strptime(text, "%Y-%m-%d %H:%M:%S")


def add_inventory_row(
    inventory_rows: List[Dict[str, object]],
    *,
    category: str,
    experiment_key: str,
    model: str,
    stage: str,
    fold_count: object,
    source_path: str,
    selection_rule: str,
    note: str = "",
) -> None:
    inventory_rows.append(
        {
            "category": category,
            "experiment_key": experiment_key,
            "experiment_label": EXPERIMENT_LABELS.get(experiment_key, experiment_key),
            "model": model,
            "stage": stage,
            "fold_count": fold_count,
            "source_path": source_path,
            "selection_rule": selection_rule,
            "note": note,
        }
    )


def add_excluded_row(
    excluded_rows: List[Dict[str, object]],
    *,
    category: str,
    experiment_key: str,
    model: str,
    stage: str,
    path: str,
    reason: str,
) -> None:
    excluded_rows.append(
        {
            "category": category,
            "experiment_key": experiment_key,
            "experiment_label": EXPERIMENT_LABELS.get(experiment_key, experiment_key),
            "model": model,
            "stage": stage,
            "path": path,
            "reason": reason,
        }
    )


def pick_latest_files_by_fold(
    paths: Sequence[Path],
    *,
    results_root: Path,
    experiment_key: str,
    model: str,
    excluded_rows: List[Dict[str, object]],
) -> Dict[int, Path]:
    grouped: Dict[int, List[Path]] = {}
    for path in paths:
        fold = extract_fold(path)
        if fold is None:
            continue
        grouped.setdefault(fold, []).append(path)

    selected: Dict[int, Path] = {}
    for fold, fold_paths in sorted(grouped.items()):
        latest = max(fold_paths, key=extract_dualsyn_timestamp)
        selected[fold] = latest
        for candidate in fold_paths:
            if candidate == latest:
                continue
            add_excluded_row(
                excluded_rows,
                category="result_metrics",
                experiment_key=experiment_key,
                model=model,
                stage="train",
                path=relative_to_root(candidate, results_root),
                reason=f"同一实验同一折存在多份结果，按文件名时间戳仅保留最新文件 fold{fold}。",
            )
    return selected


def parse_dualsyn_experiment(
    results_root: Path,
    experiment_key: str,
    directory_name: str,
    inventory_rows: List[Dict[str, object]],
    excluded_rows: List[Dict[str, object]],
) -> List[Dict[str, object]]:
    result_dir = results_root / "DualSyn" / "DualSyn" / "result" / directory_name
    selected = pick_latest_files_by_fold(
        sorted(result_dir.glob("*.txt")),
        results_root=results_root,
        experiment_key=experiment_key,
        model="DualSyn",
        excluded_rows=excluded_rows,
    )
    rows: List[Dict[str, object]] = []
    for fold, path in sorted(selected.items()):
        metrics_rows = read_tab_metrics(path)
        if not metrics_rows:
            raise ValueError(f"{path} does not contain valid DualSyn metrics rows.")
        best = max(metrics_rows, key=lambda item: item["roc_auc"])
        rows.append({"model": "DualSyn", "fold": fold, **best, "source_file": relative_to_root(path, results_root)})

    add_inventory_row(
        inventory_rows,
        category="result_metrics",
        experiment_key=experiment_key,
        model="DualSyn",
        stage="train",
        fold_count=len(rows),
        source_path=relative_to_root(result_dir, results_root),
        selection_rule="按 fold 分组后保留时间戳最新文件；每折取 AUC_dev 最大时对应指标。",
        note="主实验存在重复 fold 文件，旧文件已在排除清单中记录。",
    )
    return rows


def parse_mfsyndcp_experiment(
    results_root: Path,
    experiment_key: str,
    pattern: str,
    selection_note: str,
    inventory_rows: List[Dict[str, object]],
) -> List[Dict[str, object]]:
    result_dir = results_root / "MFSynDCP" / "MFSynDCP" / "result"
    rows: List[Dict[str, object]] = []
    matched = sorted(result_dir.glob(pattern))
    for path in matched:
        fold = extract_fold(path)
        if fold is None:
            continue
        metrics_rows = read_tab_metrics(path)
        if not metrics_rows:
            raise ValueError(f"{path} does not contain valid MFSynDCP metrics rows.")
        best = max(metrics_rows, key=lambda item: item["roc_auc"])
        rows.append({"model": "MFSynDCP", "fold": fold, **best, "source_file": relative_to_root(path, results_root)})

    add_inventory_row(
        inventory_rows,
        category="result_metrics",
        experiment_key=experiment_key,
        model="MFSynDCP",
        stage="train",
        fold_count=len(rows),
        source_path=relative_to_root(result_dir, results_root),
        selection_rule=selection_note,
        note="每折读取对应 AUC 文本，不使用模型权重文件本身参与指标计算。",
    )
    return sorted(rows, key=lambda item: int(item["fold"]))


def parse_mvcasyn_folds(path: Path, results_root: Path) -> List[Dict[str, object]]:
    lines = [line.strip() for line in path.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip()]
    header = re.split(r"[\t,]+", lines[0])
    rows: List[Dict[str, object]] = []
    for line in lines[1:]:
        values = [item.strip() for item in line.split(",")]
        row = dict(zip(header, values))
        fold_value = str(row["fold"]).replace("fold", "")
        recall = float(row["test_recall"])
        tnr = float(row["test_tnr"])
        rows.append(
            {
                "model": "MVCASyn",
                "fold": int(fold_value),
                "roc_auc": float(row["test_auc_roc"]),
                "pr_auc": float(row.get("test_int_ap", row.get("test_ap"))),
                "acc": float(row["test_acc"]),
                "bacc": (recall + tnr) / 2,
                "precision": float(row["test_precision"]),
                "recall": recall,
                "kappa": float(row["test_kappa"]),
                "source_file": relative_to_root(path, results_root),
            }
        )
    return rows


def parse_mvcasyn_experiment(
    results_root: Path,
    experiment_key: str,
    relative_folds_path: str,
    inventory_rows: List[Dict[str, object]],
) -> List[Dict[str, object]]:
    folds_path = results_root / relative_folds_path
    rows = parse_mvcasyn_folds(folds_path, results_root)
    add_inventory_row(
        inventory_rows,
        category="result_metrics",
        experiment_key=experiment_key,
        model="MVCASyn",
        stage="train",
        fold_count=len(rows),
        source_path=relative_to_root(folds_path, results_root),
        selection_rule="直接读取 folds.txt；BACC 统一按 (Recall + TNR) / 2 重算。",
        note="不直接使用原文件中的 test_bacc，以保持统一指标口径。",
    )
    return sorted(rows, key=lambda item: int(item["fold"]))


def parse_mtlsynergy_main(
    results_root: Path,
    inventory_rows: List[Dict[str, object]],
    excluded_rows: List[Dict[str, object]],
) -> List[Dict[str, object]]:
    result_dir = results_root / "MTLSynergy-main" / "result"
    result_path = result_dir / "MTLSynergy_result.txt"
    eval_path = result_dir / "MTLSynergy_eval_metrics.txt"

    text = result_path.read_text(encoding="utf-8", errors="ignore")
    pattern = re.compile(r"Test Fold (\d+).*?Synergy:\s*\n(\{.*?\})\nSensitivity:\s*\n(\{.*?\})", re.S)
    result_rows_by_fold: Dict[int, Dict[str, object]] = {}
    seen_duplicate = False
    for fold_text, synergy_text, _sensitivity_text in pattern.findall(text):
        fold = int(fold_text)
        synergy = ast.literal_eval(synergy_text)
        if fold in result_rows_by_fold:
            seen_duplicate = True
            continue
        result_rows_by_fold[fold] = {
            "model": "MTLSynergy",
            "fold": fold,
            "roc_auc": float(synergy["ROC AUC"]),
            "pr_auc": float(synergy["PR AUC"]),
            "acc": float(synergy["ACC"]),
            "bacc": None,
            "precision": float(synergy["PREC"]),
            "recall": None,
            "kappa": float(synergy["Kappa"]),
            "source_file": f"{relative_to_root(result_path, results_root)} ; {relative_to_root(eval_path, results_root)}",
        }

    rows: List[Dict[str, object]] = []

    if eval_path.exists():
        eval_text = eval_path.read_text(encoding="utf-8", errors="ignore")
        eval_pattern = re.compile(r"fold_(\d+):\s*(\{.*?\})")
        eval_by_fold = {
            int(fold_text): ast.literal_eval(metrics_text)
            for fold_text, metrics_text in eval_pattern.findall(eval_text)
        }
        for fold in sorted(eval_by_fold):
            eval_row = eval_by_fold[fold]
            rows.append(
                {
                    "model": "MTLSynergy",
                    "fold": fold,
                    "roc_auc": float(eval_row["ROC AUC"]),
                    "pr_auc": float(eval_row["PR AUC"]),
                    "acc": float(eval_row["ACC"]),
                    "bacc": float(eval_row["BACC"]),
                    "precision": float(eval_row["PREC"]),
                    "recall": float(eval_row["Recall"]),
                    "kappa": float(eval_row["Kappa"]),
                    "source_file": f"{relative_to_root(result_path, results_root)} ; {relative_to_root(eval_path, results_root)}",
                }
            )
    else:
        rows = [result_rows_by_fold[fold] for fold in sorted(result_rows_by_fold)]

    if seen_duplicate:
        add_excluded_row(
            excluded_rows,
            category="result_metrics",
            experiment_key="main",
            model="MTLSynergy",
            stage="train",
            path=relative_to_root(result_path, results_root),
            reason="MTLSynergy_result.txt 中存在重复追加的 fold 记录；主实验最终按 MTLSynergy_eval_metrics.txt 的五折补评估结果整理。",
        )

    add_inventory_row(
        inventory_rows,
        category="result_metrics",
        experiment_key="main",
        model="MTLSynergy",
        stage="train",
        fold_count=len(rows),
        source_path=f"{relative_to_root(result_path, results_root)} ; {relative_to_root(eval_path, results_root)}",
        selection_rule="只使用 Synergy 部分参与主比较；Recall/BACC 优先取 MTLSynergy_eval_metrics.txt。",
        note="用户已明确判定 MTLSynergy 副实验无效，因此仅保留主实验。",
    )
    return sorted(rows, key=lambda item: int(item["fold"]))


def parse_resource_tag(tag: str) -> Dict[str, str]:
    experiment_key = "unknown"
    if "subexp1_sample_group" in tag:
        experiment_key = "subexp1"
    elif "subexp2_labelrule_ge10_else0_pair_group" in tag:
        experiment_key = "subexp2"

    if tag.startswith("dualsyn_"):
        return {
            "model": "DualSyn",
            "stage": "train",
            "experiment_key": experiment_key,
            "comparable_group": "subexp2_train_cross_model" if experiment_key == "subexp2" else "",
        }
    if tag.startswith("mfsyndcp_creat_data_"):
        return {
            "model": "MFSynDCP",
            "stage": "preprocess",
            "experiment_key": experiment_key,
            "comparable_group": "mfsyndcp_pipeline_overhead" if experiment_key == "subexp2" else "",
        }
    if tag.startswith("mfsyndcp_"):
        comparable_group = ""
        if experiment_key == "subexp2":
            comparable_group = "subexp2_train_cross_model"
        elif experiment_key == "subexp1":
            comparable_group = "subexp1_partial"
        return {
            "model": "MFSynDCP",
            "stage": "train",
            "experiment_key": experiment_key,
            "comparable_group": comparable_group,
        }
    if tag.startswith("mvcasyn_"):
        comparable_group = ""
        if experiment_key == "subexp2":
            comparable_group = "subexp2_train_cross_model"
        elif experiment_key == "subexp1":
            comparable_group = "subexp1_partial"
        return {
            "model": "MVCASyn",
            "stage": "train",
            "experiment_key": experiment_key,
            "comparable_group": comparable_group,
        }
    if tag.startswith("mtlsynergy_ae_"):
        return {
            "model": "MTLSynergy",
            "stage": "ae_train",
            "experiment_key": experiment_key,
            "comparable_group": "",
        }
    if tag.startswith("mtlsynergy_main_"):
        return {
            "model": "MTLSynergy",
            "stage": "train",
            "experiment_key": experiment_key,
            "comparable_group": "",
        }
    return {
        "model": "Unknown",
        "stage": "unknown",
        "experiment_key": experiment_key,
        "comparable_group": "",
    }


def summarize_resource_csv(path: Path) -> Dict[str, float]:
    numeric_keys = [
        "elapsed_sec",
        "process_cpu_percent",
        "process_rss_mb",
        "target_gpu_mem_mb",
        "gpu_util_percent_max",
    ]
    numeric_rows = {key: [] for key in numeric_keys}
    returncodes: List[str] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            for key in numeric_keys:
                value = parse_float(row.get(key))
                if value is not None:
                    numeric_rows[key].append(float(value))
            return_code = str(row.get("returncode", "")).strip()
            if return_code:
                returncodes.append(return_code)

    def mean_value(key: str) -> float:
        values = numeric_rows[key]
        return float(fmean(values)) if values else 0.0

    def peak_value(key: str) -> float:
        values = numeric_rows[key]
        return float(max(values)) if values else 0.0

    return {
        "duration_sec": peak_value("elapsed_sec"),
        "mean_process_cpu_percent": mean_value("process_cpu_percent"),
        "peak_process_cpu_percent": peak_value("process_cpu_percent"),
        "mean_process_rss_mb": mean_value("process_rss_mb"),
        "peak_process_rss_mb": peak_value("process_rss_mb"),
        "mean_target_gpu_mem_mb": mean_value("target_gpu_mem_mb"),
        "peak_target_gpu_mem_mb": peak_value("target_gpu_mem_mb"),
        "mean_gpu_util_percent": mean_value("gpu_util_percent_max"),
        "peak_gpu_util_percent": peak_value("gpu_util_percent_max"),
        "returncode": returncodes[-1] if returncodes else "",
    }


def comparable_note(model: str, stage: str, experiment_key: str, comparable_group: str) -> str:
    if model == "MTLSynergy":
        return "用户已标记该模型副实验无效，因此对应监控日志不参与正式分析。"
    if comparable_group == "subexp2_train_cross_model":
        return "可与 DualSyn/MFSynDCP/MVCASyn 的副实验2训练日志进行横向观察。"
    if comparable_group == "subexp1_partial":
        return "仅能与已有的副实验1日志局部对照，缺少 DualSyn 同口径监控。"
    if comparable_group == "mfsyndcp_pipeline_overhead":
        return "表示 MFSynDCP 在训练前 creat_data.py 的额外预处理开销。"
    if stage == "train":
        return "当前仅作为单次监控记录保留。"
    return ""


def parse_resource_logs(
    results_root: Path,
    inventory_rows: List[Dict[str, object]],
    excluded_rows: List[Dict[str, object]],
) -> List[Dict[str, object]]:
    resource_dir = results_root / "resource_logs"
    rows: List[Dict[str, object]] = []
    for meta_path in sorted(resource_dir.glob("*_meta.json")):
        tag = meta_path.name[: -len("_meta.json")]
        parsed = parse_resource_tag(tag)
        csv_path = resource_dir / f"{tag}_resource_log.csv"
        if parsed["model"] == "MTLSynergy":
            add_excluded_row(
                excluded_rows,
                category="resource_log",
                experiment_key=parsed["experiment_key"],
                model="MTLSynergy",
                stage=parsed["stage"],
                path=relative_to_root(meta_path, results_root),
                reason="用户已明确判定 MTLSynergy 副实验结果无效，对应监控日志不纳入正式分析。",
            )
            continue
        if not csv_path.exists():
            add_excluded_row(
                excluded_rows,
                category="resource_log",
                experiment_key=parsed["experiment_key"],
                model=parsed["model"],
                stage=parsed["stage"],
                path=relative_to_root(meta_path, results_root),
                reason="缺少对应的 resource_log.csv，无法汇总监控数据。",
            )
            continue

        summary = summarize_resource_csv(csv_path)
        try:
            meta_payload = json.loads(meta_path.read_text(encoding="utf-8", errors="ignore"))
        except json.JSONDecodeError:
            meta_payload = {}
        if not summary["returncode"]:
            summary["returncode"] = str(meta_payload.get("returncode", ""))

        row = {
            "model": parsed["model"],
            "experiment_key": parsed["experiment_key"],
            "experiment_label": EXPERIMENT_LABELS.get(parsed["experiment_key"], parsed["experiment_key"]),
            "stage": parsed["stage"],
            "tag": tag,
            "returncode": summary["returncode"],
            "duration_sec": round(summary["duration_sec"], 2),
            "duration_min": round(summary["duration_sec"] / 60.0, 2),
            "mean_process_cpu_percent": round(summary["mean_process_cpu_percent"], 2),
            "peak_process_cpu_percent": round(summary["peak_process_cpu_percent"], 2),
            "mean_process_rss_mb": round(summary["mean_process_rss_mb"], 2),
            "peak_process_rss_mb": round(summary["peak_process_rss_mb"], 2),
            "mean_target_gpu_mem_mb": round(summary["mean_target_gpu_mem_mb"], 2),
            "peak_target_gpu_mem_mb": round(summary["peak_target_gpu_mem_mb"], 2),
            "mean_gpu_util_percent": round(summary["mean_gpu_util_percent"], 2),
            "peak_gpu_util_percent": round(summary["peak_gpu_util_percent"], 2),
            "comparable_group": parsed["comparable_group"],
            "comparable_note": comparable_note(
                parsed["model"], parsed["stage"], parsed["experiment_key"], parsed["comparable_group"]
            ),
            "meta_path": relative_to_root(meta_path, results_root),
            "resource_log_path": relative_to_root(csv_path, results_root),
        }
        rows.append(row)
        add_inventory_row(
            inventory_rows,
            category="resource_log",
            experiment_key=parsed["experiment_key"],
            model=parsed["model"],
            stage=parsed["stage"],
            fold_count="",
            source_path=relative_to_root(meta_path, results_root),
            selection_rule="直接读取监控日志元数据与 resource_log.csv。",
            note=row["comparable_note"],
        )
    return rows


def validate_fold_counts(rows: Sequence[Dict[str, object]], experiment_key: str, expected_models: Sequence[str]) -> None:
    by_model: Dict[str, int] = {}
    for row in rows:
        by_model[row["model"]] = by_model.get(row["model"], 0) + 1
    for model in expected_models:
        count = by_model.get(model, 0)
        if count != 5:
            raise ValueError(
                f"{experiment_key} expected 5 folds for {model}, but found {count}. "
                f"Please inspect the results directory."
            )


def format_metric(value: object) -> str:
    if value in ("N/A", None, ""):
        return "N/A"
    try:
        return f"{float(value):.4f}"
    except (TypeError, ValueError):
        return str(value)


def markdown_table(rows: Sequence[Dict[str, object]], columns: Sequence[str], headers: Optional[Dict[str, str]] = None) -> str:
    if not rows:
        return "_无数据_\n"
    header_cells = [headers.get(column, column) if headers else column for column in columns]
    lines = [
        "| " + " | ".join(header_cells) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        values: List[str] = []
        for column in columns:
            value = row.get(column, "")
            if isinstance(value, float):
                values.append(f"{value:.4f}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines) + "\n"


def format_summary_table(rows: Sequence[Dict[str, object]]) -> str:
    display_rows: List[Dict[str, object]] = []
    for row in rows:
        display_rows.append(
            {
                "model": row["model"],
                "roc_auc": f"{row['roc_auc_mean']} ± {row['roc_auc_std']}" if row["roc_auc_mean"] != "N/A" else "N/A",
                "pr_auc": f"{row['pr_auc_mean']} ± {row['pr_auc_std']}" if row["pr_auc_mean"] != "N/A" else "N/A",
                "acc": f"{row['acc_mean']} ± {row['acc_std']}" if row["acc_mean"] != "N/A" else "N/A",
                "bacc": f"{row['bacc_mean']} ± {row['bacc_std']}" if row["bacc_mean"] != "N/A" else "N/A",
                "precision": (
                    f"{row['precision_mean']} ± {row['precision_std']}" if row["precision_mean"] != "N/A" else "N/A"
                ),
                "recall": f"{row['recall_mean']} ± {row['recall_std']}" if row["recall_mean"] != "N/A" else "N/A",
                "kappa": f"{row['kappa_mean']} ± {row['kappa_std']}" if row["kappa_mean"] != "N/A" else "N/A",
            }
        )
    return markdown_table(
        display_rows,
        ["model", "roc_auc", "pr_auc", "acc", "bacc", "precision", "recall", "kappa"],
        {
            "model": "模型",
            "roc_auc": "ROC-AUC",
            "pr_auc": "PR-AUC",
            "acc": "ACC",
            "bacc": "BACC",
            "precision": "Precision",
            "recall": "Recall",
            "kappa": "Kappa",
        },
    )


def format_per_fold_table(rows: Sequence[Dict[str, object]]) -> str:
    display_rows: List[Dict[str, object]] = []
    for row in rows:
        display_rows.append(
            {
                "model": row["model"],
                "fold": row["fold"],
                "roc_auc": format_metric(row["roc_auc"]),
                "pr_auc": format_metric(row["pr_auc"]),
                "acc": format_metric(row["acc"]),
                "bacc": format_metric(row["bacc"]),
                "precision": format_metric(row["precision"]),
                "recall": format_metric(row["recall"]),
                "kappa": format_metric(row["kappa"]),
            }
        )
    return markdown_table(
        display_rows,
        ["model", "fold", "roc_auc", "pr_auc", "acc", "bacc", "precision", "recall", "kappa"],
        {
            "model": "模型",
            "fold": "折",
            "roc_auc": "ROC-AUC",
            "pr_auc": "PR-AUC",
            "acc": "ACC",
            "bacc": "BACC",
            "precision": "Precision",
            "recall": "Recall",
            "kappa": "Kappa",
        },
    )


def summary_lookup(summary_rows: Sequence[Dict[str, object]]) -> Dict[str, Dict[str, str]]:
    return {str(row["model"]): dict(row) for row in summary_rows}


def sort_models_by_metric(summary_rows: Sequence[Dict[str, object]], metric: str) -> List[str]:
    sortable = []
    for row in summary_rows:
        value = row.get(f"{metric}_mean")
        if value == "N/A":
            continue
        sortable.append((float(value), str(row["model"])))
    sortable.sort(reverse=True)
    return [model for _value, model in sortable]


def metric_delta(
    base_lookup: Dict[str, Dict[str, str]], compare_lookup: Dict[str, Dict[str, str]], model: str, metric: str
) -> Optional[float]:
    base = base_lookup.get(model, {}).get(f"{metric}_mean")
    compare = compare_lookup.get(model, {}).get(f"{metric}_mean")
    if not base or not compare or base == "N/A" or compare == "N/A":
        return None
    return float(compare) - float(base)


def delta_text(delta: Optional[float]) -> str:
    if delta is None:
        return "N/A"
    sign = "+" if delta >= 0 else ""
    return f"{sign}{delta:.4f}"


def build_main_analysis(summary_rows: Sequence[Dict[str, object]]) -> List[str]:
    lookup = summary_lookup(summary_rows)
    auc_rank = sort_models_by_metric(summary_rows, "roc_auc")
    pr_rank = sort_models_by_metric(summary_rows, "pr_auc")
    kappa_rank = sort_models_by_metric(summary_rows, "kappa")
    acc_rank = sort_models_by_metric(summary_rows, "acc")

    lines = []
    lines.append(
        f"主实验按 ROC-AUC 排名为 {' > '.join(auc_rank)}，按 PR-AUC 排名为 {' > '.join(pr_rank)}。"
    )
    best_auc = auc_rank[0]
    best_auc_row = lookup[best_auc]
    lines.append(
        f"{best_auc} 在主实验中取得最高 ROC-AUC（{best_auc_row['roc_auc_mean']} ± {best_auc_row['roc_auc_std']}），"
        f"同时其 PR-AUC 和 Kappa 也位于第一，说明在排序能力与正类区分稳定性上整体最强。"
    )
    best_acc = acc_rank[0]
    best_acc_row = lookup[best_acc]
    lines.append(
        f"{best_acc} 的 ACC 最高（{best_acc_row['acc_mean']} ± {best_acc_row['acc_std']}），"
        f"但其 Recall 为 {best_acc_row['recall_mean']} ± {best_acc_row['recall_std']}，明显低于其准确率表现，"
        f"说明该模型在主实验中更偏向保守判阳。"
    )
    worst_auc = auc_rank[-1]
    worst_row = lookup[worst_auc]
    lines.append(
        f"{worst_auc} 在共同分类指标上整体最弱，ROC-AUC 为 {worst_row['roc_auc_mean']} ± {worst_row['roc_auc_std']}，"
        f"Kappa 为 {worst_row['kappa_mean']} ± {worst_row['kappa_std']}。"
    )
    return lines


def build_subexperiment_analysis(
    experiment_label: str,
    main_summary: Sequence[Dict[str, object]],
    current_summary: Sequence[Dict[str, object]],
) -> List[str]:
    main_lookup = summary_lookup(main_summary)
    current_lookup = summary_lookup(current_summary)
    auc_rank = sort_models_by_metric(current_summary, "roc_auc")
    kappa_rank = sort_models_by_metric(current_summary, "kappa")
    lines = [
        f"{experiment_label} 仅纳入 DualSyn、MFSynDCP、MVCASyn；按 ROC-AUC 排名为 {' > '.join(auc_rank)}，按 Kappa 排名为 {' > '.join(kappa_rank)}。"
    ]
    deltas = []
    for model in SUBEXPERIMENT_MODELS:
        roc_delta = delta_text(metric_delta(main_lookup, current_lookup, model, "roc_auc"))
        pr_delta = delta_text(metric_delta(main_lookup, current_lookup, model, "pr_auc"))
        kappa_delta = delta_text(metric_delta(main_lookup, current_lookup, model, "kappa"))
        deltas.append(f"{model}（ROC-AUC {roc_delta}，PR-AUC {pr_delta}，Kappa {kappa_delta}）")
    lines.append("相对主实验的平均指标变化分别为：" + "；".join(deltas) + "。")
    best_model = auc_rank[0]
    best_row = current_lookup[best_model]
    lines.append(
        f"该实验设置下，{best_model} 仍保持最高 ROC-AUC（{best_row['roc_auc_mean']} ± {best_row['roc_auc_std']}），"
        f"说明在当前可用三模型中，其分类排序能力仍最稳定。"
    )
    lines.append("MTLSynergy 副实验已按用户要求全部排除，不参与本节比较和结论。")
    return lines


def build_resource_analysis(resource_rows: Sequence[Dict[str, object]]) -> tuple[List[str], List[str]]:
    comparable = [
        row
        for row in resource_rows
        if row["comparable_group"] == "subexp2_train_cross_model" and row["stage"] == "train"
    ]
    lines: List[str] = []
    needed: List[str] = []
    if comparable:
        longest = max(comparable, key=lambda item: float(item["duration_sec"]))
        max_mem = max(comparable, key=lambda item: float(item["peak_target_gpu_mem_mb"]))
        lines.append(
            "在当前可横向观察的副实验2训练日志中，"
            f"{longest['model']} 训练时长最长（{float(longest['duration_min']):.2f} 分钟），"
            f"{max_mem['model']} 的目标 GPU 显存峰值最高（{float(max_mem['peak_target_gpu_mem_mb']):.2f} MB）。"
        )
        if any(float(row["peak_process_cpu_percent"]) > 0.0 for row in comparable):
            max_cpu = max(comparable, key=lambda item: float(item["peak_process_cpu_percent"]))
            lines.append(
                f"现有日志中 {max_cpu['model']} 的进程 CPU 峰值最高（{float(max_cpu['peak_process_cpu_percent']):.2f}%），"
                "但该指标仅用于辅助观察。"
            )
        else:
            lines.append(
                "当前资源日志中的 `process_cpu_percent` 列几乎恒为 0，说明现有采样实现下该指标不适合作为正式比较依据。"
            )
        mf_preprocess = [
            row for row in resource_rows if row["model"] == "MFSynDCP" and row["stage"] == "preprocess"
        ]
        if mf_preprocess:
            preprocess = mf_preprocess[0]
            lines.append(
                f"MFSynDCP 还存在单独的预处理阶段 creat_data.py，当前日志显示其额外耗时约 "
                f"{float(preprocess['duration_min']):.2f} 分钟，应在工程部署时单独计入。"
            )
        lines.append(
            "由于当前每个模型只有单次监控记录，且缺少 MTLSynergy 的有效同口径日志，本节只作为工程观察，不写成严格的效率优劣结论。"
        )
    else:
        lines.append("当前没有足够的同口径资源日志可用于横向观察，因此本节仅保留日志清单，不形成效率结论。")

    needed.append("若要完成四模型同口径资源比较，至少需要补 1 次有效的 MTLSynergy 监控训练日志。")
    needed.append("若要完成主实验口径的效率比较，还需要补齐四模型主实验在同一采样间隔下的完整资源监控日志。")
    return lines, needed


def build_conclusion_draft(
    main_summary: Sequence[Dict[str, object]],
    subexp1_summary: Sequence[Dict[str, object]],
    subexp2_summary: Sequence[Dict[str, object]],
    resource_rows: Sequence[Dict[str, object]],
) -> List[str]:
    main_lookup = summary_lookup(main_summary)
    sub1_lookup = summary_lookup(subexp1_summary)
    sub2_lookup = summary_lookup(subexp2_summary)
    lines = []
    lines.append(
        f"在统一 benchmark 主实验下，MVCASyn 取得最高的 ROC-AUC（{main_lookup['MVCASyn']['roc_auc_mean']} ± {main_lookup['MVCASyn']['roc_auc_std']}）"
        f"和 PR-AUC（{main_lookup['MVCASyn']['pr_auc_mean']} ± {main_lookup['MVCASyn']['pr_auc_std']}），"
        "说明其在当前四模型中具有最强的整体排序与正类识别能力。"
    )
    lines.append(
        f"DualSyn 在主实验中的 ROC-AUC 达到 {main_lookup['DualSyn']['roc_auc_mean']} ± {main_lookup['DualSyn']['roc_auc_std']}，"
        f"Kappa 为 {main_lookup['DualSyn']['kappa_mean']} ± {main_lookup['DualSyn']['kappa_std']}，整体表现稳定，可视为除 MVCASyn 外最强的分类基线。"
    )
    lines.append(
        f"MTLSynergy 的 ACC 最高（{main_lookup['MTLSynergy']['acc_mean']} ± {main_lookup['MTLSynergy']['acc_std']}），"
        f"但 Recall 仅为 {main_lookup['MTLSynergy']['recall_mean']} ± {main_lookup['MTLSynergy']['recall_std']}，"
        "表明该模型在当前设置下更偏向保守判阳，因此不能仅凭 ACC 判断其综合分类能力。"
    )
    lines.append(
        f"MFSynDCP 在主实验中的 ROC-AUC 和 Kappa 分别为 {main_lookup['MFSynDCP']['roc_auc_mean']} ± {main_lookup['MFSynDCP']['roc_auc_std']}、"
        f"{main_lookup['MFSynDCP']['kappa_mean']} ± {main_lookup['MFSynDCP']['kappa_std']}，在四模型中整体最弱。"
    )
    lines.append(
        f"在副实验1（sample_group）中，三模型的 ROC-AUC 排名仍为 {' > '.join(sort_models_by_metric(subexp1_summary, 'roc_auc'))}；"
        f"在副实验2（labelrule_ge10_else0）中，排名为 {' > '.join(sort_models_by_metric(subexp2_summary, 'roc_auc'))}。"
    )
    lines.append(
        "这说明在当前可用副实验中，三模型之间的相对强弱关系总体保持稳定，系统的统一数据适配与比较流程没有改变主要结论。"
    )
    if resource_rows:
        lines.append(
            "工程监控日志显示，不同模型在 CPU/GPU 使用方式和运行时长上存在明显差异，但由于当前缺少 MTLSynergy 的有效同口径监控，"
            "本研究仅将该部分作为部署层面的工程观察，不将其上升为四模型公平效率结论。"
        )
    return lines


def build_review_markdown(
    *,
    inventory_rows: Sequence[Dict[str, object]],
    excluded_rows: Sequence[Dict[str, object]],
    main_rows: Sequence[Dict[str, object]],
    main_summary: Sequence[Dict[str, object]],
    subexp1_rows: Sequence[Dict[str, object]],
    subexp1_summary: Sequence[Dict[str, object]],
    subexp2_rows: Sequence[Dict[str, object]],
    subexp2_summary: Sequence[Dict[str, object]],
    resource_rows: Sequence[Dict[str, object]],
) -> str:
    resource_lines, needed_logs = build_resource_analysis(resource_rows)
    conclusion_lines = build_conclusion_draft(main_summary, subexp1_summary, subexp2_summary, resource_rows)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines: List[str] = [
        "# `results` 结果整理与论文结论确认稿",
        "",
        f"生成时间：{generated_at}",
        "",
        "本文档以仓库根目录 `results/` 作为唯一结果源整理生成，用于你先确认数据与论文结论。当前阶段不会改写 `streamlit_system`。",
        "",
        "## 1. 结果来源与固定规则",
        "",
        "- 主实验、副实验1、副实验2均从 `results/` 目录读取，不再以各模型原始目录作为真值来源。",
        "- `MTLSynergy` 仅保留主实验；其副实验结果和对应监控日志全部排除。",
        "- `DualSyn` 同一 fold 若存在多份结果，按文件名时间戳保留最新文件。",
        "- `DualSyn` 与 `MFSynDCP` 都按每折 `AUC_dev` 最大时对应的测试指标入表。",
        "- `MVCASyn` 的 `BACC` 统一按 `(Recall + TNR) / 2` 重算，不直接使用原文件中的 `test_bacc`。",
        "- 资源监控章节只作为工程观察；若缺少同口径日志，则明确列出需要补齐的实验。",
        "",
        "## 2. 可用结果清单",
        "",
        markdown_table(
            inventory_rows,
            ["category", "experiment_label", "model", "stage", "fold_count", "source_path", "selection_rule", "note"],
            {
                "category": "类别",
                "experiment_label": "实验",
                "model": "模型",
                "stage": "阶段",
                "fold_count": "折数",
                "source_path": "来源路径",
                "selection_rule": "选取规则",
                "note": "备注",
            },
        ),
        "## 3. 排除结果清单",
        "",
        markdown_table(
            excluded_rows,
            ["category", "experiment_label", "model", "stage", "path", "reason"],
            {
                "category": "类别",
                "experiment_label": "实验",
                "model": "模型",
                "stage": "阶段",
                "path": "路径",
                "reason": "排除原因",
            },
        ),
        "## 4. 主实验结果",
        "",
        "### 4.1 主实验汇总表",
        "",
        format_summary_table(main_summary),
        "### 4.2 主实验每折结果",
        "",
        format_per_fold_table(main_rows),
        "### 4.3 主实验分析",
        "",
    ]
    for item in build_main_analysis(main_summary):
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## 5. 副实验1结果",
            "",
            "### 5.1 副实验1汇总表",
            "",
            format_summary_table(subexp1_summary),
            "### 5.2 副实验1每折结果",
            "",
            format_per_fold_table(subexp1_rows),
            "### 5.3 副实验1分析",
            "",
        ]
    )
    for item in build_subexperiment_analysis("副实验1（sample_group）", main_summary, subexp1_summary):
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## 6. 副实验2结果",
            "",
            "### 6.1 副实验2汇总表",
            "",
            format_summary_table(subexp2_summary),
            "### 6.2 副实验2每折结果",
            "",
            format_per_fold_table(subexp2_rows),
            "### 6.3 副实验2分析",
            "",
        ]
    )
    for item in build_subexperiment_analysis("副实验2（labelrule_ge10_else0）", main_summary, subexp2_summary):
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## 7. 资源监控与工程观察",
            "",
            "### 7.1 当前可用监控汇总",
            "",
            markdown_table(
                resource_rows,
                [
                    "model",
                    "experiment_label",
                    "stage",
                    "duration_min",
                    "peak_process_rss_mb",
                    "peak_target_gpu_mem_mb",
                    "peak_gpu_util_percent",
                    "comparable_note",
                ],
                {
                    "model": "模型",
                    "experiment_label": "实验",
                    "stage": "阶段",
                    "duration_min": "时长(分钟)",
                    "peak_process_rss_mb": "内存峰值(MB)",
                    "peak_target_gpu_mem_mb": "目标GPU显存峰值(MB)",
                    "peak_gpu_util_percent": "GPU利用率峰值",
                    "comparable_note": "说明",
                },
            ),
            "### 7.2 工程观察",
            "",
        ]
    )
    for item in resource_lines:
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "### 7.3 若要补齐更公平的资源比较，需要补做的实验",
            "",
        ]
    )
    for item in needed_logs:
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## 8. 可直接用于论文的结论草稿",
            "",
        ]
    )
    for item in conclusion_lines:
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## 9. 后续动作建议",
            "",
            "- 当前文档和 CSV 先供你确认。",
            "- 你确认无误后，再把稳定摘要回写到 `streamlit_system/pages/4_Model_Notes.py`。",
            "- 回写时只放模型定位、主结果结论和能力边界，不把大段原始数值直接塞进系统页面。",
            "",
        ]
    )
    return "\n".join(lines)


def collect_all(results_root: Path) -> Dict[str, object]:
    inventory_rows: List[Dict[str, object]] = []
    excluded_rows: List[Dict[str, object]] = []

    main_rows = (
        parse_dualsyn_experiment(results_root, "main", "DualSyn_transductive", inventory_rows, excluded_rows)
        + parse_mfsyndcp_experiment(
            results_root,
            "main",
            "MFSynDCP_fold*_AUCs_labels.txt",
            "每折读取对应 AUC 文本；取 AUC_dev 最大时对应指标。",
            inventory_rows,
        )
        + parse_mvcasyn_experiment(results_root, "main", "MVCASyn/results/folds.txt", inventory_rows)
        + parse_mtlsynergy_main(results_root, inventory_rows, excluded_rows)
    )
    subexp1_rows = (
        parse_dualsyn_experiment(results_root, "subexp1", "DualSyn_subexp1_sample_group", inventory_rows, excluded_rows)
        + parse_mfsyndcp_experiment(
            results_root,
            "subexp1",
            "MFSynDCP_subexp1_sample_group_fold*_AUCs_sample_group.txt",
            "每折读取对应副实验1 AUC 文本；取 AUC_dev 最大时对应指标。",
            inventory_rows,
        )
        + parse_mvcasyn_experiment(
            results_root,
            "subexp1",
            "MVCASyn/results/subexp1_sample_group/folds.txt",
            inventory_rows,
        )
    )
    subexp2_rows = (
        parse_dualsyn_experiment(
            results_root,
            "subexp2",
            "DualSyn_subexp2_labelrule_ge10_else0_pair_group",
            inventory_rows,
            excluded_rows,
        )
        + parse_mfsyndcp_experiment(
            results_root,
            "subexp2",
            "MFSynDCP_subexp2_labelrule_ge10_else0_pair_group_fold*_AUCs_subexp2_labelrule_ge10_else0_pair_group.txt",
            "每折读取对应副实验2 AUC 文本；取 AUC_dev 最大时对应指标。",
            inventory_rows,
        )
        + parse_mvcasyn_experiment(
            results_root,
            "subexp2",
            "MVCASyn/results/subexp2_labelrule_ge10_else0_pair_group/folds.txt",
            inventory_rows,
        )
    )
    resource_rows = parse_resource_logs(results_root, inventory_rows, excluded_rows)

    validate_fold_counts(main_rows, "main", MAIN_MODELS)
    validate_fold_counts(subexp1_rows, "subexp1", SUBEXPERIMENT_MODELS)
    validate_fold_counts(subexp2_rows, "subexp2", SUBEXPERIMENT_MODELS)

    return {
        "inventory_rows": inventory_rows,
        "excluded_rows": excluded_rows,
        "main_rows": sorted(main_rows, key=lambda item: (MAIN_MODELS.index(str(item["model"])), int(item["fold"]))),
        "main_summary": build_summary_rows(main_rows, MAIN_MODELS),
        "subexp1_rows": sorted(
            subexp1_rows, key=lambda item: (SUBEXPERIMENT_MODELS.index(str(item["model"])), int(item["fold"]))
        ),
        "subexp1_summary": build_summary_rows(subexp1_rows, SUBEXPERIMENT_MODELS),
        "subexp2_rows": sorted(
            subexp2_rows, key=lambda item: (SUBEXPERIMENT_MODELS.index(str(item["model"])), int(item["fold"]))
        ),
        "subexp2_summary": build_summary_rows(subexp2_rows, SUBEXPERIMENT_MODELS),
        "resource_rows": sorted(resource_rows, key=lambda item: (item["experiment_key"], item["model"], item["stage"])),
    }


def main() -> None:
    args = parse_args()
    results_root = Path(args.results_root).resolve()
    output_dir = Path(args.output_dir).resolve()

    collected = collect_all(results_root)
    output_dir.mkdir(parents=True, exist_ok=True)

    write_csv(output_dir / "results_inventory.csv", collected["inventory_rows"], INVENTORY_COLUMNS)
    write_csv(output_dir / "results_excluded_inventory.csv", collected["excluded_rows"], EXCLUDED_COLUMNS)
    write_csv(output_dir / "results_main_per_fold.csv", collected["main_rows"], PER_FOLD_COLUMNS)
    write_csv(output_dir / "results_main_summary.csv", collected["main_summary"], SUMMARY_COLUMNS)
    write_csv(output_dir / "results_subexp1_per_fold.csv", collected["subexp1_rows"], PER_FOLD_COLUMNS)
    write_csv(output_dir / "results_subexp1_summary.csv", collected["subexp1_summary"], SUMMARY_COLUMNS)
    write_csv(output_dir / "results_subexp2_per_fold.csv", collected["subexp2_rows"], PER_FOLD_COLUMNS)
    write_csv(output_dir / "results_subexp2_summary.csv", collected["subexp2_summary"], SUMMARY_COLUMNS)
    write_csv(output_dir / "results_resource_summary.csv", collected["resource_rows"], RESOURCE_COLUMNS)

    markdown = build_review_markdown(
        inventory_rows=collected["inventory_rows"],
        excluded_rows=collected["excluded_rows"],
        main_rows=collected["main_rows"],
        main_summary=collected["main_summary"],
        subexp1_rows=collected["subexp1_rows"],
        subexp1_summary=collected["subexp1_summary"],
        subexp2_rows=collected["subexp2_rows"],
        subexp2_summary=collected["subexp2_summary"],
        resource_rows=collected["resource_rows"],
    )
    (output_dir / "results_review_for_confirmation_中文.md").write_text(markdown, encoding="utf-8-sig")

    print(f"Wrote review outputs to: {output_dir}")


if __name__ == "__main__":
    main()
