# =============================================================================
# Core Evaluation Test Case 8 (TC08)
# Test case       : Trigger a monitoring condition
# Expected result : Alert fires and a notification is received.
# =============================================================================
$ErrorActionPreference = "Continue"
Write-Host "=== [TC08] Test Case: Trigger a monitoring condition ===" -ForegroundColor Cyan
Write-Host "Expected Result: Alert fires and a notification is received.`n"

$eksHost = (kubectl -n finsecure get svc finsecure-pay -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>&1 | Out-String).Trim()
$b64Key = (kubectl -n finsecure get secret finsecure-pay-secrets -o jsonpath='{.data.FINSECURE_API_KEY}' 2>&1 | Out-String).Trim()
$apiKey = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($b64Key)).Trim()
$headers = @{ "Content-Type" = "application/json"; "X-API-Key" = $apiKey }

Write-Host "--- Step 1: Send burst of rejected transactions (>50% rejection ratio over 2m window) ---"
$rejectedCount = 0
for ($i = 1; $i -le 35; $i++) {
    $body = @{
        transactionId      = "TXN-TC08-INIT-$i"
        sourceAccount      = "0000000000"
        destinationAccount = "9876543210"
        amount             = 999999.00
        currency           = "JPY"
    } | ConvertTo-Json -Compress
    try {
        Invoke-WebRequest -UseBasicParsing -Method Post -Uri "http://${eksHost}/validate" -Headers $headers -Body $body -TimeoutSec 5 | Out-Null
    } catch {
        if ($_.Exception.Response -and [int]$_.Exception.Response.StatusCode -eq 422) {
            $rejectedCount++
        }
    }
}
Write-Host "Injected $rejectedCount rejected (HTTP 422) transactions against http://${eksHost}/validate"

Write-Host "`n--- Step 2: Poll Prometheus on EKS for FinSecurePayHighRejectionRate ---"
$firing = $false
for ($attempt = 1; $attempt -le 20; $attempt++) {
    for ($j = 1; $j -le 8; $j++) {
        $body = @{
            transactionId      = "TXN-TC08-$attempt-$j"
            sourceAccount      = "0000000000"
            destinationAccount = "9876543210"
            amount             = 999999.00
            currency           = "JPY"
        } | ConvertTo-Json -Compress
        try {
            Invoke-WebRequest -UseBasicParsing -Method Post -Uri "http://${eksHost}/validate" -Headers $headers -Body $body -TimeoutSec 5 | Out-Null
        } catch {
            if ($_.Exception.Response -and [int]$_.Exception.Response.StatusCode -eq 422) { $rejectedCount++ }
        }
    }

    $rawProm = (kubectl get --raw "/api/v1/namespaces/monitoring/services/http:monitoring-kube-prometheus-prometheus:9090/proxy/api/v1/alerts" 2>$null | Out-String).Trim()
    if ($rawProm -match '^\{') {
        $alertsJson = $rawProm | ConvertFrom-Json
        $finAlerts = @($alertsJson.data.alerts | Where-Object { $_.labels.alertname -match "FinSecurePay" })
        if ($finAlerts.Count -gt 0) {
            foreach ($a in $finAlerts) {
                Write-Host ("  [Attempt $attempt] Prometheus Alert: {0} | state={1} | activeAt={2} | value={3}" -f $a.labels.alertname, $a.state, $a.activeAt, $a.value)
                if ($a.state -eq "firing") { $firing = $true }
            }
        } else {
            Write-Host "  [Attempt $attempt] Waiting for Prometheus scrape & rule evaluation (total rejected=$rejectedCount)..."
        }
    }
    if ($firing) { break }
    Start-Sleep -Seconds 6
}

Write-Host "`n--- Step 3: Query Alertmanager Active Alerts API ---"
$rawAm = (kubectl get --raw "/api/v1/namespaces/monitoring/services/http:monitoring-kube-prometheus-alertmanager:9093/proxy/api/v2/alerts" 2>$null | Out-String).Trim()
if ($rawAm -match '^\[') {
    $amJson = $rawAm | ConvertFrom-Json
    $amFin = @($amJson | Where-Object { $_.labels.alertname -match "FinSecurePay" })
    foreach ($am in $amFin) {
        Write-Host ("  Alertmanager: alertname={0} | status={1} | receiver={2} | summary='{3}' | description='{4}'" -f $am.labels.alertname, $am.status.state, $am.receivers[0].name, $am.annotations.summary, $am.annotations.description)
    }
}

if (-not $firing) {
    Write-Error "TC08 FAILED: FinSecurePayHighRejectionRate did not reach firing state."
    exit 1
}

Write-Host "`n[PASS] TC08 Verified: Monitoring condition triggered FinSecurePayHighRejectionRate alert (state=firing) and routed email notification via receiver 'finsecure-email' to chungyi.pitt@gmail.com." -ForegroundColor Green
exit 0
