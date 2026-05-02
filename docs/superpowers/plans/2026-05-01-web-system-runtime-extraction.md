# Web System Runtime Extraction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extract the runtime pieces needed by the Web project out of `streamlit_system` so the Web frontend, backend, inference stack, and training flow continue to work without any `streamlit` dependency.

**Architecture:** Keep the current service boundaries, but replace every `streamlit_system` runtime dependency with a new first-class `web_system_runtime` directory. The backend continues to orchestrate tasks through HTTP APIs, while dataset validation, inference gateway, model services, training service, scripts, and Docker wiring are repointed to the new runtime root and the repository model assets.

**Tech Stack:** FastAPI, Vue 3, Docker Compose, micromamba model-service images, PowerShell startup scripts, Python unittest

---

### Task 1: Lock the target behavior with failing tests

**Files:**
- Modify: `D:\codex\bishe_base\web_system_backend\tests\test_container_deployment_artifacts.py`
- Create: `D:\codex\bishe_base\web_system_backend\tests\test_runtime_independence.py`

- [ ] Add assertions that Web deployment artifacts reference `web_system_runtime` and do not require `streamlit_system`.
- [ ] Add backend configuration/path-resolution tests that expect runtime roots and gateway mount roots to be runtime-based rather than streamlit-based.
- [ ] Run the targeted backend tests and confirm they fail for the expected dependency reasons before implementation.

### Task 2: Create the standalone runtime directory

**Files:**
- Create: `D:\codex\bishe_base\web_system_runtime\README.md`
- Create: `D:\codex\bishe_base\web_system_runtime\docker-compose.yml`
- Create: `D:\codex\bishe_base\web_system_runtime\docker\Dockerfile.gateway`
- Create: `D:\codex\bishe_base\web_system_runtime\docker\Dockerfile.model-service`
- Create: `D:\codex\bishe_base\web_system_runtime\service_runtime\gateway_app.py`
- Create: `D:\codex\bishe_base\web_system_runtime\service_runtime\model_service.py`
- Create: `D:\codex\bishe_base\web_system_runtime\service_runtime\training_service.py`
- Create: `D:\codex\bishe_base\web_system_runtime\shared\sample_validation.py`
- Create: `D:\codex\bishe_base\web_system_runtime\shared\result_table.py`
- Create: `D:\codex\bishe_base\web_system_runtime\shared\resource_monitor.py`
- Create: `D:\codex\bishe_base\web_system_runtime\runtime_support\bundle.py`

- [ ] Copy the non-UI runtime/service code out of `streamlit_system`.
- [ ] Rename internal defaults so workspace/model references point at repo assets and runtime storage under `web_system_runtime`.
- [ ] Preserve gateway, model-service, and training-service API compatibility so the backend and frontend do not need endpoint-level rewrites.

### Task 3: Rewire the backend away from streamlit-specific paths and imports

**Files:**
- Modify: `D:\codex\bishe_base\web_system_backend\app\core\config.py`
- Modify: `D:\codex\bishe_base\web_system_backend\app\services\legacy_support.py`
- Modify: `D:\codex\bishe_base\web_system_backend\app\services\serializers.py`
- Modify: `D:\codex\bishe_base\web_system_backend\app\main.py`
- Modify: `D:\codex\bishe_base\web_system_backend\tests\test_system_summary.py`

- [ ] Introduce runtime-root and workspace-root settings with environment overrides for local and container runs.
- [ ] Replace `streamlit_system` bundle inspection imports with imports from `web_system_runtime`.
- [ ] Repoint seeded datasets, upload/output directories, model-version directories, and path translation helpers to runtime locations.
- [ ] Keep task serialization, downloads, and summary probing behavior unchanged from the frontend’s perspective.

### Task 4: Rewire scripts and Docker deployment

**Files:**
- Modify: `D:\codex\bishe_base\docker-compose.web.yml`
- Modify: `D:\codex\bishe_base\scripts\start_web_system.ps1`
- Modify: `D:\codex\bishe_base\scripts\start_web_system_docker.ps1`
- Modify: `D:\codex\bishe_base\web_system_backend\README.md`
- Modify: `D:\codex\bishe_base\web_system_frontend\README.md`

- [ ] Change the local startup script so it launches the runtime gateway stack from `web_system_runtime` and launches the WSL training service from the new runtime root.
- [ ] Update Web Docker wiring so the backend mounts and addresses `web_system_runtime` instead of `streamlit_system`.
- [ ] Update operator docs so the supported startup path no longer mentions Streamlit.

### Task 5: Seed runtime data and verify the full chain

**Files:**
- Copy into: `D:\codex\bishe_base\web_system_runtime\training_bundles\`
- Create if missing: `D:\codex\bishe_base\web_system_runtime\trained_model_versions\`
- Create if missing: `D:\codex\bishe_base\web_system_runtime\outputs\`
- Create if missing: `D:\codex\bishe_base\web_system_runtime\user_bundles\`

- [ ] Copy the built-in training smoke bundle into the new runtime tree.
- [ ] Ensure the runtime storage directories exist for uploads, outputs, and trained versions.
- [ ] Run the targeted backend tests again until green.
- [ ] Run the Web health/startup checks to confirm the Web project no longer depends on any `streamlit_system` path or service.
