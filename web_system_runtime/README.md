# Web System Runtime

`web_system_runtime` is the standalone runtime layer for the Web project.

It includes:

- the inference gateway
- model-service wrappers for the four models
- the training service
- shared validation, result-merging, and resource-monitor helpers
- runtime storage for uploads, outputs, training bundles, and trained model versions

## Full Runtime Stack

```powershell
cd D:\codex\bishe_base
docker compose -f .\docker-compose.web.yml up -d --build
```
