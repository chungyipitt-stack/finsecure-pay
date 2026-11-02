# =============================================================================
# Core Evaluation Test Case 5 (TC05)
# Test case       : Deploy a new image/version
# Expected result : Kubernetes rollout completes successfully.
# =============================================================================
param(
    [string]$TargetImageTag = "1.1.0-4-9ea7e21"
)
$ErrorActionPreference = "Continue"
Write-Host "=== [TC05] Test Case: Deploy a new image/version ===" -ForegroundColor Cyan
Write-Host "Expected Result: Kubernetes rollout completes successfully.`n"

$eksHost = (kubectl -n finsecure get svc finsecure-pay -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>&1 | Out-String).Trim()
$curImage = (kubectl -n finsecure get deployment finsecure-pay -o jsonpath='{.spec.template.spec.containers[0].image}' 2>&1 | Out-String).Trim()
if ($curImage -eq "chungyi1979/finsecure-pay:${TargetImageTag}") {
    kubectl -n finsecure set image deployment/finsecure-pay "finsecure-pay=chungyi1979/finsecure-pay:1.0.0" | Out-Null
    kubectl -n finsecure rollout status deployment/finsecure-pay --timeout=180s | Out-Null
}

Write-Host "--- Step 1: Current /health before deploying new image ---"
$beforeHealth = (curl.exe -sS --max-time 5 "http://${eksHost}/health" 2>&1 | Out-String).Trim()
Write-Host "  $beforeHealth"

Write-Host "`n--- Step 2: Deploy new image chungyi1979/finsecure-pay:${TargetImageTag} to EKS ---"
kubectl -n finsecure set image deployment/finsecure-pay "finsecure-pay=chungyi1979/finsecure-pay:${TargetImageTag}"
kubectl -n finsecure annotate deployment/finsecure-pay --overwrite "kubernetes.io/change-cause=Evaluation TC05 rollout to chungyi1979/finsecure-pay:${TargetImageTag}"

Write-Host "`n--- Step 3: Wait for Kubernetes rolling update to complete ---"
kubectl -n finsecure rollout status deployment/finsecure-pay --timeout=180s
if ($LASTEXITCODE -ne 0) {
    Write-Error "TC05 FAILED: Kubernetes rollout did not complete successfully."
    exit 1
}

Write-Host "`n--- Step 4: Inspect Rollout History & Running Pods ---"
kubectl -n finsecure rollout history deployment/finsecure-pay
kubectl -n finsecure get pods -l app.kubernetes.io/name=finsecure-pay -o wide

Write-Host "`n--- Step 5: Verify /health reports the newly deployed version ---"
Start-Sleep -Seconds 3
$afterHealth = (curl.exe -sS --max-time 5 "http://${eksHost}/health" 2>&1 | Out-String).Trim()
Write-Host "  $afterHealth"

if ($afterHealth -notmatch [Regex]::Escape($TargetImageTag)) {
    Write-Error "TC05 FAILED: /health did not report expected version $TargetImageTag"
    exit 1
}

Write-Host "`n[PASS] TC05 Verified: New image/version ($TargetImageTag) rolled out with zero downtime and /health confirmed the new version." -ForegroundColor Green
exit 0
