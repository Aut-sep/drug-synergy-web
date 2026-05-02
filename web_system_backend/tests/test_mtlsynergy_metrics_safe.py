from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class MTLSynergyMetricsSafeTests(unittest.TestCase):
    def test_safe_roc_auc_score_returns_nan_for_single_class(self) -> None:
        from MTLSynergy.utils.metrics_safe import safe_roc_auc_score

        score = safe_roc_auc_score([1, 1, 1], [0.2, 0.6, 0.9])
        self.assertTrue(math.isnan(score))

    def test_summarize_metric_values_ignores_nan(self) -> None:
        from MTLSynergy.utils.metrics_safe import summarize_metric_values

        mean_value, std_value = summarize_metric_values([0.5, float("nan"), 1.5])
        self.assertAlmostEqual(mean_value, 1.0)
        self.assertAlmostEqual(std_value, 0.5)


if __name__ == "__main__":
    unittest.main()
