#!/usr/bin/env bash
# Installs EFK logging: Elasticsearch + Kibana (manifests) and Fluent Bit (Helm DaemonSet)
set -euo pipefail
cd "$(dirname "$0")"

kubectl apply -f elasticsearch-kibana.yaml
kubectl -n logging rollout status statefulset/elasticsearch --timeout=5m

helm repo add fluent https://fluent.github.io/helm-charts
helm repo update
helm upgrade --install fluent-bit fluent/fluent-bit -n logging -f fluent-bit-values.yaml --wait

kubectl -n logging rollout status deployment/kibana --timeout=5m
echo
echo "Kibana:  kubectl -n logging port-forward svc/kibana 5601:5601   ->  http://localhost:5601"
echo "Create data view 'k8s-logs-*' (timestamp field @timestamp), then filter:"
echo "   kubernetes.namespace_name : \"finsecure\"  and  app.log_level : \"WARN\""
