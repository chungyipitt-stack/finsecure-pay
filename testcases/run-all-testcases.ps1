# =============================================================================
# FinSecure Pay - Master Core Evaluation Test Case Runner (TC01 - TC08)
# Executes all 8 Core Test Cases from testcases/testcase_expected_result.jpg
# and saves timestamped verification logs under testcases/results/.
# =============================================================================
$ErrorActionPreference = "Continue"
$ResultsDir = Join-Path $PSScriptRoot "results"
New-Item -ItemType Directory -Force $ResultsDir | Out-Null

$TestSuite = @(
    @{ Id = "TC01"; Script = "TC01-run-unit-tests.ps1";              Log = "TC01-unit-tests.txt";              Case = "Run unit tests";                                        Expected = "Required unit tests pass." },
    @{ Id = "TC02"; Script = "TC02-controlled-failing-test.ps1";     Log = "TC02-controlled-failing-test.txt"; Case = "Introduce a controlled failing test";                   Expected = "Jenkins pipeline fails, and deployment does not proceed." },
    @{ Id = "TC03"; Script = "TC03-container-health.ps1";            Log = "TC03-container-health.txt";        Case = "Run the container and access /health";                  Expected = "Application returns a healthy response." },
    @{ Id = "TC04"; Script = "TC04-inspect-k8s-deployment.ps1";      Log = "TC04-inspect-k8s-deployment.txt";  Case = "Inspect the Kubernetes deployment";                     Expected = "At least two application pods are running and Ready." },
    @{ Id = "TC05"; Script = "TC05-deploy-new-version.ps1";          Log = "TC05-deploy-new-version.txt";      Case = "Deploy a new image/version";                            Expected = "Kubernetes rollout completes successfully." },
    @{ Id = "TC06"; Script = "TC06-delete-pod-self-healing.ps1";     Log = "TC06-delete-pod-self-healing.txt"; Case = "Delete or restart one pod";                             Expected = "Kubernetes automatically recreates the pod." },
    @{ Id = "TC07"; Script = "TC07-controlled-security-finding.ps1"; Log = "TC07-controlled-security-gate.txt";Case = "Introduce a controlled critical/high security finding"; Expected = "The security gate blocks the release." },
    @{ Id = "TC08"; Script = "TC08-trigger-monitoring-alert.ps1";    Log = "TC08-trigger-monitoring-alert.txt";Case = "Trigger a monitoring condition";                        Expected = "Alert fires and a notification is received." }
)

$Summary = @()
foreach ($tc in $TestSuite) {
    $scriptPath = Join-Path $PSScriptRoot $tc.Script
    $logPath = Join-Path $ResultsDir $tc.Log
    Write-Host "`n================================================================================" -ForegroundColor Yellow
    Write-Host "Running $($tc.Id): $($tc.Case)" -ForegroundColor Yellow
    Write-Host "================================================================================" -ForegroundColor Yellow
    $out = & powershell -NoProfile -ExecutionPolicy Bypass -File $scriptPath 2>&1 | Out-String
    $code = $LASTEXITCODE
    Write-Host $out
    [System.IO.File]::WriteAllText($logPath, $out.Trim() + "`n", (New-Object System.Text.UTF8Encoding($false)))
    $status = if ($code -eq 0 -and $out -match "\[PASS\]") { "PASS" } else { "FAIL" }
    $Summary += [PSCustomObject]@{
        ID             = $tc.Id
        TestCase       = $tc.Case
        ExpectedResult = $tc.Expected
        Status         = $status
        ResultLog      = "testcases/results/$($tc.Log)"
    }
}

Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "CORE EVALUATION TEST CASES SUMMARY (8/8)" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
$Summary | Format-Table -AutoSize
