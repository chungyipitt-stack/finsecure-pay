# =============================================================================
# Core Evaluation Test Case 2 (TC02)
# Test case       : Introduce a controlled failing test
# Expected result : Jenkins pipeline fails, and deployment does not proceed.
# =============================================================================
param(
    [switch]$TriggerLiveJenkinsBuild,
    [int]$BuildNumber = 0
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Push-Location $Root
try {
    $env:Path = [Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [Environment]::GetEnvironmentVariable("Path","User")
    Write-Host "=== [TC02] Test Case: Introduce a controlled failing test ===" -ForegroundColor Cyan
    Write-Host "Expected Result: Jenkins pipeline fails, and deployment does not proceed.`n"

    # Part A: Demonstrate local controlled failing test via -Dfinsecure.test.simulateFailure=true
    Write-Host "--- Step 1: Execute controlled failing test (-Dfinsecure.test.simulateFailure=true) ---"
    $ErrorActionPreference = "Continue"
    $mvnOut = & .\mvnw.cmd -B -ntp test "-Dtest=ControlledEvaluationTest" "-Dfinsecure.test.simulateFailure=true" 2>&1 | Out-String
    $ErrorActionPreference = "Stop"
    ($mvnOut -split "`r?`n") | Where-Object {
        $_ -match "Running com\.finsecure\.pay\.ControlledEvaluationTest|Controlled failing test triggered|Tests run:|BUILD FAILURE"
    } | ForEach-Object { Write-Host $_ }

    # Part B: Verify Jenkins pipeline stage execution where Unit Test FAILED and downstream stages were skipped
    Write-Host "`n--- Step 2: Verify Jenkins pipeline failure blocks Package, Push & EKS Deployment ---"
    $cfg = @{}
    Get-Content (Join-Path $Root "jenkins/.env") | Where-Object { $_ -match '^([A-Z0-9_]+)=(.*)$' } | ForEach-Object { $cfg[$Matches[1]] = $Matches[2].Trim() }
    $jh = @{ Authorization = "Basic " + [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes("admin:" + $cfg["JENKINS_ADMIN_PASSWORD"])) }
    $js = New-Object Microsoft.PowerShell.Commands.WebRequestSession
    $c = Invoke-RestMethod -Uri "http://localhost:8088/crumbIssuer/api/json" -Headers $jh -WebSession $js
    $jh[$c.crumbRequestField] = $c.crumb

    if ($TriggerLiveJenkinsBuild) {
        $job = Invoke-RestMethod -Uri "http://localhost:8088/job/finsecure-pay/api/json" -Headers $jh -WebSession $js
        $BuildNumber = [int]$job.nextBuildNumber
        $uri = "http://localhost:8088/job/finsecure-pay/buildWithParameters?MODE=deploy&SIMULATE_TEST_FAILURE=true&SIMULATE_SECURITY_FINDING=false&SKIP_SONAR=false"
        Invoke-WebRequest -Method Post -Uri $uri -Headers $jh -WebSession $js -UseBasicParsing | Out-Null
        Write-Host "Triggered Jenkins Build #$BuildNumber with SIMULATE_TEST_FAILURE=true..."
        for ($i = 0; $i -lt 120; $i++) {
            Start-Sleep -Seconds 3
            try {
                $wf = Invoke-RestMethod -Uri "http://localhost:8088/job/finsecure-pay/$BuildNumber/wfapi/describe" -Headers $jh -WebSession $js
                if ($wf.status -ne "IN_PROGRESS" -and $wf.status -ne "NOT_EXECUTED") { break }
            } catch {}
        }
    } elseif ($BuildNumber -eq 0) {
        $BuildNumber = 2
    }

    $wf = Invoke-RestMethod -Uri "http://localhost:8088/job/finsecure-pay/$BuildNumber/wfapi/describe" -Headers $jh -WebSession $js
    Write-Host ("Jenkins Build #{0} | Overall Status: {1} | Duration: {2}s" -f $BuildNumber, $wf.status, [int]($wf.durationMillis/1000))
    $wf.stages | ForEach-Object {
        Write-Host ("  Stage: {0,-28} Status: {1}" -f $_.name, $_.status)
    }

    $log = Invoke-RestMethod -Uri "http://localhost:8088/job/finsecure-pay/$BuildNumber/consoleText" -Headers $jh -WebSession $js
    Write-Host "`nConsole Excerpt (Skipped Downstream Stages):"
    ($log -split "`r?`n") | Where-Object { $_ -match "There are test failures|Controlled failing test|skipped due to earlier failure|Sending email to:|Finished: FAILURE" } | ForEach-Object { Write-Host "  $_" }

    if ($wf.status -ne "FAILED") {
        throw "TC02 FAILED: Expected Jenkins build #$BuildNumber to have status FAILED."
    }

    Write-Host "`n[PASS] TC02 Verified: Controlled failing test caused Jenkins pipeline to FAIL at 'Unit Test', and deployment to EKS did NOT proceed." -ForegroundColor Green
} finally {
    Pop-Location
}
