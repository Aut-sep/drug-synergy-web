param(
    [int]$TimeoutSeconds = 6
)

$ErrorActionPreference = "Stop"

$targets = @(
    @{ Name = "frontend"; Url = "http://127.0.0.1:5173"; Required = $true },
    @{ Name = "backend_health"; Url = "http://127.0.0.1:9000/health"; Required = $true },
    @{ Name = "system_summary"; Url = "http://127.0.0.1:9000/api/system/summary"; Required = $true },
    @{ Name = "gateway_health"; Url = "http://127.0.0.1:8000/health"; Required = $true },
    @{ Name = "training_health"; Url = "http://127.0.0.1:8011/health"; Required = $false }
)

$results = foreach ($target in $targets) {
    try {
        $response = Invoke-WebRequest -UseBasicParsing $target.Url -TimeoutSec $TimeoutSeconds
        [pscustomobject]@{
            name = $target.Name
            required = $target.Required
            ok = $true
            status = $response.StatusCode
            url = $target.Url
            note = ""
        }
    } catch {
        [pscustomobject]@{
            name = $target.Name
            required = $target.Required
            ok = $false
            status = "-"
            url = $target.Url
            note = $_.Exception.Message
        }
    }
}

$results | Format-Table -AutoSize

$requiredFailures = $results | Where-Object { $_.required -and -not $_.ok }
if ($requiredFailures) {
    exit 1
}
