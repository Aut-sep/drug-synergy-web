from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class TrainingCommandTuningTests(unittest.TestCase):
    def test_resolve_mtlsynergy_batch_size_caps_large_datasets(self) -> None:
        from web_system_runtime.service_runtime import training_service

        self.assertEqual(training_service._resolve_mtlsynergy_batch_size(20), 5)
        self.assertEqual(training_service._resolve_mtlsynergy_batch_size(1000), 32)
        self.assertEqual(training_service._resolve_mtlsynergy_batch_size(3), 1)

    def test_mtlsynergy_command_uses_small_dataset_batch_override(self) -> None:
        from web_system_runtime.service_runtime import training_service

        request = training_service.TrainingRunRequest(
            bundle_path="/tmp/fake-bundle",
            selected_models=["MTLSynergy"],
            profile="quick",
            device="auto",
            epochs=2,
        )

        commands = training_service._command_for_model(
            "MTLSynergy",
            request,
            Path("/tmp/project"),
            "version123",
            sample_count=20,
        )

        self.assertEqual(len(commands), 2)
        ae_command, train_command = commands
        self.assertNotIn("--batch-size", ae_command)
        self.assertIn("--batch-size", train_command)
        batch_index = train_command.index("--batch-size")
        self.assertEqual(train_command[batch_index + 1], "5")


if __name__ == "__main__":
    unittest.main()
