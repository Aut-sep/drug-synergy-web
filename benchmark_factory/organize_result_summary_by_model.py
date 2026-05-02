from __future__ import annotations

import argparse
import csv
import shutil
from pathlib import Path
from typing import Dict, Iterable, List, Sequence


MODEL_ORDER = ["DualSyn", "MFSynDCP", "MVCASyn", "MTLSynergy"]
MODEL_DIRS = {
    "DualSyn": "01_DualSyn",
    "MFSynDCP": "02_MFSynDCP",
    "MVCASyn": "03_MVCASyn",
    "MTLSynergy": "04_MTLSynergy",
}
FILE_SPECS = [
    ("results_main_summary.csv", "01_main_summary.csv", "主实验均值汇总"),
    ("results_main_per_fold.csv", "02_main_per_fold.csv", "主实验逐折结果"),
    ("results_subexp1_summary.csv", "03_subexp1_summary.csv", "副实验1均值汇总"),
    ("results_subexp1_per_fold.csv", "04_subexp1_per_fold.csv", "副实验1逐折结果"),
    ("results_subexp2_summary.csv", "05_subexp2_summary.csv", "副实验2均值汇总"),
    ("results_subexp2_per_fold.csv", "06_subexp2_per_fold.csv", "副实验2逐折结果"),
    ("results_resource_summary.csv", "07_resource_summary.csv", "资源监控汇总"),
    ("results_inventory.csv", "08_inventory.csv", "纳入结果清单"),
    ("results_excluded_inventory.csv", "09_excluded_inventory.csv", "排除结果清单"),
]


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="Organize result_summary outputs into per-model folders.")
    parser.add_argument(
        "--result-summary-dir",
        default=str(repo_root / "benchmark_factory" / "result_summary"),
        help="Directory that stores the generated result summary CSV/Markdown files.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(repo_root / "benchmark_factory" / "result_summary" / "by_model"),
        help="Directory that will receive the per-model organized files.",
    )
    return parser.parse_args()


def read_csv_rows(path: Path) -> tuple[List[str], List[Dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv_rows(path: Path, fieldnames: Sequence[str], rows: Sequence[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def clear_output_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def model_status_lines(model: str, available_files: Sequence[tuple[str, str]]) -> List[str]:
    available_names = {target for target, _ in available_files}
    lines = [f"# {model}", ""]
    if model == "MTLSynergy":
        lines.extend(
            [
                "- 当前仅保留主实验结果。",
                "- 副实验结果与对应监控日志已按既定规则排除，不写入本文件夹。",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "- 当前文件夹已按模型拆分主实验、副实验与资源监控相关汇总文件。",
                "- 原始跨模型总表仍保留在 `benchmark_factory/result_summary/` 根目录，不受本整理影响。",
                "",
            ]
        )

    lines.append("## 已生成文件")
    lines.append("")
    if available_files:
        for target_name, description in available_files:
            lines.append(f"- `{target_name}`：{description}")
    else:
        lines.append("- 当前没有可写入的整理文件。")
    lines.append("")
    lines.append("## 缺失或排除说明")
    lines.append("")
    if model == "MTLSynergy":
        lines.append("- `03/04/05/06/07` 不生成，因为当前规则下没有可用的副实验与资源监控结果。")
    else:
        lines.append("- 若某个编号文件未出现，表示该模型在该类别下当前没有可用数据。")
    lines.append("")
    return lines


def build_top_level_readme(summary_dir: Path, output_dir: Path) -> str:
    lines = [
        "# 按模型整理后的结果目录",
        "",
        "本目录用于把 `benchmark_factory/result_summary/` 下的跨模型汇总文件，按模型重新拆分成更便于查看的结构。",
        "",
        "## 目录说明",
        "",
        "- `01_DualSyn`：DualSyn 对应的主实验、副实验、资源监控与纳排清单。",
        "- `02_MFSynDCP`：MFSynDCP 对应的主实验、副实验、资源监控与纳排清单。",
        "- `03_MVCASyn`：MVCASyn 对应的主实验、副实验、资源监控与纳排清单。",
        "- `04_MTLSynergy`：MTLSynergy 对应的主实验和纳排清单；副实验与监控数据按规则排除。",
        "",
        "## 生成来源",
        "",
        f"- 源目录：`{summary_dir.as_posix()}`",
        f"- 整理目录：`{output_dir.as_posix()}`",
        "",
        "## 文件编号规则",
        "",
        "- `01/02`：主实验",
        "- `03/04`：副实验1",
        "- `05/06`：副实验2",
        "- `07`：资源监控",
        "- `08`：纳入结果清单",
        "- `09`：排除结果清单",
        "",
    ]
    return "\n".join(lines)


def filter_rows_by_model(rows: Iterable[Dict[str, str]], model: str) -> List[Dict[str, str]]:
    return [row for row in rows if row.get("model") == model]


def main() -> None:
    args = parse_args()
    summary_dir = Path(args.result_summary_dir).resolve()
    output_dir = Path(args.output_dir).resolve()

    if not summary_dir.exists():
        raise SystemExit(f"Result summary directory not found: {summary_dir}")

    clear_output_dir(output_dir)

    source_payloads = {}
    for source_name, target_name, description in FILE_SPECS:
        source_path = summary_dir / source_name
        if not source_path.exists():
            continue
        fieldnames, rows = read_csv_rows(source_path)
        source_payloads[source_name] = {
            "target_name": target_name,
            "description": description,
            "fieldnames": fieldnames,
            "rows": rows,
        }

    for model in MODEL_ORDER:
        model_dir = output_dir / MODEL_DIRS[model]
        model_dir.mkdir(parents=True, exist_ok=True)
        available_files: List[tuple[str, str]] = []
        for source_name, payload in source_payloads.items():
            filtered_rows = filter_rows_by_model(payload["rows"], model)
            if not filtered_rows:
                continue
            target_path = model_dir / payload["target_name"]
            write_csv_rows(target_path, payload["fieldnames"], filtered_rows)
            available_files.append((payload["target_name"], payload["description"]))

        readme = "\n".join(model_status_lines(model, available_files))
        (model_dir / "00_说明_中文.md").write_text(readme, encoding="utf-8-sig")

    (output_dir / "README_中文.md").write_text(
        build_top_level_readme(summary_dir, output_dir),
        encoding="utf-8-sig",
    )
    print(f"Organized per-model result folders under: {output_dir}")


if __name__ == "__main__":
    main()
