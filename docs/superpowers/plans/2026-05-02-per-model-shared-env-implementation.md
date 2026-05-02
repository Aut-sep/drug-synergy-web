# Per-Model Shared Environment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make each model use one shared environment for both training and inference, while adding a Docker GPU enablement path for both workflows without breaking CPU-only deployments.

**Architecture:** Keep the current multi-service runtime layout, but change inference services to build from the same model YAMLs used by training. Add an optional GPU compose override so Linux hosts with NVIDIA runtime can enable GPU for training and inference, while the base compose file stays portable on CPU-only machines.

**Tech Stack:** Docker Compose, FastAPI, conda, PyTorch, unittest, PowerShell, Linux shell

---

## File Map

### Compose and Runtime

- Modify: `D:\codex\bishe_base\docker-compose.web.yml`
- Create: `D:\codex\bishe_base\docker-compose.web.gpu.yml`
- Modify: `D:\codex\bishe_base\web_system_runtime\docker\Dockerfile.model-service`
- Modify: `D:\codex\bishe_base\web_system_runtime\docker\Dockerfile.training-service`

### Tests

- Modify: `D:\codex\bishe_base\web_system_backend\tests\test_container_deployment_artifacts.py`
- Create: `D:\codex\bishe_base\web_system_backend\tests\test_gpu_compose_override.py`

### Docs and Startup Guidance

- Modify: `D:\codex\bishe_base\UPLOAD_GUIDE.md`
- Modify: `D:\codex\bishe_base\scripts\start_web_system_docker.ps1`
- Modify: `D:\codex\bishe_base\docs\superpowers\specs\2026-05-02-per-model-shared-env-design.md`

---

### Task 1: Lock in Expected Shared-Environment and GPU Compose Behavior

**Files:**
- Modify: `D:\codex\bishe_base\web_system_backend\tests\test_container_deployment_artifacts.py`
- Create: `D:\codex\bishe_base\web_system_backend\tests\test_gpu_compose_override.py`

- [ ] **Step 1: Write the failing tests for compose environment unification and GPU override presence**

Add assertions that:

- `docker-compose.web.yml` points inference services to `ddi.yml`, `mf.yml`, `mvc.yml`, `mtl.yml`
- inference service env names are `ddi`, `mf`, `mvc`, `mtl`
- no active compose references to `ddi_infer.yml`, `mf_infer.yml`, `mvc_infer.yml`, `mtl_infer.yml`
- `docker-compose.web.gpu.yml` exists and contains GPU enablement for `training-service` plus the four inference services

Test skeleton to add:

```python
from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class GpuComposeOverrideTests(unittest.TestCase):
    def test_gpu_override_targets_training_and_inference_services(self) -> None:
        gpu_compose = REPO_ROOT / "docker-compose.web.gpu.yml"
        self.assertTrue(gpu_compose.exists(), "GPU override compose file should exist")

        text = gpu_compose.read_text(encoding="utf-8")
        for service_name in [
            "training-service:",
            "dualsyn-service:",
            "mfsyndcp-service:",
            "mvcasyn-service:",
            "mtlsynergy-service:",
        ]:
            self.assertIn(service_name, text)

        self.assertIn("gpus: all", text)
```

- [ ] **Step 2: Run the targeted tests and verify they fail for the expected missing/old compose behavior**

Run:

```powershell
python -m unittest `
  .\web_system_backend\tests\test_container_deployment_artifacts.py `
  .\web_system_backend\tests\test_gpu_compose_override.py -v
```

Expected:

- failure because `docker-compose.web.gpu.yml` does not exist yet
- failure because current base compose still references `*_infer.yml`

- [ ] **Step 3: Commit the failing-test checkpoint only if the repo workflow requires it**

Do not commit a broken intermediate state in this repo unless explicitly needed. Keep moving into the implementation steps once the red phase is verified.

---

### Task 2: Switch Inference Services to Per-Model Shared Environments

**Files:**
- Modify: `D:\codex\bishe_base\docker-compose.web.yml`

- [ ] **Step 1: Update inference service environment references in the base compose file**

Change each inference service build arg mapping:

