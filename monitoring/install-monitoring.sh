#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# Installs Prometheus + Grafana + Alertmanager (kube-prometheus-stack) on EKS
# and wires Alertmanager email notifications.
#
# Required environment variables (export them in your shell - do NOT commit):
#   SMTP_USER        e.g. yourname@gmail.com
#   SMTP_PASSWORD    Gmail App Password (16 chars)
#   ALERT_EMAIL_TO   recipient address
#   GRAFANA_PASSWORD Grafana admin password
# -----------------------------------------------------------------------------
set -euo pipefail
cd "$(dirname "$0")"

: "${SMTP_USER:?set SMTP_USER}"; : "${SMTP_PASSWORD:?set SMTP_PASSWORD}"
: "${ALERT_EMAIL_TO:?set ALERT_EMAIL_TO}"; : "${GRAFANA_PASSWORD:?set GRAFANA_PASSWORD}"

kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

# Grafana admin credentials -> Secret
kubectl -n monitoring create secret generic grafana-admin \
  --from-literal=admin-user=admin --from-literal=admin-password="${GRAFANA_PASSWORD}" \
  --dry-run=client -o yaml | kubectl apply -f -

# Alertmanager config (contains SMTP password) -> Secret, rendered in-memory only
export SMTP_USER SMTP_PASSWORD ALERT_EMAIL_TO
envsubst < alertmanager-config.tmpl.yaml | \
  kubectl -n monitoring create secret generic alertmanager-finsecure-config \
    --from-file=alertmanager.yaml=/dev/stdin --dry-run=client -o yaml | kubectl apply -f -

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring -f kube-prometheus-stack-values.yaml --wait --timeout 10m

kubectl apply -f grafana-dashboard-configmap.yaml
kubectl apply -f ../k8s/00-namespace.yaml
kubectl apply -f ../k8s/40-monitoring.yaml

echo "Grafana URL: http://$(kubectl -n monitoring get svc monitoring-grafana -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')"
echo "Prometheus:  kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-prometheus 9090"
echo "Alertmanager: kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-alertmanager 9093"
