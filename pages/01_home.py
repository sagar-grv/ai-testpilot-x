"""Page 01 — Home Dashboard."""
import streamlit as st
import json
from config import settings

st.set_page_config(page_title="Home | AI TestPilot X", page_icon="📊", layout="wide")

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<h2 style='margin:0; font-size:26px; font-weight:700;'>📊 System Overview</h2>
<p style='color:#718096; margin-top:4px;'>Real-time platform health, last run summary, and agent activity</p>
""", unsafe_allow_html=True)
st.divider()

# ── System Health ─────────────────────────────────────────────────────────────
st.markdown("### 🔧 System Health")

def health_badge(ok, label, detail=""):
    color = "#48BB78" if ok else "#FC8181"
    icon = "🟢" if ok else "🔴"
    return f"""
    <div style='background:#1E2130; border:1px solid #2E3250; border-radius:10px;
                padding:14px 18px; display:flex; align-items:center; gap:12px;'>
        <span style='font-size:20px;'>{icon}</span>
        <div>
            <div style='font-weight:600; font-size:14px;'>{label}</div>
            <div style='color:#718096; font-size:12px;'>{detail}</div>
        </div>
    </div>"""

hcol1, hcol2, hcol3, hcol4 = st.columns(4)

gemini_ok = bool(settings.GEMINI_API_KEY)
with hcol1:
    st.markdown(health_badge(gemini_ok, "Gemini API",
        "Connected" if gemini_ok else "API key required"), unsafe_allow_html=True)

try:
    from core.rag_engine import rag_engine
    tc_count = rag_engine.count("testcases")
    chroma_ok = True
    chroma_detail = f"{tc_count} test cases indexed"
except Exception:
    chroma_ok = False
    chroma_detail = "Initialization failed"
with hcol2:
    st.markdown(health_badge(chroma_ok, "ChromaDB RAG", chroma_detail), unsafe_allow_html=True)

if settings.EXECUTION_MODE == "GRID":
    try:
        import httpx
        r = httpx.get(f"{settings.SELENIUM_GRID_URL}/status", timeout=2.0)
        grid_ok = r.status_code == 200
        grid_detail = "Grid online"
    except Exception:
        grid_ok = False
        grid_detail = "Grid unreachable"
else:
    grid_ok = True
    grid_detail = f"Mode: {settings.EXECUTION_MODE}"
with hcol3:
    st.markdown(health_badge(grid_ok, "Execution Engine", grid_detail), unsafe_allow_html=True)

with hcol4:
    st.markdown(health_badge(True, "Agent Registry", "9 agents registered"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Last Run Summary ──────────────────────────────────────────────────────────
st.markdown("### 📋 Last Run Summary")

try:
    from storage.db import get_session
    from storage.models.reports import ReportRecord
    db = get_session()
    last_report = db.query(ReportRecord).order_by(ReportRecord.created_at.desc()).first()
    db.close()
except Exception:
    last_report = None

session_report = st.session_state.get("report")

if last_report or session_report:
    if session_report:
        rdata = session_report if isinstance(session_report, dict) else session_report.model_dump()
    else:
        rdata = json.loads(last_report.report_json or "{}")

    decision = rdata.get("decision", "GO")
    if decision == "NO_GO":
        st.markdown("""
        <div style='background:linear-gradient(135deg,#742A2A,#C53030);
             border-radius:12px; padding:20px 24px; margin-bottom:16px;'>
            <div style='font-size:22px; font-weight:800;'>🚫 RELEASE DECISION: NO GO</div>
            <div style='color:#FEB2B2; margin-top:6px; font-size:14px;'>Critical bugs must be resolved before release.</div>
        </div>""", unsafe_allow_html=True)
    elif decision == "GO_WITH_RISK":
        st.markdown("""
        <div style='background:linear-gradient(135deg,#744210,#C05621);
             border-radius:12px; padding:20px 24px; margin-bottom:16px;'>
            <div style='font-size:22px; font-weight:800;'>⚠️ RELEASE DECISION: GO WITH RISK</div>
            <div style='color:#FBD38D; margin-top:6px; font-size:14px;'>High severity bugs present. Proceed with caution.</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background:linear-gradient(135deg,#1A4731,#276749);
             border-radius:12px; padding:20px 24px; margin-bottom:16px;'>
            <div style='font-size:22px; font-weight:800;'>✅ RELEASE DECISION: GO</div>
            <div style='color:#9AE6B4; margin-top:6px; font-size:14px;'>All quality gates passed. Release approved.</div>
        </div>""", unsafe_allow_html=True)

    mc1, mc2, mc3, mc4, mc5 = st.columns(5)
    mc1.metric("Total Tests", rdata.get("total_tests", 0))
    mc2.metric("✅ Passed", rdata.get("passed", 0))
    mc3.metric("❌ Failed", rdata.get("failed", 0))
    mc4.metric("🐛 Bugs", (rdata.get("critical_bugs",0) + rdata.get("high_bugs",0) +
                           rdata.get("medium_bugs",0) + rdata.get("low_bugs",0)))
    mc5.metric("⚡ Risk Score", f"{rdata.get('risk_score', 0):.0f}/100")

    if rdata.get("recommendation_text"):
        st.info(f"💬 **AI Recommendation:** {rdata['recommendation_text']}")
else:
    st.markdown("""
    <div style='background:#1E2130; border:1px solid #2E3250; border-radius:12px;
         padding:32px; text-align:center;'>
        <div style='font-size:40px;'>🚀</div>
        <div style='font-size:18px; font-weight:600; margin-top:12px;'>No reports yet</div>
        <div style='color:#718096; margin-top:8px;'>
            Run the full pipeline on <strong>AI Test Generator</strong> to see results here.
        </div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Agent Activity Feed ───────────────────────────────────────────────────────
st.markdown("### ⚡ Agent Activity Feed")

from core.event_bus import bus
history = bus.get_history()

EVENT_ICONS = {
    "REQUIREMENT_ANALYZED": ("🔍", "#6C63FF"),
    "TESTCASES_GENERATED": ("📝", "#48BB78"),
    "VERIFICATION_COMPLETE": ("✅", "#48BB78"),
    "EXECUTION_APPROVED": ("👍", "#ECC94B"),
    "EXECUTION_COMPLETE": ("⚙️", "#4299E1"),
    "BUG_ANALYZED": ("🐛", "#FC8181"),
    "HEALING_COMPLETE": ("🔧", "#ED8936"),
    "REPORT_GENERATED": ("📊", "#6C63FF"),
    "AGENT_FAILED": ("❌", "#FC8181"),
}

if history:
    for event in reversed(history[-12:]):
        etype = event.get("type", "UNKNOWN")
        payload = event.get("payload", {})
        icon, color = EVENT_ICONS.get(etype, ("📌", "#718096"))
        payload_str = ", ".join(f"{k}: {v}" for k, v in list(payload.items())[:3]) if payload else ""
        st.markdown(f"""
        <div style='display:flex; align-items:center; gap:12px; padding:10px 14px;
             background:#1E2130; border-left:3px solid {color};
             border-radius:0 8px 8px 0; margin-bottom:6px;'>
            <span style='font-size:18px;'>{icon}</span>
            <div>
                <span style='font-weight:600; font-size:13px; color:{color};'>{etype}</span>
                {"<span style='color:#718096; font-size:12px; margin-left:8px;'>" + payload_str + "</span>" if payload_str else ""}
            </div>
        </div>""", unsafe_allow_html=True)
else:
    st.markdown("""
    <div style='background:#1E2130; border:1px solid #2E3250; border-radius:10px;
         padding:20px; text-align:center; color:#718096;'>
        No agent activity yet. Run the pipeline to see events here.
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Agent Performance ─────────────────────────────────────────────────────────
st.markdown("### 📈 Agent Performance")
try:
    import pandas as pd
    from monitoring.metrics import metrics
    agent_data = metrics.get_all()
    if agent_data:
        rows = [{
            "Agent": name,
            "Runs": m.runs,
            "Avg Latency (ms)": f"{m.avg_latency_ms:.0f}",
            "Error Rate": f"{m.error_rate:.0%}",
            "Status": "🟢 OK" if m.error_rate < 0.1 else "🔴 Issues"
        } for name, m in agent_data.items()]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.caption("Agent metrics will appear here after running the pipeline.")
except Exception:
    st.caption("Metrics unavailable.")
