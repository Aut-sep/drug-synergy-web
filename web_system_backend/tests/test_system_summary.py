from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


_TMP_ROOT = Path(tempfile.mkdtemp(prefix="web-system-tests-"))
os.environ["WEB_SYSTEM_DATABASE_URL"] = f"sqlite:///{(_TMP_ROOT / 'test.db').as_posix()}"
os.environ["WEB_SYSTEM_GATEWAY_URL"] = "http://gateway.test"
os.environ["WEB_SYSTEM_TRAINING_URL"] = "http://training.test"
os.environ["WEB_SYSTEM_RUNTIME_ROOT"] = str(_TMP_ROOT / "web_system_runtime")
os.environ["WEB_SYSTEM_WORKSPACE_ROOT"] = str(_TMP_ROOT)
os.environ["WEB_SYSTEM_GATEWAY_RUNTIME_ROOT"] = "/workspace/web_system_runtime"

from app.db import Base, SessionLocal, engine  # noqa: E402
from app.models import DatasetBundle, RunTask  # noqa: E402
from app.routers import system  # noqa: E402
from app.services import legacy_support  # noqa: E402


class SystemSummaryTests(unittest.TestCase):
    def setUp(self) -> None:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    def _seed_session(self):
        session = SessionLocal()
        dataset = DatasetBundle(
            name="Dataset A",
            bundle_path=str(_TMP_ROOT / "dataset-a"),
            sample_file="samples.csv",
            source_type="upload",
            description="",
            is_ready=True,
            sample_count=12,
            files=["samples.csv"],
            validation_detail="ready",
        )
        session.add(dataset)
        session.flush()

        session.add_all(
            [
                RunTask(
                    task_type="inference",
                    title="Inference 1",
                    local_status="running",
                    remote_state="running",
                    remote_run_id="run-1",
                    dataset_id=dataset.id,
                    selected_models=["DualSyn"],
                    log_excerpt="",
                    error_message="",
                ),
                RunTask(
                    task_type="inference",
                    title="Inference 2",
                    local_status="completed",
                    remote_state="completed",
                    remote_run_id="run-2",
                    dataset_id=dataset.id,
                    selected_models=["DualSyn"],
                    log_excerpt="",
                    error_message="",
                ),
                RunTask(
                    task_type="training",
                    title="Training 1",
                    local_status="waiting",
                    remote_state="waiting",
                    remote_run_id="run-3",
                    dataset_id=dataset.id,
                    selected_models=["DualSyn"],
                    log_excerpt="",
                    error_message="",
                ),
            ]
        )
        session.commit()
        return session

    def test_summary_uses_snapshot_helpers_and_skips_remote_refresh(self) -> None:
        with self._seed_session() as db:
            def fake_list_model_versions(*, prefer_remote: bool = True):
                self.assertFalse(prefer_remote)
                return [{"version_id": "local-v1"}]

            def fake_gateway_health(*, timeout_seconds: float = 0, summary_only: bool = False):
                self.assertTrue(summary_only)
                self.assertLessEqual(timeout_seconds, 2.0)
                return {
                    "ready": False,
                    "degraded": True,
                    "probe_mode": "summary",
                    "detail": "Gateway snapshot unavailable.",
                    "url": "http://gateway.test",
                }

            def fake_training_health(*, timeout_seconds: float = 0, summary_only: bool = False):
                self.assertTrue(summary_only)
                self.assertLessEqual(timeout_seconds, 2.0)
                return {
                    "ready": True,
                    "degraded": False,
                    "probe_mode": "summary",
                    "detail": "Training snapshot is healthy.",
                    "url": "http://training.test",
                }

            with patch.object(system, "list_model_versions", side_effect=fake_list_model_versions):
                with patch.object(system, "gateway_health", side_effect=fake_gateway_health):
                    with patch.object(system, "training_health", side_effect=fake_training_health):
                        with patch.object(
                            system,
                            "system_resource_snapshot",
                            return_value={"monitoring_available": True, "detail": "", "cpu_percent": 10.0},
                        ):
                            summary = system.get_system_summary(db=db)

        self.assertEqual(summary["dataset_count"], 1)
        self.assertEqual(summary["inference_run_count"], 2)
        self.assertEqual(summary["training_run_count"], 1)
        self.assertEqual(summary["running_run_count"], 2)
        self.assertEqual(summary["latest_model_version_count"], 1)
        self.assertEqual(summary["gateway_health"]["probe_mode"], "summary")
        self.assertEqual(summary["training_health"]["probe_mode"], "summary")


class LegacyHealthProbeTests(unittest.TestCase):
    def test_gateway_health_summary_mode_uses_one_probe_only(self) -> None:
        fake_settings = SimpleNamespace(legacy_gateway_url="http://gateway.test")
        calls: list[tuple[str, str, float, str]] = []

        def fake_request_json(method: str, url: str, *, timeout: float, context: str, json_payload=None):
            calls.append((method, url, timeout, context))
            raise legacy_support.LegacyBridgeError("primary probe failed")

        with patch.object(legacy_support, "settings", fake_settings):
            with patch.object(legacy_support, "_request_json", side_effect=fake_request_json):
                result = legacy_support.gateway_health(timeout_seconds=0.25, summary_only=True)

        self.assertEqual(len(calls), 1)
        self.assertFalse(result["ready"])
        self.assertTrue(result["degraded"])
        self.assertEqual(result["probe_mode"], "summary")
        self.assertIn("摘要", result["detail"])

    def test_training_health_summary_mode_uses_one_probe_only(self) -> None:
        fake_settings = SimpleNamespace(legacy_training_url="http://training.test")
        calls: list[tuple[str, str, float, str]] = []

        def fake_request_json(method: str, url: str, *, timeout: float, context: str, json_payload=None):
            calls.append((method, url, timeout, context))
            raise legacy_support.LegacyBridgeError("primary probe failed")

        with patch.object(legacy_support, "settings", fake_settings):
            with patch.object(legacy_support, "_request_json", side_effect=fake_request_json):
                result = legacy_support.training_health(timeout_seconds=0.25, summary_only=True)

        self.assertEqual(len(calls), 1)
        self.assertFalse(result["ready"])
        self.assertTrue(result["degraded"])
        self.assertEqual(result["probe_mode"], "summary")
        self.assertIn("摘要", result["detail"])

    def test_local_model_version_snapshot_skips_remote_probe(self) -> None:
        version_root = _TMP_ROOT / "trained_model_versions"
        (version_root / "v-20260429-1").mkdir(parents=True, exist_ok=True)
        (version_root / "v-20260429-1" / "manifest.json").write_text('{"version_id":"v-20260429-1","selected_models":["DualSyn"]}', encoding="utf-8")
        (version_root / "v-20260429-2").mkdir(parents=True, exist_ok=True)

        fake_settings = SimpleNamespace(
            legacy_training_url="http://training.test",
            trained_model_root=version_root,
        )

        def fail_remote(*args, **kwargs):  # noqa: ANN001, ANN003
            raise AssertionError("remote version probe should not run")

        with patch.object(legacy_support, "settings", fake_settings):
            with patch.object(legacy_support, "_request_json", side_effect=fail_remote):
                versions = legacy_support.list_model_versions(prefer_remote=False)

        self.assertEqual(len(versions), 2)
        self.assertTrue(all("version_id" in item for item in versions))


if __name__ == "__main__":
    unittest.main()
