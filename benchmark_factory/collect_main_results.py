from __future__ import annotations

import ast
import csv
import re
from pathlib import Path
from statistics import fmean, pstdev
from typing import Dict, Iterable, List, Optional


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


def parse_float(value: object) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def metric_summary(rows: List[Dict[str, object]], metric: str) -> tuple[str, str]:
    values = [float(row[metric]) for row in rows if row.get(metric) is not None]
    if not values:
        return ("N/A", "N/A")
    return (f"{fmean(values):.4f}", f"{pstdev(values):.4f}")


def read_tab_metrics(path: Path) -> List[Dict[str, float]]:
    parsed_rows: List[Dict[str, float]] = []
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            auc = parse_float(row.get("AUC_dev"))
            if auc is None:
                continue
            parsed_rows.append(
                {
                    "roc_auc": auc,
                    "pr_auc": float(row["PR_AUC"]),
                    "acc": float(row["ACC"]),
                    "bacc": float(row["BACC"]),
                    "precision": float(row["PREC"]),
                    "recall": float(row["RECALL"]),
                    "kappa": float(row["KAPPA"]),
                }
            )
    return parsed_rows


def parse_dualsyn(repo_root: Path) -> List[Dict[str, object]]:
    result_dir = repo_root / "DualSyn" / "DualSyn" / "result" / "DualSyn_transductive"
    rows: List[Dict[str, object]] = []
    for path in sorted(result_dir.glob("*.txt")):
        fold_match = re.search(r"fold(\d+)", path.name)
        if not fold_match:
            continue
        metrics_rows = read_tab_metrics(path)
        if not metrics_rows:
            continue
        best = max(metrics_rows, key=lambda item: item["roc_auc"])
        rows.append({"model": "DualSyn", "fold": int(fold_match.group(1)), **best})
    return rows


def parse_mfsyndcp(repo_root: Path) -> List[Dict[str, object]]:
    result_dir = repo_root / "MFSynDCP" / "MFSynDCP" / "result"
    rows: List[Dict[str, object]] = []
    for path in sorted(result_dir.glob("MFSynDCP_fold*_AUCs_labels.txt")):
        fold_match = re.search(r"fold(\d+)", path.name)
        if not fold_match:
            continue
        metrics_rows = read_tab_metrics(path)
        if not metrics_rows:
            continue
        best = max(metrics_rows, key=lambda item: item["roc_auc"])
        rows.append({"model": "MFSynDCP", "fold": int(fold_match.group(1)), **best})
    return rows


