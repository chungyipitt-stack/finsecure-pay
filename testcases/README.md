# Core Test Cases for Evaluation (`testcase_expected_result.jpg`)

This folder contains the executable test scripts, evaluation harness, and captured live verification outputs for all **8 Core Test Cases** specified in [`testcase_expected_result.jpg`](file:///c:/Users/chung/AIA_Project_CLI/Capstone_FinSecurePayAuto_Cloud_Native_DevOps/testcases/testcase_expected_result.jpg).

---

## Summary Table — Expected vs. Verified Results

| ID | Test Case (`testcase_expected_result.jpg`) | Expected Result | Implementation Script | Captured Result Log | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TC01** | **Run unit tests** | Required unit tests pass. | [`TC01-run-unit-tests.ps1`](file:///c:/Users/chung/AIA_Project_CLI/Capstone_FinSecurePayAuto_Cloud_Native_DevOps/testcases/TC01-run-unit-tests.ps1) | [`results/TC01-unit-tests.txt`](file:///c:/Users/chung/AIA_Project_CLI/Capstone_FinSecurePayAuto_Cloud_Native_DevOps/testcases/results/TC01-unit-tests.txt) | **PASS** (`50/50` JUnit 5 tests pass, `0` failures) |
| **TC02** | **Introduce a controlled failing test** | Jenkins pipeline fails, and deployment does not proceed. | [`TC02-controlled-failing-test.ps1`](file:///c:/Users/chung/AIA_Project_CLI/Capstone_FinSecurePayAuto_Cloud_Native_DevOps/testcases/TC02-controlled-failing-test.ps1) & [`ControlledEvaluationTest.java`](file:///c:/Users/chung/AIA_Project_CLI/Capstone_FinSecurePayAuto_Cloud_Native_DevOps/src/test/java/com/finsecure/pay/ControlledEvaluationTest.java) | [`results/TC02-controlled-failing-test.txt`](file:///c:/Users/chung/AIA_Project_CLI/Capstone_FinSecurePayAuto_Cloud_Native_DevOps/testcases/results/TC02-controlled-failing-test.txt) | **PASS** (`Unit Test` fails; `Package`, `Push`, `Deploy - EKS` skipped) |
| **TC03** | **Run the container and access `/health`** | Application returns a healthy response. | [`TC03-container-health.ps1`](file:///c:/Users/chung/AIA_Project_CLI/Capstone_FinSecurePayAuto_Cloud_Native_DevOps/testcases/TC03-container-health.ps1) | [`results/TC03-container-health.txt`](file:///c:/Users/chung/AIA_Project_CLI/Capstone_FinSecurePayAuto_Cloud_Native_DevOps/testcases/results/TC03-container-health.txt) | **PASS** (`HTTP 200 OK`, `{"status":"UP","service":"finsecure-pay",...}`) |
| **TC04** | **Inspect the Kubernetes deployment** | At least two application pods are running and Ready. | [`TC04-inspect-k8s-deployment.ps1`](file:///c:/Users/chung/AIA_Project_CLI/Capstone_FinSecurePayAuto_Cloud_Native_DevOps/testcases/TC04-inspect-k8s-deployment.ps1) | [`results/TC04-inspect-k8s-deployment.txt`](file:///c:/Users/chung/AIA_Project_CLI/Capstone_FinSecurePayAuto_Cloud_Native_DevOps/testcases/results/TC04-inspect-k8s-deployment.txt) | **PASS** (`2/2` replicas `Running` and `1/1 Ready` across 2 EKS nodes) |
| **TC05** | **Deploy a new image/version** | Kubernetes rollout completes successfully. | [`TC05-deploy-new-version.ps1`](file:///c:/Users/chung/AIA_Project_CLI/Capstone_FinSecurePayAuto_Cloud_Native_DevOps/testcases/TC05-deploy-new-version.ps1) | [`results/TC05-deploy-new-version.txt`](file:///c:/Users/chung/AIA_Project_CLI/Capstone_FinSecurePayAuto_Cloud_Native_DevOps/testcases/results/TC05-deploy-new-version.txt) | **PASS** (`deployment "finsecure-pay" successfully rolled out` to `1.1.0-4-9ea7e21`) |
| **TC06** | **Delete or restart one pod** | Kubernetes automatically recreates the pod. | [`TC06-delete-pod-self-healing.ps1`](file:///c:/Users/chung/AIA_Project_CLI/Capstone_FinSecurePayAuto_Cloud_Native_DevOps/testcases/TC06-delete-pod-self-healing.ps1) | [`results/TC06-delete-pod-self-healing.txt`](file:///c:/Users/chung/AIA_Project_CLI/Capstone_FinSecurePayAuto_Cloud_Native_DevOps/testcases/results/TC06-delete-pod-self-healing.txt) | **PASS** (ReplicaSet immediately spawns replacement pod to `1/1 Ready`) |
| **TC07** | **Introduce a controlled critical/high security finding** | The security gate blocks the release. | [`TC07-controlled-security-finding.ps1`](file:///c:/Users/chung/AIA_Project_CLI/Capstone_FinSecurePayAuto_Cloud_Native_DevOps/testcases/TC07-controlled-security-finding.ps1) & [`pom.xml`](file:///c:/Users/chung/AIA_Project_CLI/Capstone_FinSecurePayAuto_Cloud_Native_DevOps/pom.xml) (`simulate-security-finding`) | [`results/TC07-controlled-security-gate.txt`](file:///c:/Users/chung/AIA_Project_CLI/Capstone_FinSecurePayAuto_Cloud_Native_DevOps/testcases/results/TC07-controlled-security-gate.txt) | **PASS** (OWASP Dependency-Check `CVSS >= 7.0` & Trivy gates halt build & skip deploy) |
| **TC08** | **Trigger a monitoring condition** | Alert fires and a notification is received. | [`TC08-trigger-monitoring-alert.ps1`](file:///c:/Users/chung/AIA_Project_CLI/Capstone_FinSecurePayAuto_Cloud_Native_DevOps/testcases/TC08-trigger-monitoring-alert.ps1) | [`results/TC08-trigger-monitoring-alert.txt`](file:///c:/Users/chung/AIA_Project_CLI/Capstone_FinSecurePayAuto_Cloud_Native_DevOps/testcases/results/TC08-trigger-monitoring-alert.txt) | **PASS** (`FinSecurePayHighRejectionRate` transitions to `firing`, email routed to `chungyi.pitt@gmail.com`) |

---

## How to Run the Evaluation Suite

### Run All 8 Core Test Cases Automatically
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\testcases\run-all-testcases.ps1
```

### Run Individual Test Cases

1. **TC01 — Run unit tests**:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\testcases\TC01-run-unit-tests.ps1
   ```
2. **TC02 — Introduce a controlled failing test**:
   ```powershell
   # Verify local controlled failing test + Jenkins pipeline stage block:
   powershell -NoProfile -ExecutionPolicy Bypass -File .\testcases\TC02-controlled-failing-test.ps1

   # Or trigger a new live Jenkins build with SIMULATE_TEST_FAILURE=true:
   powershell -NoProfile -ExecutionPolicy Bypass -File .\testcases\TC02-controlled-failing-test.ps1 -TriggerLiveJenkinsBuild
   ```
3. **TC03 — Run the container and access `/health`**:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\testcases\TC03-container-health.ps1
   ```
4. **TC04 — Inspect the Kubernetes deployment**:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\testcases\TC04-inspect-k8s-deployment.ps1
   ```
5. **TC05 — Deploy a new image/version**:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\testcases\TC05-deploy-new-version.ps1
   ```
6. **TC06 — Delete or restart one pod**:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\testcases\TC06-delete-pod-self-healing.ps1
   ```
7. **TC07 — Introduce a controlled critical/high security finding**:
   ```powershell
   # Verify security gate block on CVSS >= 7.0 HIGH/CRITICAL finding:
   powershell -NoProfile -ExecutionPolicy Bypass -File .\testcases\TC07-controlled-security-finding.ps1

   # Or trigger a new live Jenkins build with SIMULATE_SECURITY_FINDING=true (injects CVE-2022-42889 CVSS 9.8 CRITICAL):
   powershell -NoProfile -ExecutionPolicy Bypass -File .\testcases\TC07-controlled-security-finding.ps1 -TriggerLiveJenkinsBuild
   ```
8. **TC08 — Trigger a monitoring condition**:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\testcases\TC08-trigger-monitoring-alert.ps1
   ```