```yaml
dualsyn-service:
  build:
    args:
      ENV_FILE: benchmark_factory/env/ddi.yml
      ENV_NAME: ddi

mfsyndcp-service:
  build:
    args:
      ENV_FILE: benchmark_factory/env/mf.yml
      ENV_NAME: mf

mvcasyn-service:
  build:
    args:
      ENV_FILE: benchmark_factory/env/mvc.yml
      ENV_NAME: mvc

mtlsynergy-service:
  build:
    args:
      ENV_FILE: benchmark_factory/env/mtl.yml
      ENV_NAME: mtl
```

- [ ] **Step 2: Keep the base compose file CPU-portable**

Do not add mandatory GPU requirements to `docker-compose.web.yml`. This file should still work as the default compose entry point for CPU-only hosts.

- [ ] **Step 3: Run compose expansion to verify the base file is still valid**

Run:

```powershell
docker compose -f .\docker-compose.web.yml config
```

Expected:

- exit code `0`
- no references to `*_infer.yml` in the expanded config

---

### Task 3: Add Optional GPU Compose Override for Training and Inference

**Files:**
- Create: `D:\codex\bishe_base\docker-compose.web.gpu.yml`

- [ ] **Step 1: Create the GPU override compose file**

Use a focused override file like:

```yaml
services:
  training-service:
    gpus: all
    environment:
      NVIDIA_VISIBLE_DEVICES: ${NVIDIA_VISIBLE_DEVICES:-all}
      NVIDIA_DRIVER_CAPABILITIES: ${NVIDIA_DRIVER_CAPABILITIES:-compute,utility}

  dualsyn-service:
    gpus: all
    environment:
      NVIDIA_VISIBLE_DEVICES: ${NVIDIA_VISIBLE_DEVICES:-all}
      NVIDIA_DRIVER_CAPABILITIES: ${NVIDIA_DRIVER_CAPABILITIES:-compute,utility}

  mfsyndcp-service:
    gpus: all
    environment:
      NVIDIA_VISIBLE_DEVICES: ${NVIDIA_VISIBLE_DEVICES:-all}
      NVIDIA_DRIVER_CAPABILITIES: ${NVIDIA_DRIVER_CAPABILITIES:-compute,utility}

  mvcasyn-service:
    gpus: all
    environment:
      NVIDIA_VISIBLE_DEVICES: ${NVIDIA_VISIBLE_DEVICES:-all}
      NVIDIA_DRIVER_CAPABILITIES: ${NVIDIA_DRIVER_CAPABILITIES:-compute,utility}

  mtlsynergy-service:
    gpus: all
    environment:
      NVIDIA_VISIBLE_DEVICES: ${NVIDIA_VISIBLE_DEVICES:-all}
      NVIDIA_DRIVER_CAPABILITIES: ${NVIDIA_DRIVER_CAPABILITIES:-compute,utility}
```

- [ ] **Step 2: Verify base + GPU override merge cleanly**

Run:

```powershell
docker compose -f .\docker-compose.web.yml -f .\docker-compose.web.gpu.yml config
```

Expected:

- exit code `0`
- the five runtime services include GPU configuration in merged output

- [ ] **Step 3: Keep GPU support opt-in**

Do not replace the default startup path with mandatory GPU compose usage. The GPU override should be documented and available, not forced.

---

### Task 4: Make Runtime Dockerfiles Compatible with Shared Training/Inference Environments

**Files:**
- Modify: `D:\codex\bishe_base\web_system_runtime\docker\Dockerfile.model-service`
- Modify: `D:\codex\bishe_base\web_system_runtime\docker\Dockerfile.training-service`

- [ ] **Step 1: Review whether model-service still assumes inference-only packages**

Confirm the model-service Dockerfile only depends on:

- `${ENV_FILE}`
- `${ENV_NAME}`
- runtime web packages needed to host FastAPI

If needed, keep the current pinned runtime web packages and shared `.condarc` mirror logic intact.

- [ ] **Step 2: Ensure no hardcoded inference-only env assumptions remain**

Preserve:

- `MODEL_ENV_NAME=${ENV_NAME}`
- conda env creation from `${ENV_FILE}`

