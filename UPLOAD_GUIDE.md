# GitHub Upload Guide

This folder is the GitHub upload package for the standalone web system source code.

## Included

- frontend, backend, runtime, and benchmark source code
- Docker compose and startup scripts
- shared per-model environment YAML files used by both inference and training
- model source code and required lightweight data files

## Not Included

- `benchmark_factory/env/miniconda.sh`
- local caches, logs, outputs, databases, and archive history
- pre-trained model weight files

## Before First Build

Place `benchmark_factory/env/miniconda.sh` back into:

`benchmark_factory/env/miniconda.sh`

If you want immediate inference without retraining, also place the existing model files into:

- `DualSyn/DualSyn/save_model/`
- `MFSynDCP/MFSynDCP/result/`
- `MVCASyn/results/model/`
- `MTLSynergy/save/AutoEncoder/`
- `MTLSynergy/save/MTLSynergy/`

## Deploy

```bash
docker compose -f docker-compose.web.yml up -d --build
```

## Deploy With GPU

If the Linux host has an NVIDIA driver plus `nvidia-container-toolkit` working with Docker, use:

```bash
docker compose -f docker-compose.web.yml -f docker-compose.web.gpu.yml up -d --build
```
