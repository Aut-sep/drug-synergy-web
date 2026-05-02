param(
    [string]$OutputRoot = "github_upload\drug-synergy-web"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$outputPath = Join-Path $repoRoot $OutputRoot

function Reset-Directory {
    param([string]$Path)

    if (Test-Path $Path) {
        Remove-Item -Recurse -Force $Path
    }
    New-Item -ItemType Directory -Path $Path | Out-Null
}

function Copy-Tree {
    param(
        [string]$Source,
        [string]$Destination,
        [string[]]$ExcludeDirs = @(),
        [string[]]$ExcludeFiles = @()
    )

    $sourcePath = Join-Path $repoRoot $Source
    $destinationPath = Join-Path $outputPath $Destination
    New-Item -ItemType Directory -Force -Path $destinationPath | Out-Null

    $robocopyArgs = @(
        $sourcePath,
        $destinationPath,
        "/E",
        "/NFL",
        "/NDL",
        "/NJH",
        "/NJS",
        "/NP",
        "/R:1",
        "/W:1"
    )

    if ($ExcludeDirs.Count -gt 0) {
        $robocopyArgs += "/XD"
        $robocopyArgs += $ExcludeDirs
    }
    if ($ExcludeFiles.Count -gt 0) {
        $robocopyArgs += "/XF"
        $robocopyArgs += $ExcludeFiles
    }

    & robocopy @robocopyArgs | Out-Null
    if ($LASTEXITCODE -gt 7) {
        throw "robocopy failed for $Source -> $Destination with exit code $LASTEXITCODE"
    }
}

function Remove-TreeIfExists {
    param([string]$RelativePath)

    $targetPath = Join-Path $outputPath $RelativePath
    if (Test-Path $targetPath) {
        Remove-Item -Recurse -Force $targetPath
    }
}

Reset-Directory -Path $outputPath

$rootFiles = @(
    ".gitignore",
    "docker-compose.web.yml",
    "start.bat",
    "start.sh"
)

foreach ($file in $rootFiles) {
    Copy-Item -LiteralPath (Join-Path $repoRoot $file) -Destination (Join-Path $outputPath $file) -Force
}

Copy-Tree -Source "scripts" -Destination "scripts"
Copy-Tree -Source "docs" -Destination "docs"
Copy-Tree -Source "benchmark_factory" -Destination "benchmark_factory" `
    -ExcludeDirs @("__pycache__", "exports", "result_summary", "paper_notes", "ref_paper") `
    -ExcludeFiles @("miniconda.sh", "Miniconda3-latest-Linux-x86_64.sh", "Miniconda3-latest-Linux-x86_64.sh.1")
Copy-Tree -Source "web_system_backend" -Destination "web_system_backend" `
    -ExcludeDirs @("__pycache__", "outputs", "runtime_logs", "data")
Copy-Tree -Source "web_system_frontend" -Destination "web_system_frontend" `
    -ExcludeDirs @("node_modules", "dist", ".vite", "runtime_logs", "output", ".vscode")
Copy-Tree -Source "web_system_runtime" -Destination "web_system_runtime" `
    -ExcludeDirs @("outputs", "runtime_logs", "trained_model_versions", "user_bundles", "workspace")
Copy-Tree -Source "DualSyn" -Destination "DualSyn" `
    -ExcludeDirs @(".git", "DualSyn\save_model", "DualSyn\result", "DualSyn\data\processed", "image")
Copy-Tree -Source "MFSynDCP" -Destination "MFSynDCP" `
    -ExcludeDirs @(".git", "MFSynDCP\result")
Copy-Tree -Source "MVCASyn" -Destination "MVCASyn" `
    -ExcludeDirs @("__pycache__", "results\model", "results\score")
Copy-Tree -Source "MTLSynergy" -Destination "MTLSynergy" `
    -ExcludeDirs @(".git", ".idea", "__pycache__", "save", "result")

$removeAfterCopy = @(
    "DualSyn\DualSyn\save_model",
    "DualSyn\DualSyn\result",
    "DualSyn\DualSyn\data\processed",
    "MFSynDCP\MFSynDCP\result",
    "MVCASyn\results\model",
    "MVCASyn\results\score",
    "MTLSynergy\save",
    "MTLSynergy\result"
)

foreach ($path in $removeAfterCopy) {
    Remove-TreeIfExists -RelativePath $path
}

$placeholderDirs = @(
    "benchmark_factory\env",
    "DualSyn\DualSyn\save_model",
    "MFSynDCP\MFSynDCP\result",
    "MVCASyn\results\model",
    "MTLSynergy\save\AutoEncoder",
    "MTLSynergy\save\MTLSynergy"
)

foreach ($dir in $placeholderDirs) {
    $targetDir = Join-Path $outputPath $dir
    New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
    Set-Content -Path (Join-Path $targetDir ".gitkeep") -Value "" -Encoding utf8
}

$guidePath = Join-Path $outputPath "UPLOAD_GUIDE.md"
$guide = @'
# GitHub Upload Guide

This folder is the GitHub upload package for the standalone web system source code.

## Included

- frontend, backend, runtime, and benchmark source code
- Docker compose and startup scripts
- environment YAML files for inference and training
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
'@
Set-Content -Path $guidePath -Value $guide -Encoding utf8

Write-Host "Prepared GitHub upload folder:"
Write-Host "  $outputPath"
