# FinSecure Pay – Transaction Validation API

Cloud-native DevOps capstone: a Spring Boot transaction validation API delivered via **Jenkins → SonarCloud / OWASP / Trivy → Docker Hub → AWS EKS**, observed with **Prometheus, Grafana, Alertmanager and EFK**.

| Doc | Purpose |
|---|---|
| [docs/DESIGN.md](docs/DESIGN.md) | Design document (architecture, decisions, security, recovery, AI use case, lessons) |
| [docs/RUNBOOK.md](docs/RUNBOOK.md) | Step-by-step guide to run every task and capture evidence |
| [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) | 10–15 minute demonstration script |
| [docs/EVIDENCE_CHECKLIST.md](docs/EVIDENCE_CHECKLIST.md) | Evidence checklist mapped to each task |

## API

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Service status, **running version** and environment |
| POST | `/validate` | Validates a transaction → `200 APPROVED` / `422 REJECTED` (+ violations) / `400` malformed / `401` bad API key |
| GET | `/actuator/health/liveness`, `/readiness` | Kubernetes probes |
| GET | `/actuator/prometheus` | Prometheus metrics |

```bash
curl -s -X POST http://localhost:8080/validate -H "Content-Type: application/json" -H "X-API-Key: $KEY" \
  -d '{"transactionId":"TXN-20261031-0001","sourceAccount":"1234567890","destinationAccount":"9876543210","amount":250.00,"currency":"SGD"}'
```

### Validation rules
| Code | Rule |
|---|---|
| `TRANSACTION_ID_REQUIRED` / `_INVALID` | Must match `TXN-[A-Za-z0-9-]{4,36}` |
| `SOURCE/DESTINATION_ACCOUNT_REQUIRED` / `_INVALID` | 10–12 digits |
| `SAME_ACCOUNT` | Source ≠ destination |
| `SOURCE/DESTINATION_ACCOUNT_BLOCKED` | Not on the compliance block list (`BLOCKED_ACCOUNTS`) |
| `AMOUNT_REQUIRED` / `_NOT_POSITIVE` / `_INVALID_PRECISION` | > 0, max 2 decimals |
| `AMOUNT_BELOW_MINIMUM` / `AMOUNT_EXCEEDS_LIMIT` | Within `MIN_TRANSACTION_AMOUNT` … `MAX_TRANSACTION_AMOUNT` |
| `CURRENCY_REQUIRED` / `_UNSUPPORTED` | In `SUPPORTED_CURRENCIES` |
| `TIMESTAMP_IN_FUTURE` | Not more than `MAX_FUTURE_SKEW_SECONDS` ahead |

## Quick start (local)

```powershell
.\mvnw.cmd clean verify                 # build + 49 JUnit 5 tests + JaCoCo
docker build -t finsecure-pay:1.0.0 .
docker run -p 8080:8080 finsecure-pay:1.0.0
curl http://localhost:8080/health
```

## Repository layout

```
src/                     Spring Boot app + JUnit 5 tests
Dockerfile               Multi-stage, non-root, layered image
Jenkinsfile              CI/CD pipeline (deploy + rollback modes)
k8s/                     Namespace, ConfigMap, Secret template, Deployment, Service+PDB, ServiceMonitor+alerts
infra/eks-cluster.yaml   eksctl cluster definition
jenkins/                 Jenkins image (Docker CLI, kubectl, aws, trivy, helm), JCasC, compose
monitoring/              kube-prometheus-stack values, Grafana dashboard, Alertmanager email template
logging/                 Elasticsearch + Kibana + Fluent Bit
security/                Dependency-Check suppression policy
scripts/                 Load generator (alert trigger), pod-recovery demo
docs/                    Design doc, runbook, demo script, evidence checklist
```
