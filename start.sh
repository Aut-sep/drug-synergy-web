#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

export WEB_SYSTEM_REPO_ROOT="$SCRIPT_DIR"
export WEB_SYSTEM_RUNTIME_ROOT="$SCRIPT_DIR/web_system_runtime"
export WEB_SYSTEM_WORKSPACE_ROOT="$SCRIPT_DIR"
export WEB_SYSTEM_BACKEND_HOST="${WEB_SYSTEM_BACKEND_HOST:-0.0.0.0}"
export WEB_SYSTEM_BACKEND_PORT="${WEB_SYSTEM_BACKEND_PORT:-9000}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"
export VITE_API_TARGET="${VITE_API_TARGET:-http://127.0.0.1:${WEB_SYSTEM_BACKEND_PORT}}"
export WEB_SYSTEM_CORS_ORIGINS="${WEB_SYSTEM_CORS_ORIGINS:-http://127.0.0.1:${FRONTEND_PORT},http://localhost:${FRONTEND_PORT}}"
export WEB_SYSTEM_GATEWAY_URL="${WEB_SYSTEM_GATEWAY_URL:-http://127.0.0.1:8000}"
export WEB_SYSTEM_TRAINING_URL="${WEB_SYSTEM_TRAINING_URL:-http://127.0.0.1:8011}"
export SYNERGY_REPO_ROOT="$SCRIPT_DIR"
export SYNERGY_RUNTIME_ROOT="$SCRIPT_DIR/web_system_runtime"
export SYNERGY_WORKSPACE_ROOT="$SCRIPT_DIR"
export SYNERGY_RUNTIME_MOUNT_ROOT="${SYNERGY_RUNTIME_MOUNT_ROOT:-/workspace/web_system_runtime}"
export SYNERGY_TRAINED_MODEL_ROOT="${SYNERGY_TRAINED_MODEL_ROOT:-$SCRIPT_DIR/web_system_runtime/trained_model_versions}"
export SYNERGY_TRAINING_WORK_ROOT="${SYNERGY_TRAINING_WORK_ROOT:-$HOME/.cache/bishe_training_runs}"

BACKEND_DIR="$SCRIPT_DIR/web_system_backend"
FRONTEND_DIR="$SCRIPT_DIR/web_system_frontend"
RUNTIME_DIR="$SCRIPT_DIR/web_system_runtime"
START_TRAINING_SERVICE="${START_TRAINING_SERVICE:-0}"

for arg in "$@"; do
    case "$arg" in
        --with-training)
            START_TRAINING_SERVICE=1
            ;;
    esac
done

PYTHON=""
for candidate in python3 python; do
    if command -v "$candidate" &>/dev/null; then
        if "$candidate" -c "import fastapi" 2>/dev/null; then
            PYTHON="$candidate"
            break
        elif "$candidate" -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
            PYTHON="$candidate"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo -e "${RED}Error: No suitable Python (3.10+) found.${NC}"
    echo "Install Python 3.10+ and pip install fastapi uvicorn sqlalchemy requests python-multipart pandas"
    exit 1
fi

wait_http_ready() {
    local url="$1"
    local timeout="${2:-60}"
    local start_time
    start_time="$(date +%s)"

    while [ $(( "$(date +%s)" - start_time )) -lt "$timeout" ]; do
        if command -v curl >/dev/null 2>&1; then
            if curl -fsS "$url" >/dev/null 2>&1; then
                return 0
            fi
        elif command -v wget >/dev/null 2>&1; then
            if wget -qO- "$url" >/dev/null 2>&1; then
                return 0
            fi
        fi
        sleep 2
    done

    return 1
}

cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down local app processes...${NC}"
    [ -n "${BACKEND_PID:-}" ] && kill "$BACKEND_PID" 2>/dev/null || true
    [ -n "${FRONTEND_PID:-}" ] && kill "$FRONTEND_PID" 2>/dev/null || true
    [ -n "${TRAINING_PID:-}" ] && kill "$TRAINING_PID" 2>/dev/null || true
    echo -e "${GREEN}Done.${NC}"
}
trap cleanup EXIT INT TERM

echo -e "${GREEN}[1/5] Starting inference runtime...${NC}"
docker compose -f "$SCRIPT_DIR/web_system_runtime/docker-compose.yml" up -d --build
if ! wait_http_ready "http://127.0.0.1:8000/health" 120; then
    echo -e "${RED}Inference gateway did not become ready at http://127.0.0.1:8000/health${NC}"
    exit 1
fi

echo -e "${GREEN}[2/5] Checking backend dependencies...${NC}"
cd "$BACKEND_DIR"
if ! "$PYTHON" -c "import fastapi, uvicorn, sqlalchemy" 2>/dev/null; then
    echo "  Installing Python dependencies..."
    if [ ! -d "venv" ] && [ "${USE_VENV:-1}" != "0" ]; then
        "$PYTHON" -m venv venv
        source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null || true
        PYTHON="python"
    fi
    pip install -q -r requirements.txt
fi

echo -e "${GREEN}[3/5] Checking frontend dependencies...${NC}"
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    echo "  Installing Node.js dependencies..."
    npm install --silent
fi

echo -e "${GREEN}[4/5] Starting backend on http://${WEB_SYSTEM_BACKEND_HOST}:${WEB_SYSTEM_BACKEND_PORT} ...${NC}"
cd "$BACKEND_DIR"
"$PYTHON" -m uvicorn app.main:app \
    --host "$WEB_SYSTEM_BACKEND_HOST" \
    --port "$WEB_SYSTEM_BACKEND_PORT" \
    --reload &
BACKEND_PID=$!
if ! wait_http_ready "http://127.0.0.1:${WEB_SYSTEM_BACKEND_PORT}/health" 60; then
    echo -e "${RED}Backend did not become ready at http://127.0.0.1:${WEB_SYSTEM_BACKEND_PORT}/health${NC}"
    exit 1
fi

if [ "$START_TRAINING_SERVICE" = "1" ]; then
    echo -e "${GREEN}[5/5] Starting optional training service on http://127.0.0.1:8011 ...${NC}"
    cd "$RUNTIME_DIR"
    "$PYTHON" -m uvicorn service_runtime.training_service:app \
        --app-dir "$RUNTIME_DIR" \
        --host 0.0.0.0 \
        --port 8011 &
    TRAINING_PID=$!
else
    echo -e "${GREEN}[5/5] Starting frontend on http://localhost:${FRONTEND_PORT} ...${NC}"
fi

cd "$FRONTEND_DIR"
npx vite --port "$FRONTEND_PORT" --host &
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}System is starting.${NC}"
echo -e "Frontend: ${YELLOW}http://localhost:${FRONTEND_PORT}${NC}"
echo -e "Backend:  ${YELLOW}http://127.0.0.1:${WEB_SYSTEM_BACKEND_PORT}/health${NC}"
echo -e "Gateway:  ${YELLOW}http://127.0.0.1:8000/health${NC}"
if [ "$START_TRAINING_SERVICE" = "1" ]; then
    echo -e "Training: ${YELLOW}http://127.0.0.1:8011/health${NC}"
else
    echo -e "Training: ${YELLOW}disabled by default${NC} (pass --with-training to enable)"
fi
echo ""
echo -e "Press ${RED}Ctrl+C${NC} to stop the local frontend/backend/training processes."
echo -e "Docker runtime containers stay managed by docker compose."
echo ""

wait
