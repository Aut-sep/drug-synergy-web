from __future__ import annotations

import importlib
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


class RuntimeIndependenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_root = Path(tempfile.mkdtemp(prefix="web-runtime-config-"))
        self.runtime_root = self.temp_root / "web_system_runtime"
        self.workspace_root = self.temp_root / "workspace"
        self.runtime_root.mkdir(parents=True, exist_ok=True)
        self.workspace_root.mkdir(parents=True, exist_ok=True)

    def test_settings_use_runtime_root_and_workspace_root_overrides(self) -> None:
        with patch.dict(
            os.environ,
            {
                "WEB_SYSTEM_RUNTIME_ROOT": str(self.runtime_root),
                "WEB_SYSTEM_WORKSPACE_ROOT": str(self.workspace_root),
                "WEB_SYSTEM_GATEWAY_RUNTIME_ROOT": "/workspace/web_system_runtime",
            },
            clear=False,
        ):
            from app.core import config as config_module

            importlib.reload(config_module)
            config_module.get_settings.cache_clear()
            settings = config_module.get_settings()

        self.assertEqual(settings.runtime_root, self.runtime_root.resolve())
        self.assertEqual(settings.workspace_root, self.workspace_root.resolve())
        self.assertEqual(settings.legacy_gateway_runtime_root, "/workspace/web_system_runtime")
        self.assertTrue(str(settings.runtime_root).endswith("web_system_runtime"))
        self.assertNotIn("streamlit_system", str(settings.runtime_root))

    def test_bridge_path_resolution_uses_runtime_mount_root(self) -> None:
        expected_file = self.runtime_root / "outputs" / "web_system_bridge" / "result.csv"
        expected_file.parent.mkdir(parents=True, exist_ok=True)
        expected_file.write_text("sample", encoding="utf-8")

        with patch.dict(
            os.environ,
            {
                "WEB_SYSTEM_RUNTIME_ROOT": str(self.runtime_root),
                "WEB_SYSTEM_WORKSPACE_ROOT": str(self.workspace_root),
                "WEB_SYSTEM_GATEWAY_RUNTIME_ROOT": "/workspace/web_system_runtime",
            },
            clear=False,
        ):
            from app.core import config as config_module
            from app.services import serializers as serializers_module

            importlib.reload(config_module)
            config_module.get_settings.cache_clear()
            importlib.reload(serializers_module)

            resolved = serializers_module.resolve_bridge_path(
                "/workspace/web_system_runtime/outputs/web_system_bridge/result.csv"
            )

        self.assertEqual(resolved, expected_file.resolve())
        self.assertNotIn("streamlit_system", str(resolved))

    def test_legacy_storage_path_rewrite_targets_runtime_locations(self) -> None:
        old_runtime_root = self.temp_root / "streamlit_system"
        old_output = old_runtime_root / "outputs" / "web_system_bridge" / "result.csv"

        with patch.dict(
            os.environ,
            {
                "WEB_SYSTEM_RUNTIME_ROOT": str(self.runtime_root),
                "WEB_SYSTEM_WORKSPACE_ROOT": str(self.workspace_root),
                "WEB_SYSTEM_GATEWAY_RUNTIME_ROOT": "/workspace/web_system_runtime",
            },
            clear=False,
        ):
            from app.core import config as config_module
            from app.services import legacy_support as legacy_support_module

            importlib.reload(config_module)
            config_module.get_settings.cache_clear()
            importlib.reload(legacy_support_module)

            rewritten = legacy_support_module.rewrite_legacy_storage_path(str(old_output))

        self.assertEqual(
            Path(rewritten),
            (self.runtime_root / "outputs" / "web_system_bridge" / "result.csv").resolve(),
        )
        self.assertNotIn("streamlit_system", rewritten)


if __name__ == "__main__":
    unittest.main()