def parse_mvcasyn(repo_root: Path) -> List[Dict[str, object]]:
    result_path = repo_root / "MVCASyn" / "results" / "folds.txt"
    rows: List[Dict[str, object]] = []
    lines = [line.strip() for line in result_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    header = re.split(r"[\t,]+", lines[0])
    for line in lines[1:]:
        values = [item.strip() for item in line.split(",")]
        row = dict(zip(header, values))
        fold_value = str(row["fold"]).replace("fold", "")
        recall = float(row["test_recall"])
        tnr = float(row["test_tnr"])
        standard_bacc = (recall + tnr) / 2
        rows.append(
            {
                "model": "MVCASyn",
                "fold": int(fold_value),
                "roc_auc": float(row["test_auc_roc"]),
                "pr_auc": float(row["test_int_ap"]),
                "acc": float(row["test_acc"]),
                "bacc": standard_bacc,
                "precision": float(row["test_precision"]),
                "recall": recall,
                "kappa": float(row["test_kappa"]),
            }
        )
    return rows


def parse_mtlsynergy(repo_root: Path) -> tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    result_path = repo_root / "MTLSynergy" / "result" / "MTLSynergy_result.txt"
    eval_path = repo_root / "MTLSynergy" / "result" / "MTLSynergy_eval_metrics.txt"
    text = result_path.read_text(encoding="utf-8")
    pattern = re.compile(
        r"Test Fold (\d+).*?Synergy:\s*\n(\{.*?\})\nSensitivity:\s*\n(\{.*?\})",
        re.S,
    )
    synergy_rows: List[Dict[str, object]] = []
    sensitivity_rows: List[Dict[str, object]] = []
    for fold_text, synergy_text, sensitivity_text in pattern.findall(text):
        fold = int(fold_text)
        synergy = ast.literal_eval(synergy_text)
        sensitivity = ast.literal_eval(sensitivity_text)
        synergy_rows.append(
            {
                "model": "MTLSynergy",
                "fold": fold,
                "roc_auc": float(synergy["ROC AUC"]),
                "pr_auc": float(synergy["PR AUC"]),
                "acc": float(synergy["ACC"]),
                "bacc": None,
                "precision": float(synergy["PREC"]),
                "recall": None,
                "kappa": float(synergy["Kappa"]),
            }
        )
        sensitivity_rows.append(
            {
                "fold": fold,
                "mse": float(sensitivity["MSE"]),
                "rmse": float(sensitivity["RMSE"]),
                "pearsonr": float(sensitivity["Pearsonr"]),
                "cce": float(sensitivity["CCE"]),
                "roc_auc": float(sensitivity["ROC AUC"]),
                "pr_auc": float(sensitivity["PR AUC"]),
                "acc": float(sensitivity["ACC"]),
                "precision": float(sensitivity["PREC"]),
                "kappa": float(sensitivity["Kappa"]),
            }
        )
    if eval_path.exists():
        eval_text = eval_path.read_text(encoding="utf-8")
        eval_pattern = re.compile(r"fold_(\d+):\s*(\{.*?\})")
        eval_by_fold = {
            int(fold_text): ast.literal_eval(metrics_text)
            for fold_text, metrics_text in eval_pattern.findall(eval_text)
        }
        for row in synergy_rows:
            eval_row = eval_by_fold.get(int(row["fold"]))
            if not eval_row:
                continue
            row["bacc"] = float(eval_row["BACC"])
            row["recall"] = float(eval_row["Recall"])
    return synergy_rows, sensitivity_rows


def model_rows(rows: Iterable[Dict[str, object]], model: str) -> List[Dict[str, object]]:
    return [row for row in rows if row["model"] == model]


def write_csv(path: Path, rows: List[Dict[str, object]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_summary_rows(rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    summary_rows: List[Dict[str, object]] = []
    for model in ["DualSyn", "MFSynDCP", "MVCASyn", "MTLSynergy"]:
        current = model_rows(rows, model)
        summary = {"model": model}
        for metric in METRICS:
            mean, std = metric_summary(current, metric)
            summary[f"{metric}_mean"] = mean
            summary[f"{metric}_std"] = std
        summary_rows.append(summary)
    return summary_rows


def build_markdown(
    summary_rows: List[Dict[str, object]],
    per_fold_rows: List[Dict[str, object]],
    mtl_sensitivity_rows: List[Dict[str, object]],
) -> str:
    lines = [
        "# 四模型主实验结果汇总",
        "",
        "本文档根据四个模型当前目录下的结果文件自动整理生成。",
        "",
        "## 主结果表",
        "",
        "| 模型 | ROC-AUC | PR-AUC | ACC | BACC | Precision | Recall | Kappa |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    for row in summary_rows:
        def metric_cell(metric: str) -> str:
            mean = row[f"{metric}_mean"]
            std = row[f"{metric}_std"]
            if mean == "N/A":
                return "N/A"
            return f"{mean} ± {std}"

        lines.append(
            "| {model} | {roc_auc} | {pr_auc} | {acc} | {bacc} | {precision} | {recall} | {kappa} |".format(
                model=row["model"],
                roc_auc=metric_cell("roc_auc"),
                pr_auc=metric_cell("pr_auc"),
                acc=metric_cell("acc"),
                bacc=metric_cell("bacc"),
                precision=metric_cell("precision"),
                recall=metric_cell("recall"),
                kappa=metric_cell("kappa"),
            )
        )

    lines.extend(
        [
            "",
            "## 说明",
            "",
            "- `DualSyn` 和 `MFSynDCP` 取各折 `AUC_dev` 最大时对应的测试指标。",
            "- `MVCASyn` 直接读取 `results/folds.txt` 中的每折测试结果。",
            "- `MVCASyn` 的 `BACC` 已依据 `test_recall` 与 `test_tnr` 按标准公式 `(Recall + TNR) / 2` 重新计算，不再使用原文件中的 `test_bacc`。",
            "- `MTLSynergy` 只整理 `Synergy` 部分用于四模型主比较。",
            "- 若存在 `MTLSynergy/result/MTLSynergy_eval_metrics.txt`，则优先使用其中补算得到的 `Recall` 和 `BACC`。",
            "",
            "## MTLSynergy Sensitivity",
            "",
            "| 指标 | 均值 ± 标准差 |",
            "| --- | --- |",
        ]
    )

    for metric in ["mse", "rmse", "pearsonr", "cce", "roc_auc", "pr_auc", "acc", "precision", "kappa"]:
        values = [float(row[metric]) for row in mtl_sensitivity_rows]
        lines.append(f"| {metric} | {fmean(values):.4f} ± {pstdev(values):.4f} |")

    return "\n".join(lines) + "\n"


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    output_dir = repo_root / "benchmark_factory" / "result_summary"

    per_fold_rows = (
        parse_dualsyn(repo_root)
        + parse_mfsyndcp(repo_root)
        + parse_mvcasyn(repo_root)
    )
    mtl_synergy_rows, mtl_sensitivity_rows = parse_mtlsynergy(repo_root)
    per_fold_rows += mtl_synergy_rows

    per_fold_fieldnames = ["model", "fold", *METRICS]
    summary_rows = build_summary_rows(per_fold_rows)

    write_csv(output_dir / "main_experiment_per_fold.csv", per_fold_rows, per_fold_fieldnames)
    write_csv(output_dir / "main_experiment_summary.csv", summary_rows, SUMMARY_COLUMNS)
    write_csv(
        output_dir / "mtlsynergy_sensitivity_per_fold.csv",
        mtl_sensitivity_rows,
        ["fold", "mse", "rmse", "pearsonr", "cce", "roc_auc", "pr_auc", "acc", "precision", "kappa"],
    )
    markdown = build_markdown(summary_rows, per_fold_rows, mtl_sensitivity_rows)
    (output_dir / "main_experiment_summary.md").write_text(markdown, encoding="utf-8")

    print(f"wrote {output_dir}")


if __name__ == "__main__":
    main()
