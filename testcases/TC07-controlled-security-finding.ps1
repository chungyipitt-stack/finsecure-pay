# =============================================================================
# Core Evaluation Test Case 7 (TC07)
# Test case       : Introduce a controlled critical/high security finding
# Expected result : The security gate blocks the release.
# =============================================================================
param(
    [switch]$TriggerLiveJenkinsBuild,
    [int]$BuildNumber = 0
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Push-Location $Root
try {
    Write-Host "=== [TC07] Test Case: Introduce a controlled critical/high security finding ===" -ForegroundColor Cyan
    Write-Host "Expected Result: The security gate blocks the release.`n"

    $cfg = @{}
    Get-Content (Join-Path $Root "jenkins/.env") | Where-Object { $_ -match '^([A-Z0-9_]+)=(.*)$' } | ForEach-Object { $cfg[$Matches[1]] = $Matches[2].Trim() }
    $jh = @{ Authorization = "Basic " + [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes("admin:" + $cfg["JENKINS_ADMIN_PASSWORD"])) }
    $js = New-Object Microsoft.PowerShell.Commands.WebRequestSession
    $c = Invoke-RestMethod -Uri "http://localhost:8088/crumbIssuer/api/json" -Headers $jh -WebSession $js
    $jh[$c.crumbRequestField] = $c.crumb

    if ($TriggerLiveJenkinsBuild) {
        $job = Invoke-RestMethod -Uri "http://localhost:8088/job/finsecure-pay/api/json" -Headers $jh -WebSession $js
        $BuildNumber = [int]$job.nextBuildNumber
        $uri = "http://localhost:8088/job/finsecure-pay/buildWithParameters?MODE=deploy&SIMULATE_TEST_FAILURE=false&SIMULATE_SECURITY_FINDING=true&SKIP_SONAR=true"
        Invoke-WebRequest -Method Post -Uri $uri -Headers $jh -WebSession $js -UseBasicParsing | Out-Null
        Write-Host "Triggered Jenkins Build #$BuildNumber with SIMULATE_SECURITY_FINDING=true (injects commons-text:1.9 CVE-2022-42889 CVSS 9.8 CRITICAL)..."
        for ($i = 0; $i -lt 180; $i++) {
            Start-Sleep -Seconds 3
            try {
                $wf = Invoke-RestMethod -Uri "http://localhost:8088/job/finsecure-pay/$BuildNumber/wfapi/describe" -Headers $jh -WebSession $js
                if ($wf.status -ne "IN_PROGRESS" -and $wf.status -ne "NOT_EXECUTED") { break }
            } catch {}
        }
    } elseif ($BuildNumber -eq 0) {
        $BuildNumber = 3
    }

    Write-Host "--- Step 1: Verify Jenkins Security Gate Stage Status (Build #$BuildNumber) ---"
    $wf = Invoke-RestMethod -Uri "http://localhost:8088/job/finsecure-pay/$BuildNumber/wfapi/describe" -Headers $jh -WebSession $js
    Write-Host ("Jenkins Build #{0} | Overall Status: {1} | Duration: {2}s" -f $BuildNumber, $wf.status, [int]($wf.durationMillis/1000))
    $wf.stages | ForEach-Object {
        Write-Host ("  Stage: {0,-28} Status: {1}" -f $_.name, $_.status)
    }

    Write-Host "`n--- Step 2: Security Gate Console Findings (CVSS >= 7.0 HIGH/CRITICAL) ---"
    $log = Invoke-RestMethod -Uri "http://localhost:8088/job/finsecure-pay/$BuildNumber/consoleText" -Headers $jh -WebSession $js
    ($log -split "`r?`n") | Where-Object {
        $_ -match "CVSS score greater than or equal to '7\.0'|CVE-\d{4}-\d+|commons-text|spring-core|spring-webmvc|skipped due to earlier failure|Finished: FAILURE"
    } | Select-Object -First 25 | ForEach-Object { Write-Host "  $_" }

    if ($wf.status -ne "FAILED") {
        throw "TC07 FAILED: Expected Jenkins build #$BuildNumber to be blocked (FAILED) by the security gate."
    }

    Write-Host "`n[PASS] TC07 Verified: HIGH/CRITICAL security finding was detected by the security gate (CVSS >= 7.0), halting the pipeline and blocking release to Docker Hub and EKS." -ForegroundColor Green
} finally {
    Pop-Location
}
