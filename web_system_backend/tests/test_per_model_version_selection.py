from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


_TMP_ROOT = Path(tempfile.mkdtemp(prefix="web-system-per-model-tests-"))
os.environ["WEB_SYSTEM_DATABASE_URL"] = f"sqlite:///{(_TMP_ROOT / 'test.db').as_posix()}"
os.environ["WEB_SYSTEM_GATEWAY_URL"] = "http://gateway.test"
os.environ["WEB_SYSTEM_TRAINING_URL"] = "http://training.test"
os.environ["WEB_SYSTEM_RUNTIME_ROOT"] = str(_TMP_ROOT / "web_system_runtime")
os.environ["WEB_SYSTEM_WORKSPACE_ROOT"] = str(_TMP_ROOT)
os.environ["WEB_SYSTEM_GATEWAY_RUNTIME_ROOT"] = "/workspace/web_system_runtime"

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "web_system_backend"
for candidate in (REPO_ROOT, BACKEND_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from app.db import Base, SessionLocal, engine  # noqa: E402
from app.models import DatasetBundle  # noqa: E402
from app.services import legacy_support  # noqa: E402
from app.services.serializers import task_to_schema  # noqa: E402
from web_system_runtime.service_runtime import training_service  # noqa: E402


class PerModelVersionSelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    def test_local_model_versions_virtualize_children_with_group_metadata(self) -> None:
        version_root = _TMP_ROOT / "trained_model_versions_local"
        version_dir = version_root / "train_20260503_demo"
        (version_dir / "artifacts" / "DualSyn").mkdir(parents=True, exist_ok=True)
        (version_dir / "artifacts" / "MVCASyn").mkdir(parents=True, exist_ok=True)
        (version_dir / "manifest.json").write_text(
            (
                "{"
                '"version_id":"train_20260503_demo",'
                '"created_at":"2026-05-03T10:00:00",'
                '"selected_models":["DualSyn","MVCASyn"],'
                '"version_group_name":"experiment-alpha",'
                '"version_note":"baseline-a"'
                "}"
            ),
            encoding="utf-8",
        )

        fake_settings = SimpleNamespace(
            legacy_training_url="http://training.test",
            trained_model_root=version_root,
        )

        with patch.object(legacy_support, "settings", fake_settings):
            versions = legacy_support.list_model_versions(prefer_remote=False)

        self.assertEqual([item["version_id"] for item in versions], ["train_20260503_demo::DualSyn", "train_20260503_demo::MVCASyn"])
        self.assertTrue(all(item["base_version_id"] == "train_20260503_demo" for item in versions))
        self.assertEqual([item["model_name"] for item in versions], ["DualSyn", "MVCASyn"])
        self.assertTrue(all(item["version_group_name"] == "experiment-alpha" for item in versions))
        self.assertTrue(str(versions[0]["artifact_root"]).endswith("artifacts\\DualSyn") or str(versions[0]["artifact_root"]).endswith("artifacts/DualSyn"))

    def test_create_inference_task_sends_per_model_version_mapping(self) -> None:
        bundle_dir = _TMP_ROOT / "bundle_inference"
        bundle_dir.mkdir(parents=True, exist_ok=True)
        (bundle_dir / "samples.csv").write_text(
            "sample_id,drug_a_name,drug_b_name,cell_line\ns1,a,b,c1\n",
            encoding="utf-8",
        )

        session = SessionLocal()
        dataset = DatasetBundle(
            name="Inference bundle",
            bundle_path=str(bundle_dir),
            sample_file="samples.csv",
            source_type="upload",
            description="",
            is_ready=True,
            sample_count=1,
            files=["samples.csv"],
            validation_detail="ready",
        )
        session.add(dataset)
        session.commit()
        session.refresh(dataset)

        captured_payload: dict[str, object] = {}

        def fake_request_json(method: str, url: str, *, timeout: int, context: str, json_payload=None):
            captured_payload.update(json_payload or {})
            return {
                "state": "waiting",
                "run_id": "remote-infer-1",
                "summary": {},
            }

        with patch.object(legacy_support, "_request_json", side_effect=fake_request_json):
            task = legacy_support.create_inference_task(
                session,
                dataset,
                selected_models=["DualSyn", "MVCASyn"],
                model_version_id="shared-base-v1",
                model_version_ids={
                    "DualSyn": "shared-base-v1::DualSyn",
                    "MVCASyn": "shared-base-v2::MVCASyn",
                },
            )

        schema = task_to_schema(task)
        self.assertEqual(
            captured_payload["model_version_ids"],
            {
                "DualSyn": "shared-base-v1::DualSyn",
                "MVCASyn": "shared-base-v2::MVCASyn",
            },
        )
        self.assertEqual(
            schema.model_version_ids,
            {
                "DualSyn": "shared-base-v1::DualSyn",
                "MVCASyn": "shared-base-v2::MVCASyn",
            },
        )
        self.assertEqual(schema.model_version_id, "shared-base-v1")
        session.close()

    def test_training_service_lists_virtual_child_versions(self) -> None:
        version_root = _TMP_ROOT / "trained_model_versions_runtime"
        version_dir = version_root / "user_train_20260503_abc123"
        (version_dir / "artifacts" / "DualSyn").mkdir(parents=True, exist_ok=True)
        (version_dir / "artifacts" / "MTLSynergy").mkdir(parents=True, exist_ok=True)
        (version_dir / "manifest.json").write_text(
            (
                "{"
                '"version_id":"user_train_20260503_abc123",'
                '"selected_models":["DualSyn","MTLSynergy"],'
                '"version_group_name":"group-zeta",'
                '"version_note":"note-zeta"'
                "}"
            ),
            encoding="utf-8",
        )

        with patch.object(training_service, "TRAINED_MODEL_ROOT", version_root):
            versions = training_service._list_versions()

        self.assertEqual(
            [item["version_id"] for item in versions],
            ["user_train_20260503_abc123::DualSyn", "user_train_20260503_abc123::MTLSynergy"],
        )
        self.assertEqual([item["model_name"] for item in versions], ["DualSyn", "MTLSynergy"])
        self.assertTrue(all(item["version_group_name"] == "group-zeta" for item in versions))


if __name__ == "__main__":
    unittest.main()
