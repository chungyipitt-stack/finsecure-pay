<#
.SYNOPSIS
  Installs EFK logging: Elasticsearch + Kibana (manifests) and Fluent Bit (Helm DaemonSet).
#>
$ErrorActionPreference = "Stop"
kubectl apply -f (Join-Path $PSScriptRoot "elasticsearch-kibana.yaml")
kubectl -n logging rollout status statefulset/elasticsearch --timeout=6m

helm repo add fluent https://fluent.github.io/helm-charts --force-update | Out-Null
helm repo update fluent | Out-Null
helm upgrade --install fluent-bit fluent/fluent-bit -n logging -f (Join-Path $PSScriptRoot "fluent-bit-values.yaml") --wait --timeout 10m
if ($LASTEXITCODE -ne 0) { throw "fluent-bit install failed" }

kubectl -n logging rollout status deployment/kibana --timeout=6m
Write-Host "`nKibana: kubectl -n logging port-forward svc/kibana 5601:5601  ->  http://localhost:5601"
Write-Host "Data view 'k8s-logs-*' (@timestamp); query: kubernetes.namespace_name : `"finsecure`" and app.log.level : `"WARN`""
