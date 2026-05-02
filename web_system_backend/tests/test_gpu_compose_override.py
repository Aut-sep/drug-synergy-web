from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class GpuComposeOverrideTests(unittest.TestCase):
    def test_gpu_override_targets_training_and_inference_services(self) -> None:
        gpu_compose_path = REPO_ROOT / "docker-compose.web.gpu.yml"
        self.assertTrue(gpu_compose_path.exists(), "GPU override compose file should exist")

        compose_text = gpu_compose_path.read_text(encoding="utf-8")
        for service_name in [
            "training-service:",
            "dualsyn-service:",
            "mfsyndcp-service:",
            "mvcasyn-service:",
            "mtlsynergy-service:",
        ]:
            self.assertIn(service_name, compose_text)

        self.assertIn("runtime: nvidia", compose_text)
        self.assertIn("NVIDIA_VISIBLE_DEVICES", compose_text)
        self.assertIn("NVIDIA_DRIVER_CAPABILITIES", compose_text)


if __name__ == "__main__":
    unittest.main()
