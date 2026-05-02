from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from statistics import mean, pstdev


DEFAULT_METRICS = ["roc_auc", "pr_auc", "acc", "bacc", "precision", "recall", "kappa"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize per-fold metrics using a shared schema.")
    parser.add_argument("metrics_csv", help="CSV file with one row per fold.")
    parser.add_argument("--metrics", nargs="*", default=DEFAULT_METRICS)
    args = parser.parse_args()

    path = Path(args.metrics_csv).resolve()
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"{path} is empty")

    for metric in args.metrics:
        if metric not in rows[0]:
            raise ValueError(f"{path} is missing metric column: {metric}")

    print("metric,mean,std")
    for metric in args.metrics:
        values = [float(row[metric]) for row in rows]
        std = pstdev(values) if len(values) > 1 else 0.0
        print(f"{metric},{mean(values):.6f},{std:.6f}")


if __name__ == "__main__":
    main()
