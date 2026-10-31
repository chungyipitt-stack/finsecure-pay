# FinSecure Pay ??10??5 Minute Demonstration Script

> **Before recording:** cluster up, app deployed (v1), monitoring + logging installed, Jenkins running with ?? green build cached (NVD DB downloaded), browser tabs open: GitHub, Jenkins, Docker Hub, SonarCloud, Grafana, Prometheus Alerts, Kibana, Gmail. Two PowerShell windows: (A) commands, (B) `while ($true) { curl.exe -s http://$LB/health; ""; sleep 2 }`.

| Time | Segment | What to show / say |
|---|---|---|
| 0:00??:00 | **Intro & architecture** | Business problem, show the architecture diagram (DESIGN.md 禮2) and walk through the flow from git push to EKS to monitoring. |
| 1:00??:30 | **Task 1 ??Code & tests** | GitHub repo; `TransactionValidationService` rules; run `.\mvnw.cmd test` (49 tests green); JaCoCo report. |
| 2:30??:30 | **Task 2 ??Container** | Dockerfile (multi-stage, non-root, layered); `docker images`; Docker Hub tags `1.0.0-<build>-<sha>`. |
| 3:30??:00 | **Task 3 ??Kubernetes on EKS** | `kubectl get nodes,pods,svc -n finsecure -o wide`; show probes/ConfigMap in YAML; `curl` the ELB: `/health` + approved and rejected `/validate`. Run `scripts\demo-pod-recovery.ps1` (pod deleted, new pod Ready, window B shows no outage). |
| 5:00??:00 | **Task 4 ??CI/CD** | Jenkinsfile stages. **Live:** change the version or a message, `git push`, and the pipeline auto-starts (pollSCM). While it runs, show a *previous* **failed-test build** (red Unit Test, later stages skipped, failure email). When the build is green, window B shows the version change (zero downtime). Then **rollback**: *Build with Parameters ??MODE=rollback*, and window B returns to the old version; show `rollout history`. |
| 8:00??0:00 | **Task 5 ??DevSecOps** | SonarCloud quality gate; the **blocked build** with commons-text 1.9 (Dependency-Check CVSS 9.8, report); the remediation commit giving a green build; Trivy report; Jenkins credentials (masked) and the K8s Secret, with nothing in Git. |
| 10:00??2:30 | **Task 6 ??Observability** | Grafana dashboard live (traffic from `load-test.ps1`); start load with `-RejectRatio 0.8`; Prometheus alert Pending, then Firing; **alert email** in Gmail (pre-recorded if waiting is too long); Jenkins emails; Kibana query `kubernetes.namespace_name:"finsecure" and app.log.level:"WARN"`; `kubectl logs`. |
| 12:30??4:00 | **Task 7 ??AI use case** | AI incident triage: problem, inputs, benefits, risks, integration diagram (DESIGN.md 禮7). |
| 14:00??5:00 | **Wrap-up** | Lessons learned and future improvements (GitOps, canary, IRSA, signing). |

**Tips:** pre-run the slow parts (first NVD download, cluster creation, waiting for the alert) and show their results; do the git push ??deploy and the rollback live.
