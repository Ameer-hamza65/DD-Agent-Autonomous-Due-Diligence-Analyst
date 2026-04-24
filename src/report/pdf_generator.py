"""ReportLab-based PDF generation with charts."""
import os
from datetime import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
)
from reportlab.lib import colors

CHART_DIR = "reports/_charts"
os.makedirs(CHART_DIR, exist_ok=True)


def _chart(breakdown: dict, ticker: str) -> str:
    fig, ax = plt.subplots(figsize=(6, 3.2))
    cats = list(breakdown.keys())
    vals = [breakdown[c] for c in cats]
    cols = ['#dc2626' if v > 0.5 else '#f59e0b' if v > 0.25 else '#10b981'
            for v in vals]
    ax.barh(cats, vals, color=cols)
    ax.set_xlim(0, 1.0)
    ax.set_xlabel("Risk Score (0=clean, 1=severe)")
    ax.set_title(f"{ticker} — Risk Breakdown")
    plt.tight_layout()
    path = f"{CHART_DIR}/{ticker}_breakdown.png"
    plt.savefig(path, dpi=120)
    plt.close()
    return path


def generate_pdf_report(state: dict, output_dir: str = "reports") -> str:
    os.makedirs(output_dir, exist_ok=True)
    ticker = state["ticker"]
    company = state.get("financials", {}).get("company_name") or ticker
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = f"{output_dir}/{ticker}_DD_{timestamp}.pdf"

    doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                            rightMargin=0.7*inch, leftMargin=0.7*inch,
                            topMargin=0.7*inch, bottomMargin=0.7*inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleBig', parent=styles['Title'],
                                 fontSize=26, textColor=HexColor('#1e3a8a'))
    h2 = ParagraphStyle('H2', parent=styles['Heading2'],
                        textColor=HexColor('#1e40af'), spaceBefore=14)
    body = styles['BodyText']
    flow = []

    flow.append(Paragraph("Due Diligence Report", title_style))
    flow.append(Spacer(1, 12))
    flow.append(Paragraph(f"<b>{company}</b> ({ticker})", styles['Heading1']))
    flow.append(Paragraph(f"Generated: {datetime.now():%Y-%m-%d %H:%M}", body))
    flow.append(Spacer(1, 24))

    score = state.get("red_flag_score", 0)
    rating = state.get("rating", "N/A")
    t = Table([
        ["Red-Flag Score", f"{score:.2f} / 1.00"],
        ["Rating", rating],
        ["Findings analyzed", str(len(state.get("findings", [])))],
        ["Debate iterations", str(state.get("iteration", 0))],
    ], colWidths=[2.5*inch, 3.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#eff6ff')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    flow.append(t)
    flow.append(Spacer(1, 18))
    flow.append(Image(_chart(state.get("score_breakdown", {}), ticker),
                      width=6.5*inch, height=3.4*inch))
    flow.append(PageBreak())

    flow.append(Paragraph("Executive Summary", h2))
    flow.append(Paragraph(
        f"This report synthesizes findings from 5 specialized analyst agents "
        f"(financial, news, tech, market, risk) coordinated via a LangGraph "
        f"multi-agent system with a critic-driven debate loop. "
        f"Total findings: {len(state.get('findings', []))}. "
        f"Debate iterations: {state.get('iteration', 0)}.", body))
    flow.append(Spacer(1, 12))

    flow.append(Paragraph("Top Red Flags", h2))
    red_flags = state.get("top_red_flags", [])
    if not red_flags:
        flow.append(Paragraph("<i>No material red flags detected.</i>", body))
    for f in red_flags:
        flow.append(Paragraph(f"<b>[{f['agent'].upper()}]</b> {f['claim']}", body))
        flow.append(Paragraph(f"<i>Evidence:</i> {f['evidence']}", body))
        flow.append(Paragraph(f"<i>Confidence:</i> {f['confidence']:.2f}", body))
        flow.append(Spacer(1, 8))

    flow.append(Paragraph("Top Strengths", h2))
    strengths = state.get("top_strengths", [])
    if not strengths:
        flow.append(Paragraph("<i>No standout strengths identified.</i>", body))
    for f in strengths:
        flow.append(Paragraph(f"<b>[{f['agent'].upper()}]</b> {f['claim']}", body))
        flow.append(Spacer(1, 6))

    flow.append(PageBreak())
    flow.append(Paragraph("Detailed Findings", h2))
    for agent in ["financial", "news", "tech", "market", "risk"]:
        agent_findings = [f for f in state.get("findings", [])
                          if f.get("agent") == agent]
        if not agent_findings:
            continue
        flow.append(Paragraph(f"{agent.title()} Analyst", styles['Heading3']))
        for f in agent_findings:
            sev_color = {"red": "#dc2626", "yellow": "#f59e0b",
                         "info": "#10b981"}.get(f["severity"], "#6b7280")
            flow.append(Paragraph(
                f'<font color="{sev_color}"><b>[{f["severity"].upper()}]</b></font> '
                f'{f["claim"]}', body))
            flow.append(Paragraph(f"<i>Evidence:</i> {f['evidence']}", body))
            if f.get("sources"):
                flow.append(Paragraph(
                    f"<i>Sources:</i> {', '.join(f['sources'][:3])}", body))
            flow.append(Spacer(1, 8))

    flow.append(PageBreak())
    flow.append(Paragraph("Methodology", h2))
    flow.append(Paragraph(
        "Data sources: SEC EDGAR, Yahoo Finance, GDELT Project, GitHub API. "
        "Agents are orchestrated via LangGraph with parallel fan-out followed "
        "by a critic agent. Scoring uses a deterministic weighted rubric: "
        "Financial 30%, Risk 25%, News 20%, Market 15%, Tech 10%.", body))

    doc.build(flow)
    return pdf_path
