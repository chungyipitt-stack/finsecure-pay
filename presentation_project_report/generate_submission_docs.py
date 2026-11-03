# -*- coding: utf-8 -*-
"""
Generates the Final Capstone Submission Package in presentation_project_report/:
  1. High-resolution architecture & evidence figures (presentation_project_report/figures/*.png)
  2. PowerPoint Presentation (presentation_project_report/FinSecure_Pay_Capstone_Presentation.pptx)
     following presentation_project_report_outline.jpg (Slides 1 to 10)
  3. Detailed Word Summary Report (presentation_project_report/FinSecure_Pay_Capstone_Summary_Report.docx)
     covering Tasks 1-7, Core Test Cases TC01-TC08, Architecture, AI Use Case, and Sanitized Evidence.
"""
import os
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

from docx import Document
from docx.shared import Inches as DocInches, Pt as DocPt, RGBColor as DocRGB
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
FIG_DIR = BASE_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# STEP 1: GENERATE HIGH-RESOLUTION VISUAL DIAGRAMS & CHARTS
# =============================================================================
def draw_box(ax, x, y, w, h, title, subtitle="", fc="#1E3A8A", ec="#0F172A", tc="white", fontsize=9):
    patch = mpatches.FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.015,rounding_size=0.02",
        facecolor=fc, edgecolor=ec, linewidth=1.5
    )
    ax.add_patch(patch)
    if subtitle:
        ax.text(x + w / 2, y + h * 0.63, title, ha="center", va="center",
                color=tc, fontsize=fontsize, fontweight="bold", family="sans-serif")
        ax.text(x + w / 2, y + h * 0.30, subtitle, ha="center", va="center",
                color=tc, fontsize=fontsize - 1.5, family="sans-serif")
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center",
                color=tc, fontsize=fontsize, fontweight="bold", family="sans-serif")


