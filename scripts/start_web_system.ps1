param(
    [switch]$StartTrainingService,
    [switch]$SkipDocker
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$frontendRoot = Join-Path $repoRoot "web_system_frontend"
$backendRoot = Join-Path $repoRoot "web_system_backend"
$composeFile = Join-Path $repoRoot "web_system_runtime\docker-compose.yml"
$dockerDesktopExe = "C:\Program Files\Docker\Docker\Docker Desktop.exe"

function Test-PortListening {
    param([int]$Port)

    $listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    return $null -ne $listener
}

function Wait-HttpReady {
    param(
        [string]$Url,
        [int]$TimeoutSeconds = 60
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -UseBasicParsing $Url -TimeoutSec 4
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
                return $true
            }
        } catch {
        }
        Start-Sleep -Seconds 2
    }

    return $false
}

function Ensure-Directory {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Force $Path | Out-Null
    }
}

function Start-BackgroundCommand {
    param(
        [string]$FilePath,
        [string[]]$ArgumentList,
        [string]$WorkingDirectory,
        [string]$StdoutPath,
        [string]$StderrPath
    )

    Ensure-Directory -Path (Split-Path -Parent $StdoutPath)
    Ensure-Directory -Path (Split-Path -Parent $StderrPath)

    Start-Process `
        -FilePath $FilePath `
        -ArgumentList $ArgumentList `
        -WorkingDirectory $WorkingDirectory `
        -RedirectStandardOutput $StdoutPath `
        -RedirectStandardError $StderrPath `
        -WindowStyle Hidden | Out-Null
}

function Ensure-DockerDesktop {
    if ($SkipDocker) {
        Write-Host "[skip] Docker startup skipped by parameter."
        return
    }

    docker ps | Out-Null 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[ok] Docker daemon is ready."
        return
    }

    if (-not (Test-Path $dockerDesktopExe)) {
        throw "Docker Desktop executable was not found: $dockerDesktopExe"
    }

    Write-Host "[info] Starting Docker Desktop..."
    Start-Process -FilePath $dockerDesktopExe -WindowStyle Hidden | Out-Null

    $deadline = (Get-Date).AddMinutes(3)
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Seconds 3
        docker ps | Out-Null 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[ok] Docker daemon is ready."
            return
        }
    }

    throw "Docker daemon did not become ready within 3 minutes."
}

function Ensure-InferenceStack {
    if ($SkipDocker) {
        return
    }

    if (Test-PortListening -Port 8000) {
        Write-Host "[ok] Inference gateway already listening on 8000."
        return
    }

    Write-Host "[info] Starting inference stack with docker compose..."
    docker compose -f $composeFile up -d --no-build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[warn] Runtime images missing or outdated, retrying with --build..."
        docker compose -f $composeFile up -d --build
        if ($LASTEXITCODE -ne 0) {
            throw "Inference stack failed to start, even after rebuilding images."
        }
    }

    if (-not (Wait-HttpReady -Url "http://127.0.0.1:8000/health" -TimeoutSeconds 90)) {
        throw "Inference gateway did not become ready within 90 seconds."
    }

    Write-Host "[ok] Inference gateway is reachable."
}

function Ensure-Backend {
    if (Test-PortListening -Port 9000) {
        Write-Host "[ok] Backend already listening on 9000."
        return
    }

    Write-Host "[info] Starting backend..."
    Start-BackgroundCommand `
        -FilePath "python" `
        -ArgumentList @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "9000") `
        -WorkingDirectory $backendRoot `
        -StdoutPath (Join-Path $backendRoot "runtime_logs\backend.out.log") `
        -StderrPath (Join-Path $backendRoot "runtime_logs\backend.err.log")
}

function Ensure-Frontend {
    if (Test-PortListening -Port 5173) {
        Write-Host "[ok] Frontend already listening on 5173."
        return
    }

    Write-Host "[info] Starting frontend..."
    Start-BackgroundCommand `
        -FilePath "npm.cmd" `
        -ArgumentList @("run", "dev", "--", "--host", "127.0.0.1", "--port", "5173") `
        -WorkingDirectory $frontendRoot `
        -StdoutPath (Join-Path $frontendRoot "runtime_logs\frontend.out.log") `
        -StderrPath (Join-Path $frontendRoot "runtime_logs\frontend.err.log")
}

function Ensure-TrainingService {
    if (-not $StartTrainingService) {
        Write-Host "[skip] Training service startup skipped."
        return
    }

    if (Test-PortListening -Port 8011) {
        Write-Host "[ok] Training service already listening on 8011."
        return
    }

    Write-Host "[info] Starting training service in WSL..."
    $command = @"
cd /mnt/d/codex/bishe_base/web_system_runtime
export SYNERGY_REPO_ROOT=/mnt/d/codex/bishe_base
export SYNERGY_RUNTIME_ROOT=/mnt/d/codex/bishe_base/web_system_runtime
export SYNERGY_WORKSPACE_ROOT=/mnt/d/codex/bishe_base
export SYNERGY_RUNTIME_MOUNT_ROOT=/workspace/web_system_runtime
export SYNERGY_TRAINED_MODEL_ROOT=/mnt/d/codex/bishe_base/web_system_runtime/trained_model_versions
export SYNERGY_TRAINING_WORK_ROOT=\$HOME/.cache/bishe_training_runs
export SYNERGY_CONDA_EXE=\$HOME/miniconda3/bin/conda
\$HOME/miniconda3/bin/conda run -n trainctl uvicorn service_runtime.training_service:app --host 0.0.0.0 --port 8011 --app-dir /mnt/d/codex/bishe_base/web_system_runtime
"@

    Start-Process `
        -FilePath "wsl.exe" `
        -ArgumentList @("-d", "Ubuntu-22.04", "--", "bash", "-lc", $command) `
        -WindowStyle Hidden | Out-Null
}

Ensure-DockerDesktop
Ensure-InferenceStack
Ensure-Backend
Ensure-Frontend
Ensure-TrainingService

Write-Host ""
Write-Host "Frontend:  http://127.0.0.1:5173"
Write-Host "Backend:   http://127.0.0.1:9000/health"
Write-Host "Gateway:   http://127.0.0.1:8000/health"
Write-Host "Training:  http://127.0.0.1:8011/health"
