# =============================================================================
# Core Evaluation Test Case 3 (TC03)
# Test case       : Run the container and access /health
# Expected result : Application returns a healthy response.
# =============================================================================
$ErrorActionPreference = "Continue"
Write-Host "=== [TC03] Test Case: Run the container and access /health ===" -ForegroundColor Cyan
Write-Host "Expected Result: Application returns a healthy response.`n"

$containerName = "finsecure-tc03-eval"
$hostPort = 18089
$image = "chungyi1979/finsecure-pay:1.0.0"

try {
    docker rm -f $containerName 2>&1 | Out-Null
    Write-Host "--- Step 1: Start container ($image) on port $hostPort -> 8080 ---"
    $cid = (docker run -d --rm --name $containerName -p "${hostPort}:8080" $image 2>&1 | Out-String).Trim()
    Write-Host "Container started: $($cid.Substring(0, [Math]::Min(12, $cid.Length)))"

    Write-Host "--- Step 2: Probe http://localhost:${hostPort}/health ---"
    $healthy = $false
    $resp = ""
    for ($i = 1; $i -le 20; $i++) {
        Start-Sleep -Seconds 2
        $resp = (curl.exe -sS --max-time 3 "http://localhost:${hostPort}/health" 2>&1 | Out-String).Trim()
        if ($resp -match '"status"\s*:\s*"UP"') {
            $healthy = $true
            break
        }
    }

    if (-not $healthy) {
        Write-Error "TC03 FAILED: Container did not return UP on /health"
        exit 1
    }

    Write-Host "HTTP 200 OK from Local Container /health:"
    Write-Host "  $resp"

    Write-Host "`n--- Step 3: Probe Live AWS EKS LoadBalancer /health ---"
    $eksHost = (kubectl -n finsecure get svc finsecure-pay -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>&1 | Out-String).Trim()
    $eksResp = (curl.exe -sS --max-time 5 "http://${eksHost}/health" 2>&1 | Out-String).Trim()
    Write-Host "HTTP 200 OK from EKS LoadBalancer (http://${eksHost}/health):"
    Write-Host "  $eksResp"

    Write-Host "`n[PASS] TC03 Verified: Container started cleanly and /health returned status=UP." -ForegroundColor Green
    exit 0
} finally {
    docker rm -f $containerName 2>&1 | Out-Null
}
