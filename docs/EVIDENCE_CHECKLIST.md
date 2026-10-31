# Evidence Checklist

Save screenshots or logs under `evidence/taskN/`. Tick each item when captured.

## Task 1 – Application & version control
- [ ] `t1-github-repo.png` – GitHub repository page (link: `https://github.com/<you>/finsecure-pay`)
- [ ] `t1-source-tree.png` – source structure (`src/main/java/...`)
- [ ] `t1-mvn-verify.png` – `mvnw clean verify`: *Tests run: 49, Failures: 0* + BUILD SUCCESS
- [ ] `t1-surefire-report` – `target/surefire-reports/*.txt` and the JaCoCo coverage page

## Task 2 – Containerisation
- [ ] `Dockerfile` (in repo)
- [ ] `t2-docker-images.png` – `docker images` showing the version tag
- [ ] `t2-docker-run-health.png` – `docker ps` (healthy) + `curl /health`
- [ ] `t2-dockerhub-tags.png` – Docker Hub repository → Tags

## Task 3 – Kubernetes & cloud
- [ ] `k8s/20-deployment.yaml`, `k8s/30-service.yaml`, `k8s/10-configmap.yaml` (in repo)
- [ ] `t3-describe-deploy.png` – `kubectl describe deploy` (replicas 2, liveness/readiness/startup probes)
- [ ] `t3-pods-running.png` – `kubectl get nodes,pods,svc -o wide` on EKS
- [ ] `t3-external-access.png` – browser/curl to the ELB hostname `/health` + `/validate`
- [ ] `t3-self-healing.png` – `demo-pod-recovery.ps1` output (old pod Terminating, new pod Running)
- [ ] `t3-eks-console.png` – AWS console EKS cluster + node group

## Task 4 – CI/CD
- [ ] `Jenkinsfile` (in repo)
- [ ] `t4-pipeline-success.png` – stage view, all green
- [ ] `t4-scm-trigger.png` – "Started by an SCM change"
- [ ] `t4-failed-test.png` – red Unit Test stage, later stages skipped + JUnit failure detail
- [ ] `t4-rollout.png` – `rollout status` + `/health` showing the new version
- [ ] `t4-rollback.png` – rollback build + `rollout history` + `/health` showing the old version

## Task 5 – DevSecOps
- [ ] `t5-sonarcloud.png` – quality gate passed
- [ ] `t5-dependency-check-report.png` – OWASP HTML report
- [ ] `t5-trivy-report.txt` – Trivy artifact
- [ ] `t5-blocked-pipeline.png` – Dependency-Check stage failed (CVE-2022-42889, CVSS 9.8)
- [ ] `t5-remediation.png` – commit removing or upgrading the dependency + green build
- [ ] `t5-credentials.png` – Jenkins credentials list (masked) + console `****`
- [ ] `t5-k8s-secret.png` – `kubectl get secret finsecure-pay-secrets -o yaml` + `.gitignore`

## Task 6 – Monitoring, alerting, logging
- [ ] `t6-grafana-dashboard.png` – dashboard with live data
- [ ] `t6-prometheus-targets.png` – Status → Targets (finsecure-pay UP)
- [ ] `t6-alert-rules.png` – Alerts page / `k8s/40-monitoring.yaml`
- [ ] `t6-alert-firing.png` – FinSecurePayHighRejectionRate *Firing*
- [ ] `t6-alert-email.png` – Alertmanager email (FIRING + RESOLVED)
- [ ] `t6-jenkins-email.png` – Jenkins success and failure emails
- [ ] `t6-kibana-logs.png` – Kibana Discover with finsecure logs
- [ ] `t6-kubectl-logs.png` – `kubectl logs -l ... --prefix`

## Task 7 – Documentation & demo
- [ ] `docs/DESIGN.md` exported to PDF (3–5 pages)
- [ ] Architecture diagram (DESIGN.md §2)
- [ ] AI use-case section (DESIGN.md §7)
- [ ] Demo video (10–15 minutes) – link
- [ ] Lessons learned & future improvements (DESIGN.md §8)
