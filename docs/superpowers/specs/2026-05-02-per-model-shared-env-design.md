# Per-Model Shared Environment Design

## Goal

Unify training and inference environments on a per-model basis so that each model family keeps exactly one conda environment definition:

- `ddi.yml` for DualSyn
- `mf.yml` for MFSynDCP
- `mvc.yml` for MVCASyn
- `mtl.yml` for MTLSynergy

The system should remain portable across Linux machines, preserve current model service boundaries, and reduce dependency drift between training and inference.

The dependency baseline for each model should follow the original dependency expectations published by that model's GitHub project as closely as practical, instead of introducing new inferred or simplified stacks unless a concrete compatibility issue forces an adjustment.

## Approved Direction

Use one environment per model, shared by both training and inference.

This design explicitly does **not** merge all four models into a single global environment. That would increase dependency conflict risk and make future debugging much harder.

## Scope

### In Scope

- Remove the separate `*_infer.yml` environment files from active use.
- Make each inference service build from the same YAML file used by training for that model.
- Keep the existing multi-service deployment structure:
  - `dualsyn-service`
  - `mfsyndcp-service`
  - `mvcasyn-service`
  - `mtlsynergy-service`
  - `training-service`
- Keep training-service responsible for holding all four model environments.
- Preserve current backend, gateway, and runtime APIs.
- Keep the system runnable on Linux without requiring any Streamlit component.

### Out of Scope

- Merging all models into one super-environment.
- Refactoring model code into a unified training framework.
- Replacing Docker with another deployment mode.
- Rewriting the training orchestration API.

## Design

### 1. Environment Model

Each model gets exactly one canonical conda YAML:

- DualSyn: `benchmark_factory/env/ddi.yml`
- MFSynDCP: `benchmark_factory/env/mf.yml`
- MVCASyn: `benchmark_factory/env/mvc.yml`
- MTLSynergy: `benchmark_factory/env/mtl.yml`

Inference containers and training-service will both build from these same files.

These YAML files should be treated as the model's canonical dependency contract. When possible, package versions and major libraries should match the original upstream project requirements rather than a custom unified stack.

### 2. Service Build Strategy

The current architecture keeps one dedicated inference container per model plus one shared training container. That structure will stay unchanged.

The unification happens at the environment-definition level:

- `dualsyn-service` uses `ddi.yml`
- `mfsyndcp-service` uses `mf.yml`
- `mvcasyn-service` uses `mvc.yml`
- `mtlsynergy-service` uses `mtl.yml`
- `training-service` creates the same four environments with the same four YAML files

This keeps isolation between models while removing training/inference drift.

### 2.1 Upstream Dependency Principle

Environment unification does not mean cross-model dependency unification.

For each model:

- start from the dependency requirements described by the original GitHub repository
- preserve the model's original PyTorch / CUDA / PyG / RDKit expectations where applicable
- only make changes when required for Docker, Linux portability, or confirmed package availability issues
- document any deviation from upstream requirements explicitly

This avoids silently changing model behavior just to make the environments look cleaner.

### 3. Runtime Device Policy

The shared per-model environments must support GPU for both training and inference.

Runtime behavior will be controlled by execution-time device selection rather than by separate CPU-only inference environments:

- Training supports `device=auto/cuda/cpu`
- Inference services must also be able to use GPU when the host exposes it to Docker
- The same per-model environment should remain usable on CPU-only hosts when GPU is unavailable

This avoids maintaining parallel CPU/GPU environment families while still allowing hardware acceleration for both workflows.

### 4. Portability

The design stays portable because portability depends more on deterministic Dockerfiles and clear external asset placement than on having separate inference YAML files.

The following remain external/manual assets:

- model weights
- `benchmark_factory/env/miniconda.sh`

The repository continues to carry only source, environment definitions, compose files, runtime code, and docs.

## Planned Code Changes

### Compose

Update `docker-compose.web.yml` so each model inference service points to the shared training YAML instead of the dedicated inference YAML.

Expected mapping:

- `ENV_FILE: benchmark_factory/env/ddi.yml`
- `ENV_FILE: benchmark_factory/env/mf.yml`
- `ENV_FILE: benchmark_factory/env/mvc.yml`
- `ENV_FILE: benchmark_factory/env/mtl.yml`

Also align `ENV_NAME` with training env names:

- `ddi`
- `mf`
- `mvc`
- `mtl`

Add GPU container support for both inference and training services:

- `dualsyn-service`
- `mfsyndcp-service`
- `mvcasyn-service`
- `mtlsynergy-service`
- `training-service`

The compose design should allow these services to see NVIDIA GPUs on Linux hosts that have the NVIDIA runtime/toolkit installed.

### Docker Runtime

`web_system_runtime/docker/Dockerfile.model-service` will continue to build a single model-specific environment, but now from the shared YAML.

`web_system_runtime/docker/Dockerfile.training-service` will continue to create all four environments from the same YAML set.

### Environment Files

The `*_infer.yml` files will be retired from active use. We may either:

1. delete them, or
2. keep them temporarily with a clear deprecation note

Preferred implementation: delete active references first, then remove the files if nothing depends on them.

The surviving shared YAML file for each model becomes the single source of truth and should reflect the original upstream dependency needs for that model.

### Documentation

Update deployment and architecture docs so they describe:

- one environment per model
- shared training/inference dependency base
- GPU-capable training environment model

## Risks

### Larger Inference Images

Inference images will become heavier than the previous CPU-only inference environments.

Mitigation:

- accept the larger image size in exchange for lower maintenance complexity
- keep model services separated so each image only carries one model environment

### CPU-Only Machines

Some shared environments include CUDA-related packages for both training and inference.

Mitigation:

- keep runtime device fallback logic
- verify the containers can still run inference on CPU-only Linux hosts
- avoid hard-coding CUDA-only execution paths in service startup

### Dependency Drift Hidden in Code

Even after environment unification, some model scripts may still assume different runtime behavior between training and inference.

Mitigation:

- smoke-test each model service after the merge
- verify one inference path and one training path still work after environment unification

### Over-Normalizing Dependencies

Trying to make the four model environments look too similar may accidentally break one model's original assumptions.

Mitigation:

- prefer upstream model-specific dependencies over aesthetic consistency
- avoid forcing all models onto the same torch/cuda stack unless upstream already matches
- record any unavoidable divergence from the original GitHub requirements

## Verification Plan

After implementation:

1. `docker compose -f docker-compose.web.yml config`
2. backend unit tests
3. build each runtime service successfully
4. verify `/health` for gateway and training-service
5. run at least one inference smoke path
6. verify training-service still resolves all four environments
7. verify each inference service can see GPU when GPU is exposed into Docker
8. verify one inference run can execute with GPU-enabled runtime

## Recommendation

Proceed with the per-model shared-environment design and explicit GPU container support together.

Target end state:

- each model has one shared environment
- training can use GPU
- inference can use GPU
- the same deployment still remains runnable on CPU-only hosts when needed
