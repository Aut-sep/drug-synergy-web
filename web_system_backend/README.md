# Web System Backend

`web_system_backend` is the FastAPI backend for the standalone Web system. It manages datasets, task records, model-version metadata, downloads, and the bridge to `web_system_runtime`.

## Local Development

```powershell
cd D:\codex\bishe_base\web_system_backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 9000
```

The frontend dev server proxies `/api` to `http://127.0.0.1:9000`.

## Container Deployment

The backend runs as `web-backend` in `docker-compose.web.yml`. In container mode it mounts:

- `web_system_runtime` for uploads, outputs, and trained versions
- repo model assets under `/workspace/repo`
- `web_system_backend/data` for SQLite persistence

Start the Web containers with:

```powershell
cd D:\codex\bishe_base
powershell -ExecutionPolicy Bypass -File .\scripts\start_web_system_docker.ps1
```
