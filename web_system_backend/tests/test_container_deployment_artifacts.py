from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class ContainerDeploymentArtifactTests(unittest.TestCase):
    def test_web_container_artifacts_are_present_and_wired(self) -> None:
        compose_path = REPO_ROOT / "docker-compose.web.yml"
        backend_dockerfile = REPO_ROOT / "web_system_backend" / "Dockerfile"
        frontend_dockerfile = REPO_ROOT / "web_system_frontend" / "Dockerfile"
        training_dockerfile = REPO_ROOT / "web_system_runtime" / "docker" / "Dockerfile.training-service"
        nginx_conf = REPO_ROOT / "web_system_frontend" / "nginx.conf"
        docker_start_script = REPO_ROOT / "scripts" / "start_web_system_docker.ps1"
        root_windows_start = REPO_ROOT / "start.bat"
        root_linux_start = REPO_ROOT / "start.sh"

        self.assertTrue(compose_path.exists(), "web compose file should exist at repository root")
        self.assertTrue(backend_dockerfile.exists(), "backend Dockerfile should exist")
        self.assertTrue(frontend_dockerfile.exists(), "frontend Dockerfile should exist")
        self.assertTrue(training_dockerfile.exists(), "training service Dockerfile should exist")
        self.assertTrue(nginx_conf.exists(), "frontend nginx config should exist")
        self.assertTrue(docker_start_script.exists(), "docker startup script should exist")
        self.assertTrue(root_windows_start.exists(), "repository root Windows startup script should exist")
        self.assertTrue(root_linux_start.exists(), "repository root Linux startup script should exist")

        compose_text = compose_path.read_text(encoding="utf-8")
        backend_text = backend_dockerfile.read_text(encoding="utf-8")
        frontend_text = frontend_dockerfile.read_text(encoding="utf-8")
        nginx_text = nginx_conf.read_text(encoding="utf-8")
        docker_start_script_text = docker_start_script.read_text(encoding="utf-8")
        root_windows_start_text = root_windows_start.read_text(encoding="utf-8")
        root_linux_start_text = root_linux_start.read_text(encoding="utf-8")

        self.assertIn("web-backend:", compose_text)
        self.assertIn("web-frontend:", compose_text)
        self.assertIn("gateway:", compose_text)
        self.assertIn("training-service:", compose_text)
        self.assertIn("dualsyn-service:", compose_text)
        self.assertIn("mfsyndcp-service:", compose_text)
        self.assertIn("mvcasyn-service:", compose_text)
        self.assertIn("mtlsynergy-service:", compose_text)
        self.assertIn("9000:9000", compose_text)
        self.assertIn("5173:80", compose_text)
        self.assertIn("WEB_SYSTEM_DATABASE_URL", compose_text)
        self.assertIn("WEB_SYSTEM_RUNTIME_ROOT", compose_text)
        self.assertIn("WEB_SYSTEM_WORKSPACE_ROOT", compose_text)
        self.assertIn("WEB_SYSTEM_GATEWAY_URL: http://gateway:8000", compose_text)
        self.assertIn("WEB_SYSTEM_TRAINING_URL: http://training-service:8011", compose_text)
        self.assertIn("WEB_SYSTEM_GATEWAY_RUNTIME_ROOT", compose_text)
        self.assertNotIn("streamlit_system", compose_text)
        self.assertIn("uvicorn", backend_text)
        self.assertIn("npm run build", frontend_text)
        self.assertIn("proxy_pass http://web-backend:9000", nginx_text)
        self.assertIn("docker compose", docker_start_script_text)
        self.assertIn("docker-compose.web.yml", docker_start_script_text)
        self.assertIn("up", docker_start_script_text)
        self.assertIn("Gateway:       http://127.0.0.1:8000/health", docker_start_script_text)
        self.assertIn("Training:      http://127.0.0.1:8011/health", docker_start_script_text)
        self.assertNotIn("optional external service", docker_start_script_text.lower())
        self.assertNotIn("start it separately", docker_start_script_text.lower())
        self.assertIn("start_web_system.ps1", root_windows_start_text)
        self.assertIn("docker compose -f \"$SCRIPT_DIR/web_system_runtime/docker-compose.yml\" up -d", root_linux_start_text)
        self.assertIn("http://127.0.0.1:8000/health", root_linux_start_text)
        self.assertNotIn("streamlit_system", docker_start_script_text)


if __name__ == "__main__":
    unittest.main()
