<#
.SYNOPSIS
  Installs Prometheus + Grafana + Alertmanager (kube-prometheus-stack) on EKS and wires
  Alertmanager e-mail. Secrets are read from the git-ignored jenkins/.env file and only
  ever stored as Kubernetes Secrets. Safe to re-run (e.g. after adding SMTP_PASSWORD).

.EXAMPLE
  .\monitoring\install-monitoring.ps1
#>
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$envFile = Join-Path $root "jenkins/.env"

# --- read KEY=VALUE pairs from jenkins/.env (never printed) ---
$cfg = @{}
Get-Content $envFile | Where-Object { $_ -match '^\s*([A-Z0-9_]+)=(.*)$' } | ForEach-Object {
    $cfg[$Matches[1]] = $Matches[2].Trim()
}
$smtpUser = $cfg["SMTP_USER"]; $smtpPass = $cfg["SMTP_PASSWORD"]
$alertTo = if ($cfg["ALERT_EMAIL_TO"]) { $cfg["ALERT_EMAIL_TO"] } else { $smtpUser }
$grafanaPass = if ($cfg["GRAFANA_PASSWORD"]) { $cfg["GRAFANA_PASSWORD"] } `
               else { (Get-Content "$env:USERPROFILE\.finsecure-grafana-password" -Raw).Trim() }
if (-not $smtpPass) { Write-Warning "SMTP_PASSWORD is empty in jenkins/.env - alerts will fire but e-mail delivery will fail until you add it and re-run this script." }

kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

# Grafana admin credentials -> Secret
kubectl -n monitoring create secret generic grafana-admin `
  --from-literal=admin-user=admin --from-literal=admin-password="$grafanaPass" `
  --dry-run=client -o yaml | kubectl apply -f -

# Alertmanager config rendered in memory only -> Secret
$amConfig = (Get-Content (Join-Path $PSScriptRoot "alertmanager-config.tmpl.yaml") -Raw) `
    -replace '\$\{SMTP_USER\}', $smtpUser -replace '\$\{SMTP_PASSWORD\}', $smtpPass -replace '\$\{ALERT_EMAIL_TO\}', $alertTo
kubectl -n monitoring create secret generic alertmanager-finsecure-config `
  --from-literal=alertmanager.yaml="$amConfig" --dry-run=client -o yaml | kubectl apply -f -

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts --force-update | Out-Null
helm repo update prometheus-community | Out-Null
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack `
  --namespace monitoring -f (Join-Path $PSScriptRoot "kube-prometheus-stack-values.yaml") --wait --timeout 15m
if ($LASTEXITCODE -ne 0) { throw "helm install failed" }

kubectl apply -f (Join-Path $PSScriptRoot "grafana-dashboard-configmap.yaml")
kubectl apply -f (Join-Path $root "k8s/00-namespace.yaml")
kubectl apply -f (Join-Path $root "k8s/40-monitoring.yaml")

$g = kubectl -n monitoring get svc monitoring-grafana -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
Write-Host "`nGrafana:      http://$g   (user: admin, password in jenkins/.env GRAFANA_PASSWORD or ~/.finsecure-grafana-password)"
Write-Host "Prometheus:   kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-prometheus 9090"
Write-Host "Alertmanager: kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-alertmanager 9093"
