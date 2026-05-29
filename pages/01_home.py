"""Page 01 — Home Dashboard: system health + last release decision + agent feed."""
import streamlit as st
import json

st.set_page_config(page_title="Home | AI TestPilot X", layout="wide")
st.title("AI TestPilot X")
st.caption("Autonomous AI-Powered Quality Engineering Platform")

from config import settings

# ── System Health Panel ───────────────────────────────────────────────────────
st.subheader("System Health")
hcol1, hcol2, hcol3, hcol4 = st.columns(4)

# Gemini
hcol1.metric("Gemini API", "🟢 Ready" if settings.GEMINI_API_KEY else "🔴 No Key")

# ChromaDB
try:
    from core.rag_engine import rag_engine
    tc_count = rag_engine.count("testcases")
    hcol2.metric("ChromaDB", f"🟢 {tc_count} test cases")
except Exception:
    hcol2.metric("ChromaDB", "🔴 Error")

# Selenium Grid / Execution Mode
if settings.EXECUTION_MODE == "GRID":
    try:
        from execution.grids.selenium_grid import check_grid_health
        grid_ok = check_grid_health(settings.SELENIUM_GRID_URL)
        hcol3.metric("Selenium Grid", "🟢 Online" if grid_ok else "🔴 Offline")
    except Exception:
        hcol3.metric("Selenium Grid", "🔴 Error")
else:
    hcol3.metric("Execution Mode", f"✅ {settings.EXECUTION_MODE}")

hcol4.metric("Environment", settings.APP_ENV)

st.divider()

# ── Last Session KPIs ─────────────────────────────────────────────────────────
try:
    from storage.db import get_session
    from storage.models.reports import ReportRecord
    db = get_session()
    last_report = db.query(ReportRecord).order_by(ReportRecord.created_at.desc()).first()
    db.close()
except Exception:
    last_report = None

# Also check session state
session_report = st.session_state.get("report")

if last_report or session_report:
    st.subheader("Last Run Summary")
    if session_report:
        rdata = session_report if isinstance(session_report, dict) else session_report.model_dump()
    elif last_report:
        rdata = json.loads(last_report.report_json or "{}")
    else:
        rdata = {}

    kc1, kc2, kc3, kc4 = st.columns(4)
    kc1.metric("Total Tests", rdata.get("total_tests", "—"))
    kc2.metric("Passed", rdata.get("passed", "—"))
    kc3.metric("Failed", rdata.get("failed", "—"))
    kc4.metric("Risk Score", f"{rdata.get('risk_score', 0):.0f}/100" if rdata.get("risk_score") is not None else "—")

    decision = rdata.get("decision", "GO")
    if decision == "NO_GO":
        st.error("🔴 RELEASE DECISION: NO GO")
    elif decision == "GO_WITH_RISK":
        st.warning("🟡 RELEASE DECISION: GO WITH RISK")
    else:
        st.success("🟢 RELEASE DECISION: GO")
else:
    st.info("No reports yet. Run the full pipeline to see results here.")

st.divider()

# ── Agent Activity Feed ───────────────────────────────────────────────────────
st.subheader("Agent Activity Feed")
from core.event_bus import bus
history = bus.get_history()
if history:
    for event in reversed(history[-10:]):
        event_type = event.get("type", "UNKNOWN")
        payload = event.get("payload", {})
        icon = "✅" if "FAILED" not in event_type else "❌"
        st.text(f"{icon} {event_type}")
else:
    st.info("No agent activity yet.")

st.divider()

# ── Agent Performance ─────────────────────────────────────────────────────────
st.subheader("Agent Performance")
try:
    import pandas as pd
    from monitoring.metrics import metrics
    agent_data = metrics.get_all()
    if agent_data:
        rows = [{
            "Agent": name,
            "Runs": m.runs,
            "Avg Latency (ms)": f"{m.avg_latency_ms:.0f}",
            "Error Rate": f"{m.error_rate:.0%}"
        } for name, m in agent_data.items()]
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.info("Agent metrics will appear here after running the pipeline.")
except Exception as e:
    st.warning(f"Could not load metrics: {e}")
