# =============================================================================
# Core Evaluation Test Case 6 (TC06)
# Test case       : Delete or restart one pod
# Expected result : Kubernetes automatically recreates the pod.
# =============================================================================
$ErrorActionPreference = "Continue"
Write-Host "=== [TC06] Test Case: Delete or restart one pod ===" -ForegroundColor Cyan
Write-Host "Expected Result: Kubernetes automatically recreates the pod.`n"

Write-Host "--- Step 1: Pods BEFORE deletion ---"
kubectl -n finsecure get pods -l app.kubernetes.io/name=finsecure-pay -o wide
$podsBefore = kubectl -n finsecure get pods -l app.kubernetes.io/name=finsecure-pay -o json | ConvertFrom-Json
$runningPod = @($podsBefore.items | Where-Object { $_.status.phase -eq "Running" -and -not $_.metadata.deletionTimestamp })[0]
$victimPod = $runningPod.metadata.name

Write-Host "`nDeleting pod: $victimPod"
kubectl -n finsecure delete pod $victimPod --wait=false

Write-Host "`n--- Step 2: Immediate state after deletion (ReplicaSet spawns replacement pod) ---"
Start-Sleep -Seconds 2
kubectl -n finsecure get pods -l app.kubernetes.io/name=finsecure-pay -o wide

Write-Host "`n--- Step 3: Wait for replacement pod to become Running and 1/1 Ready ---"
kubectl -n finsecure rollout status deployment/finsecure-pay --timeout=120s
if ($LASTEXITCODE -ne 0) {
    Write-Error "TC06 FAILED: Replacement pod did not reach Ready state within timeout."
    exit 1
}

Write-Host "`n--- Step 4: Pods AFTER automatic self-healing recovery ---"
kubectl -n finsecure get pods -l app.kubernetes.io/name=finsecure-pay -o wide

$eksHost = (kubectl -n finsecure get svc finsecure-pay -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>&1 | Out-String).Trim()
$healthResp = (curl.exe -sS --max-time 5 "http://${eksHost}/health" 2>&1 | Out-String).Trim()
Write-Host "`nExternal /health response during/after recovery:"
Write-Host "  $healthResp"

Write-Host "`n[PASS] TC06 Verified: Deleted pod '$victimPod' was automatically recreated by Kubernetes ReplicaSet and reached 1/1 Ready." -ForegroundColor Green
exit 0