def generate_figures():
    # --- Figure 1: End-to-End Architecture Diagram ---
    fig, ax = plt.subplots(figsize=(13, 6.8), dpi=220)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 6.8)
    ax.axis("off")
    fig.patch.set_facecolor("#F8FAFC")

    ax.text(6.5, 6.45, "FinSecure Pay — Cloud-Native DevSecOps & AWS EKS Architecture",
            ha="center", va="center", fontsize=14, fontweight="bold", color="#0F172A")

    # Left: Dev & Source Control
    draw_box(ax, 0.3, 4.9, 1.8, 1.0, "Developer", "Git Commit & Push", fc="#0F172A", fontsize=9.5)
    draw_box(ax, 2.5, 4.9, 2.1, 1.0, "GitHub Repo", "chungyipitt-stack/\nfinsecure-pay (main)", fc="#1E293B", fontsize=9)

    # Middle: Jenkins CI/CD + Security Gates
    ci_group = mpatches.FancyBboxPatch((0.3, 2.3), 6.2, 2.2, boxstyle="round,pad=0.02",
                                       facecolor="#EFF6FF", edgecolor="#2563EB", linewidth=1.5)
    ax.add_patch(ci_group)
    ax.text(3.4, 4.3, "Jenkins CI/CD Pipeline (JCasC, Docker Agent, PollSCM H/2)",
            ha="center", va="center", fontsize=10, fontweight="bold", color="#1E3A8A")

    stages = [
        ("1. Checkout\n& Build", "#1D4ED8"),
        ("2. Unit Tests\n50 JUnit + JaCoCo", "#1D4ED8"),
        ("3. SonarCloud\nQuality Gate (A)", "#7C3AED"),
        ("4. OWASP Scan\nGate: CVSS >= 7", "#DC2626"),
        ("5. Package &\nDocker Build", "#0369A1"),
        ("6. Trivy Scan\nGate: HIGH/CRIT", "#DC2626"),
    ]
    for idx, (lbl, col) in enumerate(stages):
        bx = 0.45 + (idx % 3) * 2.0
        by = 3.35 if idx < 3 else 2.45
        draw_box(ax, bx, by, 1.85, 0.72, lbl, fc=col, fontsize=8)

    # Docker Hub & SonarCloud
    draw_box(ax, 4.9, 4.9, 2.2, 1.0, "Docker Hub Registry", "chungyi1979/finsecure-pay\n<semver>-<build>-<sha>", fc="#0284C7", fontsize=8.5)
    draw_box(ax, 0.3, 0.5, 2.9, 1.3, "SonarCloud & NVD / Trivy DB", "Quality Gate: OK (96.2% cov)\nZero Unremediated Fixable CVEs", fc="#4C1D95", fontsize=8.5)
    draw_box(ax, 3.6, 0.5, 2.9, 1.3, "SMTP Ops Notifications", "Jenkins Email-Ext & Alertmanager\n-> chungyi.pitt@gmail.com", fc="#B45309", fontsize=8.5)

    # Right: AWS EKS Cluster
    eks_group = mpatches.FancyBboxPatch((6.8, 0.5), 5.9, 5.4, boxstyle="round,pad=0.02",
                                        facecolor="#ECFDF5", edgecolor="#059669", linewidth=2.0)
    ax.add_patch(eks_group)
    ax.text(9.75, 5.68, "AWS Cloud (ap-southeast-1) — EKS Cluster: finsecure-eks (2x m7i-flex.large)",
            ha="center", va="center", fontsize=9.8, fontweight="bold", color="#065F46")

    draw_box(ax, 7.1, 4.55, 5.3, 0.85, "AWS Network Load Balancer (External Service)",
             "http://a67e1d0b5b459453d9d9be62e598e148-a0206fab5a570f79.elb.ap-southeast-1.amazonaws.com", fc="#047857", fontsize=8)

    # Namespace: finsecure
    draw_box(ax, 7.1, 3.05, 5.3, 1.25, "Namespace: finsecure (Application Workloads)",
             "Deployment: finsecure-pay (2/2 Ready Replicas, RollingUpdate maxUnavailable=0)\nConfigMap (Validation Rules) + Secret (FINSECURE_API_KEY) + Startup/Readiness/Liveness Probes",
             fc="#065F46", fontsize=8)

    # Namespace: monitoring
    draw_box(ax, 7.1, 1.8, 2.55, 1.05, "Namespace: monitoring",
             "Prometheus + ServiceMonitor\nGrafana + Alertmanager", fc="#0F766E", fontsize=8)

    # Namespace: logging
    draw_box(ax, 9.85, 1.8, 2.55, 1.05, "Namespace: logging",
             "Fluent Bit DaemonSet ->\nElasticsearch -> Kibana (EFK)", fc="#115E59", fontsize=8)

    # CD Stage box inside EKS bottom
    draw_box(ax, 7.1, 0.7, 5.3, 0.9, "7. CD Deploy, Smoke Test & Auto-Rollback Gate",
             "kubectl apply -> rollout status --timeout=180s -> /health Smoke Test (or MODE=rollback)",
             fc="#1E40AF", fontsize=8)

    # Arrows
    arrow_kw = dict(arrowstyle="->", color="#334155", lw=1.8)
    ax.annotate("", xy=(2.5, 5.4), xytext=(2.1, 5.4), arrowprops=arrow_kw)
    ax.annotate("", xy=(3.4, 4.5), xytext=(3.4, 4.9), arrowprops=arrow_kw)
    ax.annotate("", xy=(5.5, 4.9), xytext=(5.5, 4.2), arrowprops=arrow_kw)
    ax.annotate("", xy=(7.1, 4.9), xytext=(6.8, 4.9), arrowprops=arrow_kw)
    ax.annotate("", xy=(7.1, 1.15), xytext=(6.5, 2.6), arrowprops=arrow_kw)
    ax.annotate("", xy=(9.75, 4.3), xytext=(9.75, 4.55), arrowprops=arrow_kw)

    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig1_architecture_diagram.png", dpi=220)
    plt.close(fig)

    # --- Figure 2: Jenkins Pipeline Stage Matrix (Builds #2, #3, #4, #5) ---
    fig, ax = plt.subplots(figsize=(12, 4.6), dpi=220)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.set_title("Jenkins CI/CD Pipeline Execution Matrix (Live Builds #2 – #5)",
                 fontsize=13, fontweight="bold", color="#0F172A", pad=12)

    builds = [
        "Build #2\n(TC02 Failed Test\n97s -> BLOCKED)",
        "Build #3\n(TC07 OWASP Gate\n670s -> BLOCKED)",
        "Build #4\n(Full Release v1.1.0\n422s -> DEPLOYED)",
        "Build #5\n(Rollback to v1.0.0\n59s -> REVERTED)",
    ]
    stage_names = [
        "Checkout", "Build", "Unit Test", "SonarCloud", "OWASP\nScan",
        "Package", "Docker\nBuild", "Trivy\nScan", "Docker\nPush",
        "Deploy\nEKS", "Rollback\nEKS", "Smoke\nTest", "Email\nNotify"
    ]
    matrix = [
        # Build #2: failed at Unit Test
        ["PASS", "PASS", "FAIL", "SKIP", "SKIP", "SKIP", "SKIP", "SKIP", "SKIP", "SKIP", "SKIP", "SKIP", "SENT"],
        # Build #3: failed at OWASP Scan
        ["PASS", "PASS", "PASS", "PASS", "FAIL", "SKIP", "SKIP", "SKIP", "SKIP", "SKIP", "SKIP", "SKIP", "SENT"],
        # Build #4: full deploy success
        ["PASS", "PASS", "PASS", "PASS", "PASS", "PASS", "PASS", "PASS", "PASS", "PASS", "N/A",  "PASS", "SENT"],
        # Build #5: rollback success
        ["PASS", "N/A",  "N/A",  "N/A",  "N/A",  "N/A",  "N/A",  "N/A",  "N/A",  "N/A",  "PASS", "PASS", "SENT"],
    ]
    colors = {
        "PASS": "#16A34A",
        "FAIL": "#DC2626",
        "SKIP": "#94A3B8",
        "N/A":  "#CBD5E1",
        "SENT": "#2563EB",
    }

    ax.set_xlim(0, 15.2)
    ax.set_ylim(0, 5.2)

    for c_idx, s_name in enumerate(stage_names):
        ax.text(2.35 + c_idx * 0.98, 4.65, s_name, ha="center", va="center",
                fontsize=8, fontweight="bold", color="#1E293B")

    for r_idx, b_label in enumerate(builds):
        y = 3.55 - r_idx * 1.0
        ax.text(1.05, y + 0.35, b_label, ha="center", va="center",
                fontsize=8.5, fontweight="bold", color="#0F172A")
        for c_idx, status in enumerate(matrix[r_idx]):
            x = 1.9 + c_idx * 0.98
            col = colors[status]
            tc = "white" if status in ("PASS", "FAIL", "SENT") else "#334155"
            draw_box(ax, x, y, 0.88, 0.7, status, fc=col, ec="white", tc=tc, fontsize=8)

    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig2_jenkins_pipeline_matrix.png", dpi=220)
    plt.close(fig)

    # --- Figure 3: DevSecOps Vulnerability Remediation Chart ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.2), dpi=220)
    fig.patch.set_facecolor("white")

    cats = ["CRITICAL CVEs\n(Tomcat / Jackson)", "HIGH CVEs\n(Tomcat / Jackson)", "MEDIUM CVEs\n(Log4j-API)"]
    before_counts = [6, 5, 3]
    after_counts = [0, 0, 0]
    x = [0, 1, 2]
    w = 0.34
    b1 = ax1.bar([i - w/2 for i in x], before_counts, width=w, label="Before Remediation (Blocked)", color="#DC2626")
    b2 = ax1.bar([i + w/2 for i in x], after_counts, width=w, label="After Remediation (Passed)", color="#16A34A")
    ax1.set_xticks(x)
    ax1.set_xticklabels(cats, fontsize=9)
    ax1.set_ylabel("Fixable Vulnerability Count", fontsize=9.5)
    ax1.set_title("Trivy & OWASP Fixable Vulnerabilities (Before vs After)", fontsize=10.5, fontweight="bold")
    ax1.set_ylim(0, 7.5)
    ax1.legend(loc="upper right", fontsize=8.5)
    ax1.grid(axis="y", linestyle="--", alpha=0.4)
    for bar in list(b1) + list(b2):
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, h + 0.18, f"{int(h)}",
                 ha="center", va="bottom", fontsize=9, fontweight="bold")

    # Right subplot: SonarCloud Quality Gate metrics
    ax2.axis("off")
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.text(5, 9.2, "SonarCloud Quality Gate: PASSED (Grade A)",
             ha="center", va="center", fontsize=11, fontweight="bold", color="#0F172A")
    cards = [
        (0.5, 5.2, "96.2%", "Line Test Coverage\n(50 JUnit 5 Tests)", "#16A34A"),
        (5.2, 5.2, "0 Bugs", "Reliability Rating: A\n(1.0 Best Value)", "#2563EB"),
        (0.5, 1.0, "0 Vulns", "Security Rating: A\n(0 Hotspots)", "#7C3AED"),
        (5.2, 1.0, "0 Smells", "Maintainability: A\n(0.0% Duplication)", "#0D9488"),
    ]
    for cx, cy, big, sub, col in cards:
        draw_box(ax2, cx, cy, 4.3, 3.4, big, sub, fc=col, fontsize=13)

    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig3_devsecops_remediation.png", dpi=220)
    plt.close(fig)

    # --- Figure 4: Monitoring & Alert Firing Curve ---
    fig, ax = plt.subplots(figsize=(11, 4.0), dpi=220)
    fig.patch.set_facecolor("white")
    times = ["T+0s\n(Normal)", "T+15s\n(Burst Start)", "T+30s", "T+45s\n(Pending)", "T+60s", "T+90s", "T+105s\n(FIRING)", "T+120s\n(Email Sent)"]
    rej_rate = [4.0, 62.0, 83.3, 94.0, 100.0, 100.0, 100.0, 100.0]
    threshold = [50.0] * len(times)

    ax.plot(times, rej_rate, marker="o", linewidth=2.6, color="#DC2626", label="Observed Rejection Ratio (%)")
    ax.plot(times, threshold, linestyle="--", linewidth=1.8, color="#D97706", label="Alert Threshold (>50% for 1m)")
    ax.fill_between(range(len(times)), rej_rate, threshold,
                    where=[r >= 50 for r in rej_rate], color="#FCA5A5", alpha=0.35)
    ax.set_ylim(0, 115)
    ax.set_ylabel("Rejection Ratio (%)", fontsize=9.5)
    ax.set_title("Task 6 & TC08 — FinSecurePayHighRejectionRate Alert Trigger & Notification Timeline",
                 fontsize=11, fontweight="bold")
    ax.annotate("Prometheus: state=pending", xy=(3, 94), xytext=(2.0, 106),
                arrowprops=dict(arrowstyle="->", color="#B45309"), fontsize=8.5, fontweight="bold", color="#B45309")
    ax.annotate("Alertmanager: state=active -> Email to chungyi.pitt@gmail.com", xy=(6, 100), xytext=(3.6, 75),
                arrowprops=dict(arrowstyle="->", color="#991B1B"), fontsize=8.5, fontweight="bold", color="#991B1B")
    ax.legend(loc="lower right", fontsize=8.5)
    ax.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig4_observability_alert_dashboard.png", dpi=220)
    plt.close(fig)

    # --- Figure 5: AI-Assisted Incident Triage Architecture ---
    fig, ax = plt.subplots(figsize=(11.5, 4.2), dpi=220)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4.4)
    ax.axis("off")
    fig.patch.set_facecolor("#F8FAFC")
    ax.text(6.0, 4.05, "Task 7 AI Use Case — AI-Assisted Incident Triage & Root-Cause Analysis Architecture",
            ha="center", va="center", fontsize=12, fontweight="bold", color="#0F172A")

    draw_box(ax, 0.3, 1.5, 2.0, 1.4, "1. Alertmanager", "Webhook Trigger on\nFinSecurePay Alerts", fc="#B45309", fontsize=9)
    draw_box(ax, 2.8, 1.5, 2.4, 1.4, "2. AI Triage Service", "K8s Pod (Read-Only RBAC)\nPII Redaction & Correlation", fc="#1E3A8A", fontsize=9)
    draw_box(ax, 5.7, 2.8, 2.6, 0.9, "Prometheus + Elasticsearch", "±30m Metrics & ECS Logs", fc="#0F766E", fontsize=8)
    draw_box(ax, 5.7, 1.75, 2.6, 0.9, "Jenkins + K8s Rollout API", "Last 3 Builds & Config Diffs", fc="#0369A1", fontsize=8)
    draw_box(ax, 5.7, 0.7, 2.6, 0.9, "Amazon Bedrock LLM", "ap-southeast-1 (Redacted)\nRanked RCA + Runbook Steps", fc="#6D28D9", fontsize=8)
    draw_box(ax, 8.9, 1.5, 2.8, 1.4, "3. Human-in-the-Loop", "60s RCA Email / Slack\n1-Click Jenkins MODE=rollback", fc="#15803D", fontsize=9)

    akw = dict(arrowstyle="->", color="#1E293B", lw=1.8)
    ax.annotate("", xy=(2.8, 2.2), xytext=(2.3, 2.2), arrowprops=akw)
    ax.annotate("", xy=(5.7, 3.25), xytext=(5.2, 2.4), arrowprops=akw)
    ax.annotate("", xy=(5.7, 2.2), xytext=(5.2, 2.2), arrowprops=akw)
    ax.annotate("", xy=(5.7, 1.15), xytext=(5.2, 2.0), arrowprops=akw)
    ax.annotate("", xy=(8.9, 2.2), xytext=(8.3, 1.15), arrowprops=akw)

    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig5_ai_triage_architecture.png", dpi=220)
    plt.close(fig)

    # --- Figure 0: Cover Background (DevOps & AI Theme, 16:9 Widescreen) ---
    import numpy as np
    fig, ax = plt.subplots(figsize=(13.333, 7.5), dpi=200)
    ax.set_xlim(0, 13.333)
    ax.set_ylim(0, 7.5)
    ax.axis("off")

    # Smooth dark navy -> deep indigo -> cyber teal gradient background
    grad = np.zeros((300, 500, 3))
    for i in range(300):
        for j in range(500):
            u = j / 500.0
            v = i / 300.0
            r = (6 + 18 * u + 12 * (1 - v)) / 255.0
            g = (12 + 28 * u + 22 * v) / 255.0
            b = (28 + 65 * u + 35 * (1 - v)) / 255.0
            grad[i, j] = [min(1, r), min(1, g), min(1, b)]
    ax.imshow(grad, extent=[0, 13.333, 0, 7.5], aspect="auto", zorder=0)

    # Subtle cyber grid lines
    for gx in np.linspace(0, 13.333, 28):
        ax.plot([gx, gx], [0, 7.5], color="#38BDF8", alpha=0.05, lw=0.6, zorder=1)
    for gy in np.linspace(0, 7.5, 16):
        ax.plot([0, 13.333], [gy, gy], color="#38BDF8", alpha=0.05, lw=0.6, zorder=1)

    # Right-side DevOps Infinity Loop (Glowing Cyan / Violet)
    t = np.linspace(0, 2 * np.pi, 400)
    scale_x, scale_y = 1.85, 0.95
    cx, cy = 10.15, 4.75
    inf_x = cx + scale_x * np.sin(t)
    inf_y = cy + scale_y * np.sin(t) * np.cos(t)
    for lw, al in [(18, 0.06), (11, 0.14), (6, 0.30), (2.8, 0.90)]:
        ax.plot(inf_x, inf_y, color="#38BDF8", alpha=al, lw=lw, zorder=2)

    ax.text(cx - 0.92, cy, "DEV\nBuild • Test\nSecOps", ha="center", va="center",
            color="#E0F2FE", fontsize=9.5, fontweight="bold", zorder=4)
    ax.text(cx + 0.92, cy, "OPS\nDeploy • EKS\nMonitor", ha="center", va="center",
            color="#DDD6FE", fontsize=9.5, fontweight="bold", zorder=4)

    # AI Neural Network Constellation (Right / Lower-Right)
    ai_nodes = [
        (8.2, 2.5), (8.9, 3.1), (8.8, 1.8), (9.7, 2.6), (9.8, 1.4),
        (10.6, 3.0), (10.7, 2.0), (11.5, 2.7), (11.6, 1.5), (12.4, 2.2),
        (12.2, 3.4), (7.6, 1.7)
    ]
    for i_n, (x1, y1) in enumerate(ai_nodes):
        for j_n, (x2, y2) in enumerate(ai_nodes):
            if i_n < j_n and np.hypot(x2 - x1, y2 - y1) < 1.55:
                ax.plot([x1, x2], [y1, y2], color="#A78BFA", alpha=0.32, lw=1.2, zorder=2)
    for (nx, ny) in ai_nodes:
        ax.scatter([nx], [ny], s=95, color="#38BDF8", alpha=0.28, zorder=3)
        ax.scatter([nx], [ny], s=28, color="#F0F9FF", alpha=0.95, zorder=4)

    # AI Core Badge on right
    ai_box = mpatches.FancyBboxPatch((8.55, 0.65), 3.9, 0.62, boxstyle="round,pad=0.02,rounding_size=0.12",
                                     facecolor="#1E1B4B", edgecolor="#818CF8", linewidth=1.5, alpha=0.88, zorder=4)
    ax.add_patch(ai_box)
    ax.text(10.5, 0.96, "AI-Driven Observability • Cloud-Native DevSecOps",
            ha="center", va="center", color="#C7D2FE", fontsize=9.5, fontweight="bold", zorder=5)

    # Left glowing accent bar
    ax.plot([0.62, 0.62], [1.0, 6.5], color="#38BDF8", lw=4.5, alpha=0.95, zorder=4)
    ax.plot([0.62, 3.8], [6.5, 6.5], color="#38BDF8", lw=2.0, alpha=0.75, zorder=4)

    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    fig.savefig(FIG_DIR / "fig0_cover_bg_devops_ai.png", dpi=200)
    plt.close(fig)


