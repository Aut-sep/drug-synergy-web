param(
    [switch]$NoBuild
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$composeFile = Join-Path $repoRoot "docker-compose.web.yml"
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

Ensure-DockerReady

$composeArgs = @("compose", "-f", $composeFile, "up", "-d")
$composePreview = "docker compose -f docker-compose.web.yml up -d"
if (-not $NoBuild) {
    $composeArgs += "--build"
    $composePreview += " --build"
}

Write-Host "[info] Starting Web frontend/backend containers..."
Write-Host "[info] Running: $composePreview"
docker @composeArgs

Write-Host ""
Write-Host "Web frontend: http://127.0.0.1:5173"
Write-Host "Web backend:  http://127.0.0.1:9000/health"
Write-Host "Gateway:       http://127.0.0.1:8000/health"
Write-Host "Training:      http://127.0.0.1:8011/health"
Write-Host ""
Write-Host "This compose file now includes the inference runtime and training service alongside the web frontend/backend."
