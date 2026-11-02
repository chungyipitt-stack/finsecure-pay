# Final Capstone Submission Package (`presentation_project_report/`)

This directory contains the final submission deliverables for **FinSecure Pay: Automating a Cloud-Native DevOps & DevSecOps Pipeline**, structured according to [`presentation_project_report_outline.jpg`](file:///c:/Users/chung/AIA_Project_CLI/Capstone_FinSecurePayAuto_Cloud_Native_DevOps/presentation_project_report/presentation_project_report_outline.jpg).

---

## Primary Submission Files

| Deliverable | File Path | Description |
| :--- | :--- | :--- |
| **PowerPoint Presentation (`.pptx`)** | [`FinSecure_Pay_Capstone_Presentation.pptx`](file:///c:/Users/chung/AIA_Project_CLI/Capstone_FinSecurePayAuto_Cloud_Native_DevOps/presentation_project_report/FinSecure_Pay_Capstone_Presentation.pptx) | 10-slide widescreen (`16:9`) executive presentation following the exact slide-by-slide outline in `presentation_project_report_outline.jpg`, complete with embedded architecture & evidence figures, evaluation scorecard table, and presenter notes. |
| **Detailed Summary Report (`.docx`)** | [`FinSecure_Pay_Capstone_Summary_Report.docx`](file:///c:/Users/chung/AIA_Project_CLI/Capstone_FinSecurePayAuto_Cloud_Native_DevOps/presentation_project_report/FinSecure_Pay_Capstone_Summary_Report.docx) | Comprehensive Microsoft Word report covering all 7 Capstone Tasks (`Task 1`–`Task 7`), all 8 Core Evaluation Test Cases (`TC01`–`TC08`), embedded architecture & DevSecOps figures, sanitized live console/API logs, AI use case analysis, and lessons learned. |
| **Visual Diagrams & Figures (`figures/`)** | [`figures/fig1_architecture_diagram.png`](file:///c:/Users/chung/AIA_Project_CLI/Capstone_FinSecurePayAuto_Cloud_Native_DevOps/presentation_project_report/figures/fig1_architecture_diagram.png)<br/>[`figures/fig2_jenkins_pipeline_matrix.png`](file:///c:/Users/chung/AIA_Project_CLI/Capstone_FinSecurePayAuto_Cloud_Native_DevOps/presentation_project_report/figures/fig2_jenkins_pipeline_matrix.png)<br/>[`figures/fig3_devsecops_remediation.png`](file:///c:/Users/chung/AIA_Project_CLI/Capstone_FinSecurePayAuto_Cloud_Native_DevOps/presentation_project_report/figures/fig3_devsecops_remediation.png)<br/>[`figures/fig4_observability_alert_dashboard.png`](file:///c:/Users/chung/AIA_Project_CLI/Capstone_FinSecurePayAuto_Cloud_Native_DevOps/presentation_project_report/figures/fig4_observability_alert_dashboard.png)<br/>[`figures/fig5_ai_triage_architecture.png`](file:///c:/Users/chung/AIA_Project_CLI/Capstone_FinSecurePayAuto_Cloud_Native_DevOps/presentation_project_report/figures/fig5_ai_triage_architecture.png) | High-resolution (`220 DPI`) visual diagrams embedded in the PowerPoint deck and Word report. |
| **Generator Script** | [`generate_submission_docs.py`](file:///c:/Users/chung/AIA_Project_CLI/Capstone_FinSecurePayAuto_Cloud_Native_DevOps/presentation_project_report/generate_submission_docs.py) | Reproducible Python script that generates the figures, `.pptx` presentation, and `.docx` Word report. |

---

## Slide-by-Slide Mapping (`presentation_project_report_outline.jpg`)

| Slide | Outline Topic | Key Content Included |
| :---: | :--- | :--- |
| **1** | **Project overview and business problem** | Business context, fintech validation API problem statement, end-to-end solution summary across Tasks 1–7, and high-level architecture diagram (`fig1_architecture_diagram.png`). |
| **2** | **Application and Git implementation** | Spring Boot 3.5.16 (`/health`, `/validate`, `/actuator/prometheus`), 8 configurable validation rules, 50 JUnit 5 tests (`96.2%` line coverage), and Git repository layout. |
| **3** | **Docker and Kubernetes/cloud deployment** | Multi-stage non-root Alpine JRE 21 `Dockerfile`, Docker Hub tags (`1.0.0`, `1.1.0-4-9ea7e21`), AWS EKS cluster (`finsecure-eks` in `ap-southeast-1`), `2/2` replicas, NLB, probes, and self-healing pod recovery. |
| **4** | **CI/CD pipeline** | 11-stage declarative `Jenkinsfile`, JCasC automation, `pollSCM` trigger, stage matrix (`fig2_jenkins_pipeline_matrix.png`) across Builds #2–#5 (failed test block, rollout, and rollback). |
| **5** | **DevSecOps and security implementation** | SonarCloud Quality Gate (`Grade A`), OWASP Dependency-Check (`CVSS >= 7.0` gate), Trivy image scan (`HIGH/CRITICAL` gate), CVE remediation (`fig3_devsecops_remediation.png`), and masked secret management. |
| **6** | **Monitoring, alerting, and logging** | Prometheus `ServiceMonitor`, 6-panel Grafana dashboard, `FinSecurePayHighRejectionRate` firing timeline (`fig4_observability_alert_dashboard.png`), Alertmanager + Jenkins email alerts, and EFK ECS JSON logging. |
| **7** | **AI application and architecture** | AI-Assisted Incident Triage & Root-Cause Analysis (`fig5_ai_triage_architecture.png`): problem, data inputs, MTTR benefits, hallucination/privacy governance, and Alertmanager-to-Bedrock-to-Jenkins integration. |
| **8** | **Test results, recovery/rollback, and key findings** | Full 8/8 Core Evaluation Test Cases scorecard (`TC01`–`TC08`), self-healing recovery (`0` dropped requests), and 59-second automated rollback verification. |
| **9** | **Additional evidence — Live Verification Artifacts** | Complete index of repository evidence files (`evidence/task1/` through `evidence/task6/` and `testcases/results/`). |
| **10** | **Lessons learned, future roadmap & accessible links** | Key engineering lessons learned, future production roadmap (Argo CD, Cosign, IRSA, ESO), public project URLs, and secret-exclusion attestation. |
