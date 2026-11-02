# =============================================================================
# Core Evaluation Test Case 1 (TC01)
# Test case       : Run unit tests
# Expected result : Required unit tests pass.
# =============================================================================
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
Push-Location $Root
try {
    $env:Path = [Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [Environment]::GetEnvironmentVariable("Path","User")
    $env:FINSECURE_API_KEY = ""

    Write-Host "=== [TC01] Test Case: Run unit tests ===" -ForegroundColor Cyan
    Write-Host "Expected Result: Required unit tests pass.`n"

    $output = & .\mvnw.cmd -B -ntp test 2>&1 | Out-String
    $exitCode = $LASTEXITCODE
    $summaryLines = ($output -split "`r?`n") | Where-Object {
        $_ -match "Running com\.finsecure\.pay|Tests run:|BUILD SUCCESS|BUILD FAILURE"
    }
    $summaryLines | ForEach-Object { Write-Host $_ }

    if ($exitCode -ne 0 -or $output -notmatch "BUILD SUCCESS") {
        Write-Error "TC01 FAILED: Unit tests did not pass."
        exit 1
    }

    Write-Host "`n[PASS] TC01 Verified: All 50 required unit tests passed (0 failures, 0 errors)." -ForegroundColor Green
    exit 0
} finally {
    Pop-Location
}
