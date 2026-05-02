param(
    [switch]$StartTrainingService
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$cachedRuntimeComposeFile = Join-Path $repoRoot "web_system_runtime\docker-compose.cached.yml"
$dockerDesktopExe = "C:\Program Files\Docker\Docker\Docker Desktop.exe"

function Ensure-DockerReady {
    docker ps | Out-Null 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[ok] Docker daemon is ready."
        return
    }

    if (Test-Path $dockerDesktopExe) {
        Write-Host "[info] Starting Docker Desktop..."
        Start-Process -FilePath $dockerDesktopExe -WindowStyle Hidden | Out-Null
    }

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

function Ensure-CachedRuntimeImages {
    $requiredImages = @(
        "streamlit_system-gateway:latest",
        "streamlit_system-dualsyn-service:latest",
        "streamlit_system-mfsyndcp-service:latest",
        "streamlit_system-mvcasyn-service:latest",
        "streamlit_system-mtlsynergy-service:latest"
    )

    $missing = @()
    foreach ($image in $requiredImages) {
        docker image inspect $image | Out-Null 2>$null
        if ($LASTEXITCODE -ne 0) {
            $missing += $image
        }
    }

    if ($missing.Count -gt 0) {
        throw "Cached runtime images are missing: $($missing -join ', ')"
    }
}

function Start-CachedRuntime {
    if (-not (Test-Path $cachedRuntimeComposeFile)) {
        throw "Cached runtime compose file not found: $cachedRuntimeComposeFile"
    }

    Ensure-CachedRuntimeImages

    Write-Host "[info] Starting cached runtime services from current compatibility compose..."
    docker compose -f $cachedRuntimeComposeFile up -d gateway dualsyn-service mfsyndcp-service mvcasyn-service mtlsynergy-service

    if ($LASTEXITCODE -ne 0) {
        throw "Failed to start cached runtime services."
    }
}

Ensure-DockerReady
Start-CachedRuntime

$startArgs = @(
    "-ExecutionPolicy", "Bypass",
    "-File", (Join-Path $repoRoot "scripts\start_web_system.ps1"),
    "-SkipDocker"
)

if ($StartTrainingService) {
    $startArgs += "-StartTrainingService"
}

Write-Host "[info] Starting current web frontend/backend against cached runtime..."
powershell @startArgs