Avoid any naming or comments that still imply `*_infer` is the active path.

- [ ] **Step 3: Verify Dockerfiles remain syntactically valid through compose expansion checks**

Run:

```powershell
docker compose -f .\docker-compose.web.yml config
docker compose -f .\docker-compose.web.yml -f .\docker-compose.web.gpu.yml config
```

Expected:

- both commands exit `0`

---

### Task 5: Update Docs and Startup Instructions for Shared Envs and GPU Mode

**Files:**
- Modify: `D:\codex\bishe_base\UPLOAD_GUIDE.md`
- Modify: `D:\codex\bishe_base\scripts\start_web_system_docker.ps1`
- Modify: `D:\codex\bishe_base\docs\superpowers\specs\2026-05-02-per-model-shared-env-design.md`

- [ ] **Step 1: Document the new startup commands**

Add or update instructions so users can choose:

```bash
docker compose -f docker-compose.web.yml up -d --build
```

or GPU mode:

```bash
docker compose -f docker-compose.web.yml -f docker-compose.web.gpu.yml up -d --build
```

- [ ] **Step 2: Document Linux GPU prerequisites**

List the minimum GPU requirements:

- NVIDIA driver installed on host
- `nvidia-container-toolkit` installed
- Docker GPU runtime working

- [ ] **Step 3: Make the Windows/PowerShell helper mention GPU override availability**

Update `start_web_system_docker.ps1` so the script guidance references the GPU override file, even if the default path still launches the CPU-portable base compose file.

---

### Task 6: Run Verification and Capture the Final Behavior

**Files:**
- Modify: `D:\codex\bishe_base\web_system_backend\tests\test_container_deployment_artifacts.py`
- Create: `D:\codex\bishe_base\web_system_backend\tests\test_gpu_compose_override.py`

- [ ] **Step 1: Run the focused compose-related tests**

Run:

```powershell
python -m unittest `
  .\web_system_backend\tests\test_container_deployment_artifacts.py `
  .\web_system_backend\tests\test_gpu_compose_override.py -v
```

Expected:

- all targeted tests pass

- [ ] **Step 2: Run the full backend test suite**

Run:

```powershell
python -m unittest discover .\web_system_backend\tests -v
```

Expected:

- all tests pass

- [ ] **Step 3: Run both compose validation commands**

Run:

```powershell
docker compose -f .\docker-compose.web.yml config
docker compose -f .\docker-compose.web.yml -f .\docker-compose.web.gpu.yml config
```

Expected:

- both commands exit `0`

- [ ] **Step 4: Review staged diff before commit**

Run:

```powershell
git diff -- docker-compose.web.yml docker-compose.web.gpu.yml `
  web_system_runtime/docker/Dockerfile.model-service `
  web_system_runtime/docker/Dockerfile.training-service `
  web_system_backend/tests `
  UPLOAD_GUIDE.md `
  scripts/start_web_system_docker.ps1
```

Expected:

- diff shows shared env references, GPU override file, updated tests, and docs

- [ ] **Step 5: Commit**

```powershell
git add docker-compose.web.yml docker-compose.web.gpu.yml `
  web_system_runtime/docker/Dockerfile.model-service `
  web_system_runtime/docker/Dockerfile.training-service `
  web_system_backend/tests `
  UPLOAD_GUIDE.md `
  scripts/start_web_system_docker.ps1 `
  docs/superpowers/specs/2026-05-02-per-model-shared-env-design.md `
  docs/superpowers/plans/2026-05-02-per-model-shared-env-implementation.md
git commit -m "feat: share per-model training and inference environments"
```

---

## Self-Review

### Spec Coverage

- shared per-model envs: covered by Tasks 1-2
- GPU support for training and inference: covered by Task 3
- Docker/runtime compatibility: covered by Task 4
- docs/startup guidance: covered by Task 5
- verification: covered by Task 6

### Placeholder Scan

No `TODO`/`TBD` placeholders remain in the tasks.

### Type and Naming Consistency

- shared env names are consistently `ddi`, `mf`, `mvc`, `mtl`
- compose file names are consistently `docker-compose.web.yml` and `docker-compose.web.gpu.yml`
