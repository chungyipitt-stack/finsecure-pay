# =============================================================================
# Core Evaluation Test Case 4 (TC04)
# Test case       : Inspect the Kubernetes deployment
# Expected result : At least two application pods are running and Ready.
# =============================================================================
$ErrorActionPreference = "Continue"
Write-Host "=== [TC04] Test Case: Inspect the Kubernetes deployment ===" -ForegroundColor Cyan
Write-Host "Expected Result: At least two application pods are running and Ready.`n"

Write-Host "--- Step 1: Inspect Deployment in namespace 'finsecure' ---"
kubectl -n finsecure get deployment finsecure-pay -o wide

Write-Host "`n--- Step 2: Inspect Application Pods in namespace 'finsecure' ---"
kubectl -n finsecure get pods -l app.kubernetes.io/name=finsecure-pay -o wide

$deployJson = kubectl -n finsecure get deployment finsecure-pay -o json | ConvertFrom-Json
$readyReplicas = [int]$deployJson.status.readyReplicas
$availableReplicas = [int]$deployJson.status.availableReplicas

$podsJson = kubectl -n finsecure get pods -l app.kubernetes.io/name=finsecure-pay -o json | ConvertFrom-Json
$runningReadyPods = @($podsJson.items | Where-Object {
    $_.status.phase -eq "Running" -and @($_.status.containerStatuses | Where-Object { $_.ready -eq $true }).Count -ge 1
})

Write-Host "`nDeployment Summary: desired=$($deployJson.spec.replicas), readyReplicas=$readyReplicas, availableReplicas=$availableReplicas, runningReadyPodCount=$($runningReadyPods.Count)"

if ($readyReplicas -lt 2 -or $runningReadyPods.Count -lt 2) {
    Write-Error "TC04 FAILED: Expected at least 2 running and Ready pods, found $($runningReadyPods.Count)."
    exit 1
}

Write-Host "`n[PASS] TC04 Verified: $($runningReadyPods.Count) application pods are Running and Ready (>= 2 required)." -ForegroundColor Green
exit 0
