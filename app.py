"""Streamlit frontend - calls the FastAPI backend (no LangGraph imports)."""
import os
import time
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="DD Agent", page_icon="📊", layout="wide")
st.title("📊 Autonomous Due Diligence Agent")
st.caption(f"FastAPI backend → LangGraph multi-agent system • API: `{API_BASE}`")

# Health check
with st.sidebar:
    st.header("Backend Status")
    try:
        h = requests.get(f"{API_BASE}/health", timeout=3).json()
        if h.get("openai_configured"):
            st.success("✅ API online & OpenAI configured")
        else:
            st.warning("⚠️ API online but OPENAI_API_KEY missing on server")
    except Exception:
        st.error(f"❌ Cannot reach API at {API_BASE}\n\nStart it with:\n`uvicorn src.api.main:app --reload`")
        st.stop()

    st.markdown("---")
    max_iter = st.slider("Max debate iterations", 1, 3, 2)
    st.markdown("---")
    st.markdown("**Data sources** (all free):")
    st.markdown("- SEC EDGAR\n- Yahoo Finance\n- GDELT (news)\n- GitHub API")
    st.markdown("---")
    st.markdown(f"[📖 API Docs]({API_BASE}/docs)")

col1, col2 = st.columns([2, 1])
with col1:
    ticker = st.text_input("Ticker symbol", "AAPL",
                           help="US-listed ticker, e.g. AAPL, MSFT, SNOW")
with col2:
    st.write("")
    st.write("")
    run_btn = st.button("🚀 Run Analysis", type="primary",
                        use_container_width=True)

if run_btn:
    # Submit job
    try:
        r = requests.post(f"{API_BASE}/analyze",
                          json={"ticker": ticker, "max_iterations": max_iter},
                          timeout=10)
        r.raise_for_status()
        job_id = r.json()["job_id"]
        st.info(f"Job submitted: `{job_id}`")
    except Exception as e:
        st.error(f"Failed to submit job: {e}")
        st.stop()

    # Poll status
    progress = st.progress(0, "Starting...")
    status_text = st.empty()
    log = st.expander("📋 Live progress", expanded=True)
    seen_steps = []

    while True:
        try:
            status = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=5).json()
        except Exception as e:
            st.error(f"Polling error: {e}")
            break

        progress.progress(status["progress"] / 100, status.get("current_step", ""))
        step = status.get("current_step")
        if step and step not in seen_steps:
            seen_steps.append(step)
            with log:
                st.write(f"✅ **{step}**")

        if status["status"] == "completed":
            status_text.success("Analysis complete ✓")
            break
        if status["status"] == "failed":
            status_text.error(f"Failed: {status.get('error')}")
            st.stop()
        time.sleep(1.5)

    # Fetch full result
    result = requests.get(f"{API_BASE}/jobs/{job_id}/result", timeout=10).json()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rating", result.get("rating") or "N/A")
    c2.metric("Red-Flag Score",
              f"{result.get('red_flag_score', 0):.2f} / 1.00")
    c3.metric("Findings", len(result.get("all_findings", [])))
    c4.metric("Iterations", result.get("iterations", 0))

    st.subheader("📊 Score Breakdown")
    if result.get("score_breakdown"):
        st.bar_chart(result["score_breakdown"])

    tab1, tab2, tab3, tab4 = st.tabs(
        ["🚩 Red Flags", "💪 Strengths", "📑 All Findings", "📥 Download PDF"])

    with tab1:
        if not result.get("top_red_flags"):
            st.info("No material red flags detected.")
        for f in result.get("top_red_flags", []):
            st.error(f"**[{f['agent'].upper()}]** {f['claim']}")
            st.caption(f"Evidence: {f['evidence']}")
            st.caption(f"Confidence: {f['confidence']:.2f}")

    with tab2:
        if not result.get("top_strengths"):
            st.info("No standout strengths identified.")
        for f in result.get("top_strengths", []):
            st.success(f"**[{f['agent'].upper()}]** {f['claim']}")
            st.caption(f"Confidence: {f['confidence']:.2f}")

    with tab3:
        for f in result.get("all_findings", []):
            sev = {"red": "🔴", "yellow": "🟡", "info": "🟢"}.get(
                f["severity"], "⚪")
            with st.expander(f"{sev} [{f['agent']}] {f['claim'][:80]}"):
                st.write(f"**Evidence:** {f['evidence']}")
                st.write(f"**Confidence:** {f['confidence']:.2f}")
                st.write(f"**Sources:** {f.get('sources', [])}")

    with tab4:
        if result.get("report_pdf_url"):
            pdf_url = f"{API_BASE}{result['report_pdf_url']}"
            try:
                pdf_bytes = requests.get(pdf_url, timeout=15).content
                st.download_button(
                    "⬇️ Download Full PDF Report",
                    data=pdf_bytes,
                    file_name=f"{result['ticker']}_DD_Report.pdf",
                    mime="application/pdf",
                )
                st.caption(f"PDF endpoint: `{pdf_url}`")
            except Exception as e:
                st.error(f"PDF fetch failed: {e}")