# =============================================================================
# STEP 2: GENERATE 10-SLIDE POWERPOINT PRESENTATION (.PPTX)
# =============================================================================
def add_header(slide, prs, slide_num, title, subtitle):
    banner = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.05))
    banner.fill.solid()
    banner.fill.fore_color.rgb = RGBColor(15, 23, 42)
    banner.line.fill.background()

    tf = banner.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.4)
    tf.margin_top = Inches(0.12)
    p = tf.paragraphs[0]
    p.text = f"Slide {slide_num}  |  {title}"
    p.font.size = Pt(21)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)

    p2 = tf.add_paragraph()
    p2.text = subtitle
    p2.font.size = Pt(11.5)
    p2.font.color.rgb = RGBColor(148, 163, 184)

    # Footer bar
    footer = slide.shapes.add_textbox(Inches(0.4), Inches(7.12), Inches(12.5), Inches(0.3))
    ftf = footer.text_frame
    fp = ftf.paragraphs[0]
    fp.text = f"Capstone Assignment: FinSecure Pay  |  Chungyi Wang  |  2026/11/04  |  https://github.com/chungyipitt-stack/finsecure-pay  |  Slide {slide_num}/10"
    fp.font.size = Pt(9)
    fp.font.color.rgb = RGBColor(100, 116, 139)


def add_cover_slide(prs, blank):
    cover = prs.slides.add_slide(blank)
    # Full-slide DevOps & AI background image
    cover.shapes.add_picture(
        str(FIG_DIR / "fig0_cover_bg_devops_ai.png"),
        Inches(0), Inches(0), width=Inches(13.333), height=Inches(7.5)
    )

    # Top pill badge
    badge = cover.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.95), Inches(1.15), Inches(4.8), Inches(0.48))
    badge.fill.solid()
    badge.fill.fore_color.rgb = RGBColor(15, 23, 42)
    badge.line.color.rgb = RGBColor(56, 189, 248)
    badge.line.width = Pt(1.5)
    btf = badge.text_frame
    bp = btf.paragraphs[0]
    bp.text = "CLOUD-NATIVE DEVOPS • DEVSECOPS • AI OPERATIONS"
    bp.font.size = Pt(10.5)
    bp.font.bold = True
    bp.font.color.rgb = RGBColor(56, 189, 248)

    # Main Title Box
    tbox = cover.shapes.add_textbox(Inches(0.95), Inches(1.85), Inches(7.2), Inches(2.6))
    ttf = tbox.text_frame
    ttf.word_wrap = True
    p_title = ttf.paragraphs[0]
    p_title.text = "Capstone Assignment:\nFinSecure Pay: Automating a\nCloud-Native DevOps Pipeline"
    p_title.font.size = Pt(32)
    p_title.font.bold = True
    p_title.font.color.rgb = RGBColor(255, 255, 255)
    p_title.space_after = Pt(12)

    p_sub = ttf.add_paragraph()
    p_sub.text = "End-to-End CI/CD, Shift-Left Security Gates, AWS EKS Orchestration, Full-Stack Observability & AI-Assisted Incident Triage"
    p_sub.font.size = Pt(13.5)
    p_sub.font.color.rgb = RGBColor(186, 230, 253)

    # Presenter & Date Card
    meta_card = cover.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.95), Inches(4.75), Inches(6.6), Inches(1.65))
    meta_card.fill.solid()
    meta_card.fill.fore_color.rgb = RGBColor(15, 23, 42)
    meta_card.line.color.rgb = RGBColor(129, 140, 248)
    meta_card.line.width = Pt(1.5)
    mtf = meta_card.text_frame
    mtf.word_wrap = True
    mtf.margin_left = Inches(0.25)
    mtf.margin_top = Inches(0.18)

    mp1 = mtf.paragraphs[0]
    mp1.text = "Author / Presenter:   Chungyi Wang"
    mp1.font.size = Pt(16)
    mp1.font.bold = True
    mp1.font.color.rgb = RGBColor(255, 255, 255)
    mp1.space_after = Pt(6)

    mp2 = mtf.add_paragraph()
    mp2.text = "Submission Date:      2026/11/04"
    mp2.font.size = Pt(14)
    mp2.font.bold = True
    mp2.font.color.rgb = RGBColor(56, 189, 248)
    mp2.space_after = Pt(6)

    mp3 = mtf.add_paragraph()
    mp3.text = "GitHub Repository:    https://github.com/chungyipitt-stack/finsecure-pay"
    mp3.font.size = Pt(11)
    mp3.font.color.rgb = RGBColor(203, 213, 225)

    cover.notes_slide.notes_text_frame.text = (
        "Title Slide: Capstone Assignment: FinSecure Pay: Automating a Cloud-Native DevOps Pipeline. "
        "Presented by Chungyi Wang, Date: 2026/11/04."
    )


def add_bullet_card(slide, left, top, width, height, heading, bullets, header_rgb=(30, 58, 138), font_size=11):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    card.fill.solid()
    card.fill.fore_color.rgb = RGBColor(248, 250, 252)
    card.line.color.rgb = RGBColor(*header_rgb)
    card.line.width = Pt(1.5)

    tf = card.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.18)
    tf.margin_right = Inches(0.18)
    tf.margin_top = Inches(0.14)

    p0 = tf.paragraphs[0]
    p0.text = heading
    p0.font.size = Pt(font_size + 2)
    p0.font.bold = True
    p0.font.color.rgb = RGBColor(*header_rgb)
    p0.space_after = Pt(6)

    for b in bullets:
        p = tf.add_paragraph()
        p.text = f"• {b}"
        p.font.size = Pt(font_size)
        p.font.color.rgb = RGBColor(30, 41, 59)
        p.space_after = Pt(4)


