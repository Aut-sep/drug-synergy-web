from __future__ import annotations

import warnings
from typing import Iterable

import numpy as np
from sklearn.metrics import roc_auc_score
from sklearn.exceptions import UndefinedMetricWarning


def safe_roc_auc_score(y_true, y_score) -> float:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=UndefinedMetricWarning)
            return float(roc_auc_score(y_true, y_score))
    except ValueError:
        return float("nan")


def summarize_metric_values(values: Iterable[float]) -> list[float]:
    array = np.asarray(list(values), dtype=float)
    return [float(np.nanmean(array)), float(np.nanstd(array))]
