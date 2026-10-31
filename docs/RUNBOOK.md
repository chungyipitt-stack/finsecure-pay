# FinSecure Pay ??Runbook (execute tasks & capture evidence)

> Shell notes: PowerShell commands are marked `ps>`; Bash commands (`.sh` scripts) run in **Git Bash**.
> Save screenshots into `evidence/taskN/` using the names in [EVIDENCE_CHECKLIST.md](EVIDENCE_CHECKLIST.md).

## 0. Prerequisites (one-off)

| Item | How |
|---|---|
| JDK 21, Maven | `winget install Microsoft.OpenJDK.21` (Maven Wrapper `mvnw` is in the repo) |
| Docker Desktop | running |
| AWS CLI v2, kubectl | installed |
| eksctl, Helm | `winget install eksctl.eksctl Helm.Helm` |
| Accounts | GitHub, Docker Hub (create **access token**), SonarCloud (login with GitHub, import repo, create token), NVD API key (https://nvd.nist.gov/developers/request-an-api-key), Gmail **App Password** (needs 2FA), AWS IAM user with EKS admin rights |

---

## Task 1 ??Application & version control
```powershell
ps> .\mvnw.cmd clean verify                   # 49 tests, BUILD SUCCESS
ps> start target\site\jacoco\index.html        # coverage report
ps> git init -b main; git add .; git commit -m "feat: FinSecure Pay transaction validation API"
ps> git remote add origin https://github.com/chungyipitt-stack/finsecure-pay.git; git push -u origin main
```
Evidence: test summary in console, `target/surefire-reports`, JaCoCo page, GitHub repo page.

## Task 2 ??Containerisation
```powershell
ps> docker build --build-arg APP_VERSION=1.0.0 -t chungyi1979/finsecure-pay:1.0.0 .
ps> docker images chungyi1979/finsecure-pay
ps> docker run -d --name fsp -p 18080:8080 chungyi1979/finsecure-pay:1.0.0
ps> curl.exe http://localhost:18080/health
ps> docker login; docker push chungyi1979/finsecure-pay:1.0.0
```
Evidence: `docker images`, `docker ps`, `/health` response, Docker Hub tags page.

## Task 3 ??EKS deployment
```powershell
ps> eksctl create cluster -f infra/eks-cluster.yaml          # ~15-20 min
ps> kubectl get nodes -o wide
ps> kubectl apply -f k8s/00-namespace.yaml -f k8s/10-configmap.yaml
ps> kubectl -n finsecure create secret generic finsecure-pay-secrets --from-literal=FINSECURE_API_KEY=<key>
ps> (Get-Content k8s/20-deployment.yaml) -replace 'IMAGE_PLACEHOLDER','chungyi1979/finsecure-pay:1.0.0' -replace 'CHANGE_CAUSE_PLACEHOLDER','manual 1.0.0' | kubectl apply -f -
ps> kubectl apply -f k8s/30-service.yaml
ps> kubectl -n finsecure get deploy,rs,pods,svc -o wide
ps> $LB = kubectl -n finsecure get svc finsecure-pay -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
ps> curl.exe http://$LB/health                                # may take 2-3 min for DNS
ps> .\scripts\demo-pod-recovery.ps1                           # self-healing evidence
```
Evidence: `kubectl describe deploy finsecure-pay` (probes, replicas), ConfigMap YAML, pods Running, browser/curl on the ELB hostname, pod deletion + recreation output.

## Task 4 ??Jenkins CI/CD
1. Edit the `environment {}` block in `Jenkinsfile` (`DOCKERHUB_USER`, `SONAR_ORG`, `SONAR_PROJECT`, `NOTIFY_EMAIL`), commit and push.
2. Start Jenkins:
   ```powershell
   ps> Copy-Item jenkins/.env.example jenkins/.env   # fill in all values (never commit)
   ps> docker compose -f jenkins/docker-compose.yml up -d --build
   ```
   Open http://localhost:8088 and log in as `admin`. The job `finsecure-pay` and all credentials are already created by JCasC.
3. Configure email: **Manage Jenkins ??System ??Extended E-mail Notification**: SMTP `smtp.gmail.com`, port `587`, *Use TLS*, credentials `smtp-creds`. Also set **E-mail Notification** (same values) and send a test email.
4. Click **Build with Parameters** once (MODE=deploy). The first run downloads the NVD database (~10-20 min, then it is cached).
5. **Automatic trigger:** change something small (e.g. a log message), `git push`. `pollSCM` starts a build within 2 minutes (look for "Started by an SCM change").
6. **Failed test blocks deploy:** on a branch or commit, break a rule, e.g. change `MAX_TRANSACTION_AMOUNT` default logic or set `maxAmount` comparison `>=`, then push. *Unit Test* fails (red), the later stages are skipped, and you receive a failure email. Revert the change and push again.
7. **Rollout of a new version:** bump `<version>` in `pom.xml` to `1.1.0` (or any change), push, and watch `kubectl -n finsecure rollout status deploy/finsecure-pay` while running `curl.exe http://$LB/health` in a loop. The version changes with no failed requests.
8. **Rollback:** *Build with Parameters* ??`MODE=rollback` (empty `ROLLBACK_TAG` = previous revision, or give a known-good tag). Show `kubectl -n finsecure rollout history deploy/finsecure-pay` and `/health` version before and after.

## Task 5 ??DevSecOps
1. Show the SonarCloud dashboard (quality gate passed) and the `OWASP Dependency-Check` HTML report link on the build, plus the Trivy report artifact.
2. **Blocked pipeline:** add a vulnerable dependency to `pom.xml`:
   ```xml
   <dependency>
     <groupId>org.apache.commons</groupId>
     <artifactId>commons-text</artifactId>
     <version>1.9</version>   <!-- CVE-2022-42889 Text4Shell, CVSS 9.8 -->
   </dependency>
   ```
   Push. *Dependency Scan - OWASP* fails with `CVSS score >= 7`. Screenshot the stage view, the console, and the report.
3. **Remediate:** remove the dependency (or upgrade it to `1.15.0`), push, and the build is green again.
4. **Secrets evidence:** Jenkins Credentials page (values masked), console showing `****`, `kubectl -n finsecure get secret finsecure-pay-secrets -o yaml` (base64, not in Git), `git grep -i password` returns nothing sensitive, and `.gitignore`.

## Task 6 ??Monitoring, alerting, logging
```bash
# Git Bash
export SMTP_USER=you@gmail.com SMTP_PASSWORD='app-password' ALERT_EMAIL_TO=you@gmail.com GRAFANA_PASSWORD='StrongPass!'
./monitoring/install-monitoring.sh
./logging/install-logging.sh
```
1. Open the Grafana URL that the script prints, then *Dashboards ??FinSecure Pay - Service Overview*.
2. Generate traffic: `ps> .\scripts\load-test.ps1 -BaseUrl http://$LB -ApiKey <key> -DurationSeconds 600 -RejectRatio 0.1`
3. **Trigger the alert:** `ps> .\scripts\load-test.ps1 -BaseUrl http://$LB -ApiKey <key> -DurationSeconds 300 -RejectRatio 0.8`
   After about 3 minutes `FinSecurePayHighRejectionRate` goes *Pending*, then *Firing* (Prometheus ??Alerts, `kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-prometheus 9090`). An email arrives from Alertmanager, followed by a *RESOLVED* email after the load stops.
   *Alternative (outage alert):* `kubectl -n finsecure scale deploy finsecure-pay --replicas=0` makes `FinSecurePayDown` fire (critical) after about 1?? minutes. Restore with `--replicas=2` and you receive the RESOLVED email.
4. **Jenkins notification:** success and failure emails from Task 4 and 5 builds (screenshot the inbox).
5. **Logs:** see the troubleshooting section below.

### Log access for troubleshooting
| Need | Command |
|---|---|
| Live logs of all replicas | `kubectl -n finsecure logs -l app.kubernetes.io/name=finsecure-pay -f --prefix` |
| Previous crashed container | `kubectl -n finsecure logs <pod> --previous` |
| Why a pod is not starting | `kubectl -n finsecure describe pod <pod>`; `kubectl -n finsecure get events --sort-by=.lastTimestamp` |
| Centralised search | `kubectl -n logging port-forward svc/kibana 5601:5601`, open http://localhost:5601, create data view `k8s-logs-*`, then query `kubernetes.namespace_name:"finsecure" and app.log_level:"WARN"` |
| Find a specific transaction | Kibana: `app.message:"TXN-LOAD-42"` |
| Pipeline logs | Jenkins build ??*Console Output* (and the failure email has the log attached) |

## Teardown (avoid AWS charges!)
```powershell
ps> helm -n monitoring uninstall monitoring; helm -n logging uninstall fluent-bit
ps> kubectl delete ns finsecure logging monitoring       # releases the load balancers
ps> eksctl delete cluster -f infra/eks-cluster.yaml --disable-nodegroup-eviction
ps> docker compose -f jenkins/docker-compose.yml down
```