def build_pptx():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    # --- COVER PAGE (First Page: DevOps & AI Theme) ---
    add_cover_slide(prs, blank)

    # --- SLIDE 1: Project overview and business problem ---
    s1 = prs.slides.add_slide(blank)
    add_header(s1, prs, 1, "Project Overview & Business Problem",
               "FinSecure Pay — Automating a Cloud-Native DevSecOps Pipeline on AWS EKS")
    add_bullet_card(s1, 0.4, 1.25, 6.1, 2.7, "Business Context & Problem Statement", [
        "FinSecure Pay is a fast-growing fintech startup offering a real-time Transaction Validation API (/health and /validate).",
        "Manual builds, ad-hoc testing, and unvalidated deployments created release bottlenecks, inconsistent quality, and security exposure.",
        "Lack of automated vulnerability gates and production observability delayed incident detection and increased recovery time (MTTR).",
        "Core Objective: Deliver an automated, secure, observable, and self-healing cloud-native CI/CD pipeline from Git commit to AWS EKS."
    ], header_rgb=(15, 23, 42))
    add_bullet_card(s1, 0.4, 4.15, 6.1, 2.85, "End-to-End Solution Highlights (Tasks 1–7)", [
        "Task 1: Spring Boot 3.5.16 (Java 21) REST API with 8 validation rules & 50 JUnit 5 tests (96.2% coverage).",
        "Task 2: Multi-stage non-root Alpine JRE 21 container image published to Docker Hub.",
        "Task 3: High-availability AWS EKS deployment (ap-southeast-1, 2 replicas, NLB, PDB, self-healing).",
        "Task 4 & 5: 11-stage Jenkins CI/CD pipeline with SonarCloud, OWASP Dependency-Check, and Trivy gates.",
        "Task 6 & 7: Prometheus, Grafana, Alertmanager, EFK logging, and AI-assisted incident triage design."
    ], header_rgb=(30, 58, 138))
    s1.shapes.add_picture(str(FIG_DIR / "fig1_architecture_diagram.png"), Inches(6.7), Inches(1.3), width=Inches(6.25))
    s1.notes_slide.notes_text_frame.text = (
        "Welcome to the FinSecure Pay Capstone presentation. Slide 1 introduces the fintech business challenge: "
        "replacing error-prone manual releases of a transaction validation API with a fully automated, security-gated "
        "cloud-native CI/CD pipeline deploying to Amazon EKS in ap-southeast-1."
    )

    # --- SLIDE 2: Application and Git implementation ---
    s2 = prs.slides.add_slide(blank)
    add_header(s2, prs, 2, "Application & Git Implementation (Task 1)",
               "Spring Boot 3.5.16 Transaction Validation Microservice, JUnit 5 Test Suite & GitHub Workflow")
    add_bullet_card(s2, 0.4, 1.25, 6.1, 5.7, "REST API Endpoints & 8 Configurable Validation Rules", [
        "GET /health: Returns HTTP 200 OK with service status ('UP'), active version tag (<semver>-<build>-<sha>), environment ('production-eks'), and UTC timestamp.",
        "POST /validate: Evaluates payment payload and returns HTTP 200 APPROVED or HTTP 422 REJECTED with structured Violation codes:",
        "  1. TXN_ID_FORMAT — Matches ^TXN-[A-Z0-9-]{4,32}$",
        "  2. ACCOUNT_FORMAT — 10–16 digit numeric source & destination accounts",
        "  3. SAME_SOURCE_AND_DESTINATION — Prevents self-transfers",
        "  4. SOURCE_ACCOUNT_BLOCKED / DESTINATION_ACCOUNT_BLOCKED — Configurable blocklist",
        "  5. AMOUNT_BELOW_MINIMUM (0.01) & AMOUNT_EXCEEDS_LIMIT (10,000.00)",
        "  6. AMOUNT_SCALE_INVALID — At most 2 decimal places",
        "  7. UNSUPPORTED_CURRENCY — Configurable ISO allowlist (SGD, USD, EUR, GBP)",
        "  8. TIMESTAMP_OUT_OF_RANGE — Rejects clock skew > ±5 minutes",
        "Custom Micrometer counters: finsecure_validations_total{result} and finsecure_validation_violations_total{code}."
    ], header_rgb=(30, 58, 138), font_size=10.2)
    add_bullet_card(s2, 6.75, 1.25, 6.15, 2.75, "Unit & Integration Testing (50 JUnit 5 Tests — 100% Pass)", [
        "TransactionValidationServiceTest (38 tests): Boundary, negative, and multi-violation tests across all 8 business rules.",
        "TransactionControllerTest (4 tests): MockMvc HTTP 200, 422, 400 (malformed JSON), and 415 (wrong Content-Type).",
        "ApiKeyFilterTest (5 tests): Constant-time X-API-Key authentication & open dev mode.",
        "FinSecurePayApplicationTests (5 tests) & ControlledEvaluationTest (1 test): E2E probes, /actuator/prometheus metrics, and TC02 evaluation gate.",
        "JaCoCo Coverage: 96.2% line coverage (mvn clean verify)."
    ], header_rgb=(22, 163, 74), font_size=10.2)
    add_bullet_card(s2, 6.75, 4.2, 6.15, 2.75, "Git Repository Structure & Hygiene", [
        "GitHub Repository: https://github.com/chungyipitt-stack/finsecure-pay.git",
        "Clean modular layout: src/, k8s/, infra/, jenkins/, monitoring/, logging/, security/, scripts/, testcases/, docs/, evidence/.",
        ".gitignore enforces strict secret exclusion (.env, *secret*.yaml, kubeconfig, target/).",
        "Maven Wrapper (mvnw / mvnw.cmd) committed with 100755 executable permissions for deterministic builds."
    ], header_rgb=(15, 23, 42), font_size=10.2)

    # --- SLIDE 3: Docker and Kubernetes/cloud deployment ---
    s3 = prs.slides.add_slide(blank)
    add_header(s3, prs, 3, "Docker Containerisation & AWS EKS Deployment (Tasks 2 & 3)",
               "Multi-Stage Layered Dockerfile, Docker Hub Registry & Resilient Kubernetes Architecture on AWS EKS")
    add_bullet_card(s3, 0.4, 1.25, 6.1, 5.7, "Task 2: Multi-Stage Hardened Container Image", [
        "Stage 1 (Builder): eclipse-temurin:21-jdk-alpine compiles the JAR and runs spring-boot-jarmode-tools extract --layers.",
        "Stage 2 (Runtime): Minimal eclipse-temurin:21-jre-alpine with apk upgrade --no-cache to patch base OS packages.",
        "Layered Copy: Dependencies -> spring-boot-loader -> snapshot-dependencies -> application layer for fast caching.",
        "Non-Root Execution: Runs as dedicated user/group finsecure (UID/GID 10001) with MaxRAMPercentage=75.0.",
        "Built-in Docker HEALTHCHECK probing http://127.0.0.1:8080/health.",
        "Published to Docker Hub: chungyi1979/finsecure-pay:1.0.0, :1.1.0-4-9ea7e21, and :latest."
    ], header_rgb=(2, 132, 199), font_size=10.5)
    add_bullet_card(s3, 6.75, 1.25, 6.15, 5.7, "Task 3: AWS EKS Cluster & Self-Healing Deployment", [
        "AWS EKS Cluster: finsecure-eks in ap-southeast-1 (Kubernetes v1.34, 2x m7i-flex.large managed nodes) provisioned via infra/eks-cluster.yaml.",
        "Manifests in k8s/: 00-namespace.yaml, 10-configmap.yaml, 20-deployment.yaml, 30-service.yaml, 40-monitoring.yaml.",
        "High Availability: 2 replicas spread across AvailabilityZones/nodes via topologySpreadConstraints + PodDisruptionBudget (minAvailable: 1).",
        "Zero-Downtime Rollout: RollingUpdate (maxUnavailable: 0, maxSurge: 1), 5s preStop hook, and 3-tier probes (startup, readiness, liveness).",
        "Container SecurityContext: runAsNonRoot, readOnlyRootFilesystem, capabilities drop ALL, RuntimeDefault seccomp.",
        "Self-Healing Verified (TC06): Deleting pod finsecure-pay-754c5d8fdc-k9jq7 triggered immediate ReplicaSet recreation; 114/114 external NLB health probes succeeded (0% packet loss)."
    ], header_rgb=(5, 150, 105), font_size=10.2)

    # --- SLIDE 4: CI/CD pipeline ---
    s4 = prs.slides.add_slide(blank)
    add_header(s4, prs, 4, "CI/CD Pipeline Automation with Jenkins (Task 4)",
               "11-Stage Declarative Pipeline, Automated Triggers, Failed-Test Gate, Rolling Updates & Rollbacks")
    s4.shapes.add_picture(str(FIG_DIR / "fig2_jenkins_pipeline_matrix.png"), Inches(0.4), Inches(1.2), width=Inches(12.5))
    add_bullet_card(s4, 0.4, 5.1, 4.0, 1.9, "Automated Trigger & Traceability", [
        "Jenkins configured as code (jenkins/casc.yaml) polling GitHub every 2 min (pollSCM H/2).",
        "Traceable image tags: <semver>-<build>-<gitsha> (e.g., 1.1.0-4-9ea7e21) injected into /health."
    ], header_rgb=(30, 58, 138), font_size=9.8)
    add_bullet_card(s4, 4.65, 5.1, 4.0, 1.9, "Failed Test Blocks Deploy (Build #2)", [
        "When a unit test fails (or SIMULATE_TEST_FAILURE=true in TC02), Jenkins halts at 'Unit Test'.",
        "Package, Docker Push & EKS Deploy are skipped; failure email sent automatically."
    ], header_rgb=(220, 38, 38), font_size=9.8)
    add_bullet_card(s4, 8.9, 5.1, 4.0, 1.9, "Zero-Downtime Rollout & Rollback", [
        "Build #4 rolled out v1.1.0-4-9ea7e21 to EKS and verified /health via Smoke Test.",
        "Build #5 (MODE=rollback, ROLLBACK_TAG=1.0.0) reverted EKS to v1.0.0 in 59s."
    ], header_rgb=(22, 163, 74), font_size=9.8)

    # --- SLIDE 5: DevSecOps and security implementation ---
    s5 = prs.slides.add_slide(blank)
    add_header(s5, prs, 5, "DevSecOps & Security Implementation (Task 5)",
               "Shift-Left Security Gates (SonarCloud, OWASP Dependency-Check, Trivy), Vulnerability Remediation & Secret Hygiene")
    s5.shapes.add_picture(str(FIG_DIR / "fig3_devsecops_remediation.png"), Inches(0.4), Inches(1.2), width=Inches(12.5))
    add_bullet_card(s5, 0.4, 5.15, 6.1, 1.85, "Real Security Gate Block & Remediation (Builds #3 -> #4)", [
        "Gate 1 (SonarCloud): Enforced via -Dsonar.qualitygate.wait=true — PASSED (0 Bugs, 0 Vulns, 96.2% coverage).",
        "Gate 2 (OWASP Dependency-Check): failBuildOnCVSS=7 blocked Build #3 on log4j-api 2.24.3 & Spring CPEs.",
        "Gate 3 (Trivy Image Scan): --severity HIGH,CRITICAL --exit-code 1 blocked initial Tomcat 10.1.55 (6 CRIT) & Jackson 2.21.4 (5 HIGH).",
        "Remediation: Upgraded Tomcat -> 10.1.59, Jackson -> 2.21.8, Log4j2 -> 2.26.0 in pom.xml; governed expiring risk acceptance (until 2026-12-31) for non-applicable Spring 7-only advisories."
    ], header_rgb=(124, 58, 237), font_size=9.5)
    add_bullet_card(s5, 6.75, 5.15, 6.15, 1.85, "Secret Management & Runtime Hardening", [
        "Zero secrets in Git: All 5 CI credentials (dockerhub-creds, sonarcloud-token, nvd-api-key, aws-creds, finsecure-api-key) reside in Jenkins Credentials Store via JCasC.",
        "Credentials bound strictly via withCredentials(...) and masked as **** in Jenkins console logs.",
        "EKS Secret finsecure-pay-secrets injected dynamically at deploy time; ephemeral kubeconfig deleted in post { always }."
    ], header_rgb=(15, 23, 42), font_size=9.5)

    # --- SLIDE 6: Monitoring, alerting, and logging ---
    s6 = prs.slides.add_slide(blank)
    add_header(s6, prs, 6, "Monitoring, Alerting & Centralised Logging (Task 6)",
               "Prometheus + Grafana Dashboards, Alertmanager + Jenkins Email Notifications & EFK Structured Logging")
    s6.shapes.add_picture(str(FIG_DIR / "fig4_observability_alert_dashboard.png"), Inches(0.4), Inches(1.2), width=Inches(12.5))
    add_bullet_card(s6, 0.4, 5.05, 4.0, 1.95, "Prometheus & Grafana (6 Panels)", [
        "ServiceMonitor scrapes /actuator/prometheus every 15s.",
        "Grafana dashboard 'FinSecure Pay — Operational Overview' tracks RPS, Rejection Ratio %, Violation Codes, p50/p95/p99 Latency, CPU/Heap & Pod Replicas."
    ], header_rgb=(15, 118, 110), font_size=9.5)
    add_bullet_card(s6, 4.65, 5.05, 4.0, 1.95, "Alert Firing & Dual Email Notifications", [
        "6 PrometheusRules in k8s/40-monitoring.yaml.",
        "Injected rejected transactions (>50% ratio) -> FinSecurePayHighRejectionRate fired -> Alertmanager sent email to chungyi.pitt@gmail.com.",
        "Jenkins sent FAILURE (Build #2/#3) & SUCCESS (Build #4/#5) emails."
    ], header_rgb=(180, 83, 9), font_size=9.5)
    add_bullet_card(s6, 8.9, 5.05, 4.0, 1.95, "EFK Centralised Logging Stack", [
        "Spring Boot outputs Elastic Common Schema (ECS) structured JSON logs with MDC trace fields (app.transaction.id, app.validation.status).",
        "Fluent Bit DaemonSet ships container logs to Elasticsearch (fluentbit-*); searchable in Kibana & kubectl logs."
    ], header_rgb=(30, 58, 138), font_size=9.5)

    # --- SLIDE 7: AI application and architecture ---
    s7 = prs.slides.add_slide(blank)
    add_header(s7, prs, 7, "AI Application in DevOps & Architecture (Task 7)",
               "AI-Assisted Incident Triage & Root-Cause Analysis (RCA) Integrated with Alertmanager, Observability & Jenkins")
    s7.shapes.add_picture(str(FIG_DIR / "fig5_ai_triage_architecture.png"), Inches(0.4), Inches(1.2), width=Inches(12.5))
    add_bullet_card(s7, 0.4, 5.1, 4.0, 1.9, "Problem & Required Data Inputs", [
        "Problem: Manual correlation across Grafana, Kibana, Jenkins builds, and K8s events during 3 a.m. incidents inflates MTTR.",
        "Inputs: PromQL metrics (±30m), ECS WARN/ERROR log clusters, last 3 Jenkins build diffs, K8s rollout history, and docs/RUNBOOK.md (RAG)."
    ], header_rgb=(30, 58, 138), font_size=9.5)
    add_bullet_card(s7, 4.65, 5.1, 4.0, 1.9, "Expected Operational Benefits", [
        "Delivers a ranked Top-3 Root-Cause Analysis summary within 60 seconds of an alert firing (30–50% MTTR reduction).",
        "Correlates config/code changes (e.g., ConfigMap limit change in Build #N) directly with rejection spikes and provides a 1-click rollback link."
    ], header_rgb=(22, 163, 74), font_size=9.5)
    add_bullet_card(s7, 8.9, 5.1, 4.0, 1.9, "Risks, Limitations & Governance", [
        "Hallucination Control: Model must cite metric/log timestamps; output is advisory only.",
        "PCI-DSS / PDPA Privacy: Account numbers masked in Fluent Bit before indexing; hosted in-region (Amazon Bedrock ap-southeast-1).",
        "Human-in-the-Loop: Engineers approve any rollback execution."
    ], header_rgb=(109, 40, 217), font_size=9.5)

    # --- SLIDE 8: Test results, recovery/rollback, and key findings ---
    s8 = prs.slides.add_slide(blank)
    add_header(s8, prs, 8, "Core Evaluation Test Results, Recovery & Key Findings",
               "100% Pass Rate Across All 8 Core Evaluation Test Cases (testcases/testcase_expected_result.jpg)")

    rows_data = [
        ("TC01", "Run unit tests", "Required unit tests pass.", "50/50 JUnit 5 tests passed (0 failures, 96.2% line coverage).", "PASS"),
        ("TC02", "Introduce a controlled failing test", "Jenkins pipeline fails, deployment blocked.", "Unit Test stage FAILED; Package, Push & EKS Deploy skipped.", "PASS"),
        ("TC03", "Run the container and access /health", "Application returns a healthy response.", "Container & EKS NLB /health returned HTTP 200 OK (status=UP).", "PASS"),
        ("TC04", "Inspect the Kubernetes deployment", "At least two application pods running & Ready.", "deployment/finsecure-pay has 2/2 Running & Ready pods on EKS.", "PASS"),
        ("TC05", "Deploy a new image/version", "Kubernetes rollout completes successfully.", "Rolled out v1.1.0-4-9ea7e21 with zero downtime; verified on /health.", "PASS"),
        ("TC06", "Delete or restart one pod", "Kubernetes automatically recreates the pod.", "Deleted pod recreated by ReplicaSet to 1/1 Ready; 0 dropped requests.", "PASS"),
        ("TC07", "Introduce critical/high security finding", "The security gate blocks the release.", "OWASP (CVSS >= 7.0) & Trivy gates failed build and blocked release.", "PASS"),
        ("TC08", "Trigger a monitoring condition", "Alert fires and a notification is received.", "FinSecurePayHighRejectionRate fired; email sent to chungyi.pitt@gmail.com.", "PASS"),
    ]
    tbl_shape = s8.shapes.add_table(len(rows_data) + 1, 5, Inches(0.4), Inches(1.25), Inches(12.5), Inches(5.6))
    tbl = tbl_shape.table
    widths = [Inches(0.8), Inches(3.0), Inches(3.1), Inches(4.5), Inches(1.1)]
    for i, w in enumerate(widths):
        tbl.columns[i].width = w

    headers = ["ID", "Core Test Case", "Expected Result", "Verified Live Evidence (testcases/results/)", "Status"]
    for i, h in enumerate(headers):
        cell = tbl.cell(0, i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(15, 23, 42)
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 255)

    for r_idx, row in enumerate(rows_data, start=1):
        bg = RGBColor(241, 245, 249) if r_idx % 2 == 0 else RGBColor(255, 255, 255)
        for c_idx, val in enumerate(row):
            cell = tbl.cell(r_idx, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(22, 163, 74) if c_idx == 4 else bg
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(9.8)
            p.font.bold = (c_idx in (0, 4))
            p.font.color.rgb = RGBColor(255, 255, 255) if c_idx == 4 else RGBColor(15, 23, 42)

    # --- SLIDE 9: Additional evidence — End-to-End Evidence Catalog ---
    s9 = prs.slides.add_slide(blank)
    add_header(s9, prs, 9, "Additional Evidence — Live Verification Artifacts (Tasks 1–6)",
               "Complete Repository Evidence Package Captured from Live AWS EKS, Jenkins, SonarCloud, Trivy & EFK")
    add_bullet_card(s9, 0.4, 1.25, 6.1, 5.7, "Tasks 1–4 Evidence Artifacts", [
        "Task 1 (evidence/task1/t1-junit-and-api-verification.txt):",
        "  • 50/50 JUnit 5 tests passing; live /health (200 OK) & /validate (200 APPROVED / 422 REJECTED).",
        "Task 2 (evidence/task2/t2-docker-push.txt):",
        "  • Multi-stage non-root Docker build & push digest sha256:9f2272f4... on Docker Hub.",
        "Task 3 (evidence/task3/t3-k8s-state.txt, t3-external-access.txt, t3-self-healing.txt):",
        "  • 2x m7i-flex.large EKS nodes Ready; 2/2 pods Running; 114/114 NLB probes OK during pod deletion.",
        "Task 4 (evidence/task4/t4-failed-test-blocks-deploy.txt, t4-successful-pipeline-and-rollout.txt, t4-rollback-to-known-good.txt):",
        "  • Build #2 failed-test block; Build #4 v1.1.0-4-9ea7e21 rollout; Build #5 rollback to v1.0.0."
    ], header_rgb=(30, 58, 138), font_size=10)
    add_bullet_card(s9, 6.75, 1.25, 6.15, 5.7, "Tasks 5–6 & Evaluation Suite Evidence Artifacts", [
        "Task 5 (evidence/task5/):",
        "  • t5-sonarcloud-analysis.txt: Quality Gate OK, 96.2% coverage, 0 bugs/vulns/smells.",
        "  • t5-jenkins-security-gate-blocked.txt: Build #3 blocked by OWASP Dependency-Check (CVSS >= 7.0).",
        "  • t5-trivy-blocked-before-remediation.txt & t5-trivy-after-remediation.txt: 11 HIGH/CRIT CVEs fixed.",
        "  • t5-remediated-pipeline-and-secrets.txt: Build #4 clean pass + masked credentials (****).",
        "Task 6 (evidence/task6/):",
        "  • t6-install-monitoring.txt & t6-alert-triggered.txt: FinSecurePayHighRejectionRate firing + Gmail receipt.",
        "  • t6-jenkins-email-notification.txt: Jenkins FAILURE & SUCCESS emails to chungyi.pitt@gmail.com.",
        "  • t6-elasticsearch-logs.txt & t6-kubectl-logs.txt: Structured ECS JSON logs indexed in EFK."
    ], header_rgb=(15, 118, 110), font_size=10)

    # --- SLIDE 10: Lessons learned, future improvements & project links ---
    s10 = prs.slides.add_slide(blank)
    add_header(s10, prs, 10, "Lessons Learned, Future Roadmap & Accessible Project Links",
               "Engineering Reflections, Production Evolution Path & Verifiable Public Links")
    add_bullet_card(s10, 0.4, 1.25, 6.1, 2.8, "Key Engineering Lessons Learned", [
        "Security gates must fail the build (-Dsonar.qualitygate.wait=true, failBuildOnCVSS=7, trivy --exit-code 1) rather than merely archiving passive reports.",
        "Ordering fast checks (unit tests in 13s) ahead of heavier scans (SonarCloud, OWASP, Trivy) keeps developer feedback loops short.",
        "Persisting the NVD database (/var/jenkins_home/dependency-check-data) with an NVD API key reduced OWASP scan time from 524s (Build #3) to 13s (Build #4).",
        "Isolating test properties (finsecure.security.api-key=) prevents CI container environment variables from polluting integration tests."
    ], header_rgb=(30, 58, 138), font_size=9.8)
    add_bullet_card(s10, 0.4, 4.2, 6.1, 2.75, "Future Production Improvements", [
        "GitOps & Progressive Delivery: Adopt Argo CD + Argo Rollouts for automated canary analysis on Prometheus rejection/latency metrics.",
        "Supply-Chain Security: Sign container images with Sigstore Cosign and enforce admission via Kyverno on EKS.",
        "Secret Management & Identity: Migrate to AWS Secrets Manager + External Secrets Operator and EKS IAM Roles for Service Accounts (IRSA).",
        "Production AI Copilot: Deploy the read-only AI Triage microservice on EKS connected to Amazon Bedrock."
    ], header_rgb=(109, 40, 217), font_size=9.8)
    add_bullet_card(s10, 6.75, 1.25, 6.15, 5.7, "Accessible Project Links & Secret Hygiene Attestation", [
        "GitHub Repository (Public):",
        "  https://github.com/chungyipitt-stack/finsecure-pay",
        "Docker Hub Image Repository (Public):",
        "  https://hub.docker.com/r/chungyi1979/finsecure-pay/tags",
        "SonarCloud Quality Gate Dashboard (Public):",
        "  https://sonarcloud.io/project/overview?id=chungyipitt-stack_finsecure-pay",
        "AWS EKS Application LoadBalancer (/health):",
        "  http://a67e1d0b5b459453d9d9be62e598e148-a0206fab5a570f79.elb.ap-southeast-1.amazonaws.com/health",
        "AWS EKS Grafana Dashboard:",
        "  http://a8ecf49751a7f43acae13e9c6d8f50d7-1691906106.ap-southeast-1.elb.amazonaws.com",
        "Security & Secret Exclusion Attestation:",
        "  Zero passwords, API keys, tokens, or private keys are included in this presentation, report, or Git repository."
    ], header_rgb=(15, 23, 42), font_size=9.8)

    pptx_path = BASE_DIR / "FinSecure_Pay_Capstone_Presentation.pptx"
    prs.save(str(pptx_path))
    return pptx_path


# =============================================================================
# STEP 3: GENERATE DETAILED SUMMARY REPORT IN WORD FORMAT (.DOCX)
# =============================================================================
def add_code_block(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = DocInches(0.2)
    p.paragraph_format.space_before = DocPt(4)
    p.paragraph_format.space_after = DocPt(6)
    run = p.add_run(text.strip())
    run.font.name = "Consolas"
    run.font.size = DocPt(8.5)
    run.font.color.rgb = DocRGB(15, 23, 42)


def read_snippet(rel_path, max_lines=45):
    import re
    p = ROOT_DIR / rel_path
    if not p.exists():
        return f"[File {rel_path} not found]"
    raw = p.read_bytes()
    if raw.startswith(b"\xff\xfe") or b"\x00" in raw[:100]:
        text = raw.decode("utf-16", errors="replace")
    else:
        text = raw.decode("utf-8-sig", errors="replace")
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    lines = text.splitlines()
    if len(lines) > max_lines:
        return "\n".join(lines[:max_lines]) + f"\n... ({len(lines) - max_lines} additional lines in {rel_path})"
    return "\n".join(lines)


def build_docx():
    doc = Document()
    for section in doc.sections:
        section.top_margin = DocInches(0.8)
        section.bottom_margin = DocInches(0.8)
        section.left_margin = DocInches(0.85)
        section.right_margin = DocInches(0.85)

    # Dedicated Cover Page (First Page) with DevOps & AI Theme
    doc.add_picture(str(FIG_DIR / "fig0_cover_bg_devops_ai.png"), width=DocInches(6.5))
    doc.add_paragraph()

    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = title_p.add_run("Capstone Assignment: FinSecure Pay: Automating a Cloud-Native DevOps Pipeline\n\n")
    r_title.font.size = DocPt(20)
    r_title.font.bold = True
    r_title.font.color.rgb = DocRGB(15, 23, 42)

    r_sub = title_p.add_run("Detailed Technical Summary Report, DevSecOps Architecture, AI Application & Evaluation Evidence\n\n")
    r_sub.font.size = DocPt(13)
    r_sub.font.color.rgb = DocRGB(30, 58, 138)

    r_author = title_p.add_run("Author: Chungyi Wang\nDate: 2026/11/04\n")
    r_author.font.size = DocPt(14)
    r_author.font.bold = True
    r_author.font.color.rgb = DocRGB(15, 23, 42)

    # Metadata & Links Table
    meta_table = doc.add_table(rows=9, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.style = "Table Grid"
    meta_rows = [
        ("Assignment Title", "Capstone Assignment: FinSecure Pay: Automating a Cloud-Native DevOps Pipeline"),
        ("Author & Date", "Chungyi Wang  |  2026/11/04 (Individual Capstone Work)"),
        ("GitHub Repository (Public)", "https://github.com/chungyipitt-stack/finsecure-pay"),
        ("Docker Hub Repository (Public)", "https://hub.docker.com/r/chungyi1979/finsecure-pay/tags"),
        ("SonarCloud Dashboard (Public)", "https://sonarcloud.io/project/overview?id=chungyipitt-stack_finsecure-pay"),
        ("AWS EKS Cluster & Region", "finsecure-eks (ap-southeast-1, Kubernetes v1.34, 2x m7i-flex.large nodes)"),
        ("Live EKS App Endpoint (/health)", "http://a67e1d0b5b459453d9d9be62e598e148-a0206fab5a570f79.elb.ap-southeast-1.amazonaws.com/health"),
        ("Live Grafana Dashboard Endpoint", "http://a8ecf49751a7f43acae13e9c6d8f50d7-1691906106.ap-southeast-1.elb.amazonaws.com"),
        ("Secret Hygiene Attestation", "All passwords, API keys, tokens, and private keys are strictly excluded (<REDACTED> / ****)."),
    ]
    for idx, (k, v) in enumerate(meta_rows):
        c0 = meta_table.cell(idx, 0)
        c1 = meta_table.cell(idx, 1)
        r0 = c0.paragraphs[0].add_run(k)
        r0.bold = True
        r0.font.size = DocPt(9.5)
        r1 = c1.paragraphs[0].add_run(v)
        r1.font.size = DocPt(9.5)

    doc.add_page_break()

    # 1. Executive Summary & Business Problem (Slide 1)
    doc.add_heading("1. Project Overview, Business Problem & Architecture (Slide 1 & Task 7)", level=1)
    doc.add_paragraph(
        "FinSecure Pay is a financial technology startup providing a real-time Transaction Validation microservice "
        "used by payment gateways to verify account formats, blocklists, currency rules, transaction limits, and "
        "timestamp freshness before settlement. Previously, manual builds, inconsistent testing, lack of automated "
        "vulnerability scanning, and manual server deployments created operational risk and slow recovery times."
    )
    doc.add_paragraph(
        "This project designs, implements, and verifies an automated, cloud-native DevSecOps delivery pipeline covering "
        "all seven capstone tasks: (1) Spring Boot 3.5 / Java 21 REST microservice and 50 JUnit 5 tests in GitHub; "
        "(2) Multi-stage non-root Docker containerisation published to Docker Hub; (3) High-availability Kubernetes "
        "deployment on AWS EKS with self-healing and zero-downtime rollouts; (4) 11-stage Jenkins CI/CD automation "
        "with automated triggers, failed-test blocking, rolling updates, and 1-click rollbacks; (5) Shift-left DevSecOps "
        "gates integrating SonarCloud, OWASP Dependency-Check, and Trivy with real CVE remediation and encrypted secret "
        "management; (6) Full observability with Prometheus, Grafana, Alertmanager email notifications, Jenkins pipeline "
        "email notifications, and EFK centralised structured logging; and (7) Comprehensive architecture documentation "
        "and an AI-assisted incident triage and root-cause analysis design."
    )
    doc.add_picture(str(FIG_DIR / "fig1_architecture_diagram.png"), width=DocInches(6.5))

    # Major Technical Decisions Table
    doc.add_heading("1.1 Major Technical & Architectural Decisions", level=2)
    tech_tbl = doc.add_table(rows=8, cols=3)
    tech_tbl.style = "Table Grid"
    tech_headers = ["Layer / Domain", "Selected Technology", "Engineering Justification & Design Decision"]
    for i, h in enumerate(tech_headers):
        r = tech_tbl.cell(0, i).paragraphs[0].add_run(h)
        r.bold = True
        r.font.size = DocPt(9.5)
    tech_rows = [
        ("Application & Build", "Java 21, Spring Boot 3.5.16, Maven Wrapper", "Spring Boot Actuator natively exposes /actuator/health/{liveness,readiness} and /actuator/prometheus. Validation thresholds are externalised via ConfigMap environment variables."),
        ("Containerisation", "Multi-stage Dockerfile (eclipse-temurin:21-jre-alpine)", "Separates JDK/Maven build layer from minimal JRE runtime, extracts Spring Boot layers, patches Alpine OS packages, and runs as non-root UID 10001."),
        ("Orchestration & Cloud", "AWS EKS (ap-southeast-1, 2x m7i-flex.large)", "Managed Kubernetes control plane with AWS NLB, topologySpreadConstraints across nodes, PodDisruptionBudget (minAvailable: 1), and RollingUpdate (maxUnavailable: 0)."),
        ("CI/CD Automation", "Jenkins LTS + JCasC + Declarative Jenkinsfile", "Configuration-as-Code reproduces Jenkins jobs and credentials from git-ignored .env. Fail-fast stage ordering runs unit tests (13s) before heavy scans and image builds."),
        ("DevSecOps Gates", "SonarCloud + OWASP Dependency-Check + Trivy", "Three mandatory blocking gates: SonarCloud qualitygate.wait=true, OWASP failBuildOnCVSS=7, and Trivy --severity HIGH,CRITICAL --exit-code 1."),
        ("Monitoring & Alerting", "kube-prometheus-stack + Gmail SMTP", "ServiceMonitor scrapes custom business counters (finsecure_validations_total) every 15s; PrometheusRule triggers Alertmanager emails when rejection ratio > 50%."),
        ("Centralised Logging", "Fluent Bit + Elasticsearch + Kibana (EFK)", "Application emits Elastic Common Schema (ECS) JSON logs with MDC transaction IDs and validation status, enabling zero-regex indexing in Elasticsearch."),
    ]
    for r_i, row in enumerate(tech_rows, start=1):
        for c_i, val in enumerate(row):
            run = tech_tbl.cell(r_i, c_i).paragraphs[0].add_run(val)
            run.font.size = DocPt(9)

    # 2. Task 1: Application Development & Version Control (Slide 2)
    doc.add_heading("2. Task 1 — Application Development & Version Control (Slide 2)", level=1)
    doc.add_paragraph(
        "The FinSecure Pay service exposes two primary REST endpoints on port 8080: GET /health and POST /validate, "
        "plus Kubernetes probes (/actuator/health/liveness, /actuator/health/readiness) and Prometheus metrics (/actuator/prometheus). "
        "POST /validate evaluates all eight validation rules and returns every violation code in a single response so callers "
        "can remediate issues in one round-trip and Prometheus can track per-rule violation rates."
    )
    doc.add_heading("2.1 Task 1 Verification Evidence (50/50 JUnit 5 Tests & Live API Responses)", level=2)
    add_code_block(doc, read_snippet("evidence/task1/t1-junit-and-api-verification.txt", max_lines=45))

    # 3. Task 2 & Task 3: Containerisation & Kubernetes Cloud Deployment (Slide 3)
    doc.add_heading("3. Tasks 2 & 3 — Docker Containerisation & AWS EKS Deployment (Slide 3)", level=1)
    doc.add_paragraph(
        "Task 2 packages the application using a multi-stage Dockerfile that compiles and extracts layered JAR contents "
        "in eclipse-temurin:21-jdk-alpine and copies them into a hardened eclipse-temurin:21-jre-alpine image running as "
        "non-root user finsecure (UID 10001). Images are tagged with both semantic versions (1.0.0) and immutable CI "
        "traceability tags (<semver>-<build>-<gitsha>, e.g. 1.1.0-4-9ea7e21) and pushed to Docker Hub (chungyi1979/finsecure-pay)."
    )
    doc.add_heading("3.1 Task 2 Evidence — Docker Hub Push & Digest Verification", level=2)
    add_code_block(doc, read_snippet("evidence/task2/t2-docker-push.txt", max_lines=25))

    doc.add_paragraph(
        "Task 3 provisions the production AWS EKS cluster (finsecure-eks in ap-southeast-1) with two m7i-flex.large "
        "worker nodes and deploys the finsecure namespace, ConfigMap (finsecure-pay-config), Secret (finsecure-pay-secrets), "
        "2-replica Deployment (finsecure-pay), PodDisruptionBudget, and AWS Network Load Balancer Service."
    )
    doc.add_heading("3.2 Task 3 Evidence — EKS Cluster State, External NLB Access & Pod Self-Healing", level=2)
    add_code_block(doc, read_snippet("evidence/task3/t3-k8s-state.txt", max_lines=32))
    add_code_block(doc, read_snippet("evidence/task3/t3-self-healing.txt", max_lines=30))

    # 4. Task 4: CI/CD Pipeline Automation (Slide 4)
    doc.add_heading("4. Task 4 — CI/CD Pipeline Automation with Jenkins (Slide 4)", level=1)
    doc.add_paragraph(
        "The declarative Jenkinsfile defines an 11-stage pipeline connected to GitHub (pollSCM H/2 * * * *): "
        "Checkout -> Build -> Unit Test -> Code Quality (SonarCloud) -> Dependency Scan (OWASP) -> Package -> "
        "Container Build -> Image Scan (Trivy) -> Push (Docker Hub) -> Deploy (EKS) / Rollback (EKS) -> Smoke Test, "
        "with post-build email notifications on both success and failure."
    )
    doc.add_picture(str(FIG_DIR / "fig2_jenkins_pipeline_matrix.png"), width=DocInches(6.5))
    doc.add_heading("4.1 Task 4 Evidence — Failed Unit Test Halts Pipeline & Prevents Deployment (Build #2)", level=2)
    add_code_block(doc, read_snippet("evidence/task4/t4-failed-test-blocks-deploy.txt", max_lines=35))
    doc.add_heading("4.2 Task 4 Evidence — Full End-to-End Pipeline & Version 1.1.0 Rollout (Build #4)", level=2)
    add_code_block(doc, read_snippet("evidence/task4/t4-successful-pipeline-and-rollout.txt", max_lines=40))
    doc.add_heading("4.3 Task 4 Evidence — Automated Rollback to Known-Good Release 1.0.0 (Build #5)", level=2)
    add_code_block(doc, read_snippet("evidence/task4/t4-rollback-to-known-good.txt", max_lines=35))

    # 5. Task 5: DevSecOps & Security Integration (Slide 5)
    doc.add_heading("5. Task 5 — DevSecOps & Security Implementation (Slide 5)", level=1)
    doc.add_paragraph(
        "Three automated security gates enforce shift-left security across source code, third-party dependencies, "
        "and container images: (1) SonarCloud Static Analysis & Quality Gate, (2) OWASP Dependency-Check failing on "
        "any vulnerability with CVSS >= 7.0 (HIGH/CRITICAL), and (3) Trivy container image scanning failing on any "
        "fixable HIGH or CRITICAL vulnerability (--exit-code 1)."
    )
    doc.add_picture(str(FIG_DIR / "fig3_devsecops_remediation.png"), width=DocInches(6.5))
    doc.add_heading("5.1 Task 5 Evidence — SonarCloud Quality Gate Passed (96.2% Coverage, Grade A)", level=2)
    add_code_block(doc, read_snippet("evidence/task5/t5-sonarcloud-analysis.txt", max_lines=38))
    doc.add_heading("5.2 Task 5 Evidence — Pipeline Blocked by Security Gate Before Remediation (Build #3 & Trivy)", level=2)
    add_code_block(doc, read_snippet("evidence/task5/t5-jenkins-security-gate-blocked.txt", max_lines=36))
    doc.add_heading("5.3 Task 5 Evidence — Remediated Pipeline Pass & Masked Secret Management (Build #4)", level=2)
    add_code_block(doc, read_snippet("evidence/task5/t5-remediated-pipeline-and-secrets.txt", max_lines=40))

    # 6. Task 6: Monitoring, Alerting & Logging (Slide 6)
    doc.add_heading("6. Task 6 — Monitoring, Alerting & Centralised Logging (Slide 6)", level=1)
    doc.add_paragraph(
        "Prometheus, Grafana, and Alertmanager (kube-prometheus-stack) are deployed in the monitoring namespace on EKS, "
        "scraping /actuator/prometheus every 15 seconds via ServiceMonitor. A custom 6-panel Grafana dashboard "
        "visualises request rate, validation rejection ratio, violation code breakdown, p50/p95/p99 latency, and pod "
        "resources. In the logging namespace, a Fluent Bit DaemonSet ships Elastic Common Schema (ECS) JSON container "
        "logs to Elasticsearch and Kibana."
    )
    doc.add_picture(str(FIG_DIR / "fig4_observability_alert_dashboard.png"), width=DocInches(6.5))
    doc.add_heading("6.1 Task 6 Evidence — Alert Firing & Email Notifications (Alertmanager & Jenkins)", level=2)
    add_code_block(doc, read_snippet("testcases/results/TC08-trigger-monitoring-alert.txt", max_lines=35))
    add_code_block(doc, read_snippet("evidence/task6/t6-jenkins-email-notification.txt", max_lines=30))
    doc.add_heading("6.2 Task 6 Evidence — Centralised EFK Structured JSON Logs & Pod Logs", level=2)
    add_code_block(doc, read_snippet("evidence/task6/t6-elasticsearch-logs.txt", max_lines=30))

    # 7. Task 7: AI Application in DevOps & Architecture (Slide 7)
    doc.add_heading("7. Task 7 — AI Application in DevOps: AI-Assisted Incident Triage & RCA (Slide 7)", level=1)
    doc.add_picture(str(FIG_DIR / "fig5_ai_triage_architecture.png"), width=DocInches(6.5))
    ai_sections = [
        ("Problem Statement", "When production alerts such as FinSecurePayHighRejectionRate fire, the on-call engineer must manually correlate Prometheus metrics, Kibana ECS logs, recent Jenkins build commits, ConfigMap changes, and Kubernetes events. During off-hours incidents, manual triage takes 15–30 minutes and increases Mean Time to Resolution (MTTR)."),
        ("Required Data & Inputs", "1) Prometheus PromQL metrics over a ±30-minute window (rejection ratio, violation code distribution, p95 latency, pod restarts); 2) Aggregated WARN/ERROR ECS JSON log patterns from Elasticsearch; 3) Last 3 Jenkins build metadata (image tag, git commit diff, dependency/Trivy scan summary) and kubectl rollout history; 4) Operational runbook entries (docs/RUNBOOK.md) via Retrieval-Augmented Generation (RAG)."),
        ("Expected Operational Benefits", "Generates an automated, evidence-backed Top-3 Root-Cause Analysis (RCA) summary within 60 seconds of an alert firing, targeting a 30–50% reduction in MTTR. Rapidly pinpoints deployment-induced or configuration-induced regressions and provides a pre-populated Jenkins MODE=rollback link."),
        ("Risks, Limitations & Governance", "1) Hallucinations: Prompt enforces strict citation of metric values and log timestamps; AI output is advisory only. 2) Data Privacy (PCI-DSS / PDPA): Account numbers are masked in Fluent Bit before indexing, and only redacted aggregates are sent to an in-region model (Amazon Bedrock in ap-southeast-1). 3) Prompt Injection: Log fields are isolated as untrusted data delimiters. 4) Human-in-the-Loop: Production rollbacks require explicit engineer approval."),
        ("Proposed Integration", "Alertmanager adds a webhook_configs receiver pointing to a lightweight read-only AI Triage Deployment in EKS. Upon receiving an alert payload, the service queries Prometheus, Elasticsearch, and Jenkins REST APIs, invokes Amazon Bedrock with the RAG runbook context, and dispatches the enriched RCA report and 1-click rollback URL to the ops email/Slack channel."),
    ]
    for heading, body in ai_sections:
        p = doc.add_paragraph()
        r_h = p.add_run(f"{heading}: ")
        r_h.bold = True
        p.add_run(body)

    # 8. Core Test Cases for Evaluation (Slide 8)
    doc.add_heading("8. Core Test Cases for Evaluation — TC01 to TC08 (Slide 8)", level=1)
    doc.add_paragraph(
        "All eight Core Test Cases specified in testcases/testcase_expected_result.jpg are implemented as automated, "
        "repeatable scripts in the testcases/ directory and verified against the live environment (8/8 PASS)."
    )
    tc_table = doc.add_table(rows=9, cols=4)
    tc_table.style = "Table Grid"
    for i, h in enumerate(["ID", "Test Case", "Expected Result", "Verified Output Summary (Status: PASS)"]):
        r = tc_table.cell(0, i).paragraphs[0].add_run(h)
        r.bold = True
        r.font.size = DocPt(9.5)
    tc_rows = [
        ("TC01", "Run unit tests", "Required unit tests pass.", "50/50 JUnit 5 tests pass (0 failures, 0 errors, 96.2% coverage) — testcases/results/TC01-unit-tests.txt"),
        ("TC02", "Introduce a controlled failing test", "Jenkins pipeline fails, and deployment does not proceed.", "ControlledEvaluationTest fails on -Dfinsecure.test.simulateFailure=true; Jenkins Build #2 halted at Unit Test and skipped Package, Push & Deploy — testcases/results/TC02-controlled-failing-test.txt"),
        ("TC03", "Run the container and access /health", "Application returns a healthy response.", "Container and EKS NLB return HTTP 200 OK with {\"status\":\"UP\",\"service\":\"finsecure-pay\"} — testcases/results/TC03-container-health.txt"),
        ("TC04", "Inspect the Kubernetes deployment", "At least two application pods are running and Ready.", "deployment/finsecure-pay has 2/2 Running & Ready pods across 2 EKS worker nodes — testcases/results/TC04-inspect-k8s-deployment.txt"),
        ("TC05", "Deploy a new image/version", "Kubernetes rollout completes successfully.", "Rolling update to chungyi1979/finsecure-pay:1.1.0-4-9ea7e21 succeeded with zero downtime; /health confirmed new version — testcases/results/TC05-deploy-new-version.txt"),
        ("TC06", "Delete or restart one pod", "Kubernetes automatically recreates the pod.", "Deleted pod was immediately replaced by ReplicaSet controller to 1/1 Ready with zero failed /health requests — testcases/results/TC06-delete-pod-self-healing.txt"),
        ("TC07", "Introduce a controlled critical/high security finding", "The security gate blocks the release.", "OWASP Dependency-Check (CVSS >= 7.0) and Trivy (--exit-code 1) failed the pipeline and blocked release — testcases/results/TC07-controlled-security-gate.txt"),
        ("TC08", "Trigger a monitoring condition", "Alert fires and a notification is received.", "Injected rejected transactions drove rejection ratio to 100%; FinSecurePayHighRejectionRate fired and Alertmanager emailed chungyi.pitt@gmail.com — testcases/results/TC08-trigger-monitoring-alert.txt"),
    ]
    for r_i, row in enumerate(tc_rows, start=1):
        for c_i, val in enumerate(row):
            run = tc_table.cell(r_i, c_i).paragraphs[0].add_run(val)
            run.font.size = DocPt(9)

    # 9. Lessons Learned & Future Improvements (Slides 9-10)
    doc.add_heading("9. Lessons Learned & Future Roadmap (Slides 9–10)", level=1)
    lessons = [
        "Enforcing Blocking Quality & Security Gates: Security scanners only protect production when configured with hard failure thresholds (-Dsonar.qualitygate.wait=true, failBuildOnCVSS=7, trivy --exit-code 1) and governed, time-bound suppressions.",
        "Fast-Feedback Pipeline Ordering & Caching: Running fast unit tests (13s) ahead of network-bound scans and persisting the NVD CVE database (/var/jenkins_home/dependency-check-data) reduced OWASP scan duration from 524s to 13s.",
        "Test Environment Isolation: Explicitly isolating test properties (finsecure.security.api-key=) ensures container-level secrets in CI agents do not alter unit/integration test behaviour.",
        "Business-Level Observability: Custom Micrometer metrics (finsecure_validations_total{result}) detect application-level anomalies (such as fraud bursts or misconfigured limits) that infrastructure CPU/memory metrics never surface.",
        "Future Roadmap: Evolve toward GitOps with Argo CD and Argo Rollouts canary releases, Cosign image signing with Kyverno admission control, AWS Secrets Manager with External Secrets Operator and IRSA, and a live EKS deployment of the AI Incident Triage service.",
    ]
    for item in lessons:
        doc.add_paragraph(item, style="List Bullet")

    docx_path = BASE_DIR / "FinSecure_Pay_Capstone_Summary_Report.docx"
    try:
        doc.save(str(docx_path))
        return docx_path
    except PermissionError:
        alt_path = BASE_DIR / "FinSecure_Pay_Capstone_Summary_Report_Updated.docx"
        doc.save(str(alt_path))
        return alt_path


if __name__ == "__main__":
    generate_figures()
    pptx_out = build_pptx()
    docx_out = build_docx()
    print(f"Generated PowerPoint: {pptx_out}")
    print(f"Generated Word Report: {docx_out}")
