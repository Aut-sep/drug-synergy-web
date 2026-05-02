from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class TrainingRuntimeLayoutTests(unittest.TestCase):
    def test_reset_training_outputs_recreates_runtime_directories(self) -> None:
        from web_system_runtime.service_runtime import training_service

        temp_root = Path(tempfile.mkdtemp(prefix="training-runtime-layout-"))
        source_root = temp_root / "source"

        expected_dirs = [
            source_root / "DualSyn" / "DualSyn" / "save_model",
            source_root / "DualSyn" / "DualSyn" / "result",
            source_root / "MFSynDCP" / "MFSynDCP" / "result",
            source_root / "MVCASyn" / "results" / "training_run",
            source_root / "MTLSynergy" / "save",
            source_root / "MTLSynergy" / "save" / "AutoEncoder",
            source_root / "MTLSynergy" / "save" / "MTLSA",
            source_root / "MTLSynergy" / "save" / "MTLSynergy",
            source_root / "MTLSynergy" / "result",
        ]

        for directory in expected_dirs:
            directory.mkdir(parents=True, exist_ok=True)
            (directory / "stale.txt").write_text("old", encoding="utf-8")

        training_service._reset_training_outputs(source_root)

        for directory in expected_dirs:
            self.assertTrue(directory.exists(), f"{directory} should exist after reset")
            self.assertTrue(directory.is_dir(), f"{directory} should remain a directory")
            self.assertFalse((directory / "stale.txt").exists(), f"{directory} should be cleaned")


if __name__ == "__main__":
    unittest.main()
