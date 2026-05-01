# Web System Frontend

`web_system_frontend` is the Vue 3 management UI for the standalone Web system. It provides dashboard, dataset management, inference, training, model-version, and run-detail pages.

## Tech Stack

- Vue 3
- TypeScript
- Vite
- Vue Router
- Pinia
- Element Plus

## Local Development

```powershell
cd D:\codex\bishe_base\web_system_frontend
npm install
npm run dev
```

The dev server proxies `/api` to `http://127.0.0.1:9000`.

## Container Deployment

The frontend runs as `web-frontend` in `docker-compose.web.yml`. Vite builds the static assets and Nginx serves them, while `/api` and `/health` are proxied to the backend container.

```powershell
cd D:\codex\bishe_base
powershell -ExecutionPolicy Bypass -File .\scripts\start_web_system_docker.ps1
```
