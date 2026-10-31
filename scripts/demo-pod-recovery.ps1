<#
.SYNOPSIS
  Task 3 evidence: deletes one FinSecure Pay pod and shows Kubernetes recreating it.
#>
$ns = "finsecure"
Write-Host "=== Pods BEFORE ===" -ForegroundColor Cyan
kubectl -n $ns get pods -l app.kubernetes.io/name=finsecure-pay -o wide

$victim = kubectl -n $ns get pods -l app.kubernetes.io/name=finsecure-pay -o jsonpath='{.items[0].metadata.name}'
Write-Host "`n=== Deleting pod $victim at $(Get-Date -Format o) ===" -ForegroundColor Yellow
kubectl -n $ns delete pod $victim --wait=false

Write-Host "`n=== Watching recovery (Ctrl+C to stop) ===" -ForegroundColor Cyan
for ($i = 0; $i -lt 12; $i++) {
    Start-Sleep -Seconds 5
    Write-Host "--- t+$((($i + 1) * 5))s ---"
    kubectl -n $ns get pods -l app.kubernetes.io/name=finsecure-pay
}
Write-Host "`n=== Deployment status ===" -ForegroundColor Green
kubectl -n $ns get deployment finsecure-pay
kubectl -n $ns get events --sort-by=.lastTimestamp | Select-Object -Last 10
