"""Page 01 — Home Dashboard."""
import streamlit as st
import json

st.set_page_config(page_title="Home | AI TestPilot X", page_icon="📊", layout="wide")

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<h1 class="tp-page-title">📊 Home Dashboard</h1>
<p class="tp-page-subtitle">System health, last run summary, and agent activity feed</p>
""", unsafe_allow_html=True)
st.divider()

# ── System Health ─────────────────────────────────────────────────────────────
st.markdown('<div class="tp-section-title">System Health</div>', unsafe_allow_html=True)

from config import settings

def _health_card(icon, label, status, detail, ok):
    border = "#22c55e44" if ok else "#ef444444"
    bg = "#0a1a0a" if ok else "#1a0a0a"
    dot_color = "#22c55e" if ok else "#ef4444"
    status_text_color = "#4ade80" if ok else "#f87171"
    return f"""
    <div style="background:{bg}; border:1px solid {border}; border-radius:12px;
                padding:16px 18px; display:flex; align-items:center; gap:14px;">
        <div style="font-size:28px; flex-shrink:0;">{icon}</div>
        <div style="flex:1; min-width:0;">
            <div style="font-weight:700; font-size:13px; color:#F0F4FF;
                        white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{label}</div>
            <div style="font-size:11px; color:#64748B; margin-top:2px;
                        white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{detail}</div>
        </div>
        <div style="background:{dot_color}22; color:{status_text_color};
                    border:1px solid {dot_color}44; border-radius:20px;
                    padding:3px 10px; font-size:11px; font-weight:700;
                    white-space:nowrap; flex-shrink:0;">{status}</div>
    </div>"""

h1, h2, h3, h4 = st.columns(4)

gemini_ok = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.startswith("AIzaSy"))
with h1:
    st.markdown(_health_card("🤖", "Gemini API",
        "Connected" if gemini_ok else "Invalid Key",
        "gemini-2.5-flash" if gemini_ok else "Check .env for AIzaSy... key",
        gemini_ok), unsafe_allow_html=True)

try:
    from core.rag_engine import rag_engine
    tc = rag_engine.count("testcases")
    chroma_ok = True
    chroma_detail = f"{tc} test cases · {rag_engine.count('bugs')} bugs indexed"
except Exception as e:
    chroma_ok = False
    chroma_detail = str(e)[:50]
with h2:
    st.markdown(_health_card("🗄️", "ChromaDB RAG",
        "Ready" if chroma_ok else "Error",
        chroma_detail, chroma_ok), unsafe_allow_html=True)

if settings.EXECUTION_MODE == "GRID":
    try:
        import httpx
        r = httpx.get(f"{settings.SELENIUM_GRID_URL}/status", timeout=2.0)
        exec_ok = r.status_code == 200
        exec_detail = f"Grid online · {settings.SELENIUM_GRID_URL}"
    except Exception:
        exec_ok = False
        exec_detail = "Grid unreachable"
else:
    exec_ok = True
    exec_detail = f"Mode: {settings.EXECUTION_MODE} · No browser required"
with h3:
    st.markdown(_health_card("⚙️", "Execution Engine",
        settings.EXECUTION_MODE, exec_detail, exec_ok), unsafe_allow_html=True)

try:
    import agents
    from agents.registry import AgentRegistry
    n = len(AgentRegistry.list_agents())
    reg_ok = n > 0
    reg_detail = f"{n} agents registered"
except Exception:
    reg_ok = False
    reg_detail = "Registry load failed"
with h4:
    st.markdown(_health_card("🔧", "Agent Registry",
        f"{n} Agents" if reg_ok else "Error",
        reg_detail, reg_ok), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Last Run Summary ──────────────────────────────────────────────────────────
st.markdown('<div class="tp-section-title">Last Run Summary</div>', unsafe_allow_html=True)

rdata = None
try:
    from storage.db import get_session
    from storage.models.reports import ReportRecord
    db = get_session()
    last = db.query(ReportRecord).order_by(ReportRecord.created_at.desc()).first()
    db.close()
    if last:
        rdata = json.loads(last.report_json or "{}")
except Exception:
    pass

session_report = st.session_state.get("report")
if session_report:
    rdata = session_report if isinstance(session_report, dict) else session_report.model_dump()

if rdata:
    decision = rdata.get("decision", "GO")
    BANNERS = {
        "NO_GO": ("#7f1d1d", "#ef4444", "#fca5a5", "🚫", "NO GO",
                  "Critical defects must be resolved. Release is blocked."),
        "GO_WITH_RISK": ("#78350f", "#f59e0b", "#fde68a", "⚠️", "GO WITH RISK",
                         "High severity issues present. Proceed with caution."),
        "GO": ("#14532d", "#22c55e", "#bbf7d0", "✅", "GO",
               "All quality gates passed. Release is approved."),
    }
    bg, accent, text, icon, label, subtitle = BANNERS.get(decision, BANNERS["GO"])
    st.markdown(f"""
    <div style="background:linear-gradient(135deg, {bg}, {bg}cc);
                border:1px solid {accent}55; border-radius:14px;
                padding:22px 28px; margin-bottom:20px;">
        <div style="display:flex; align-items:center; gap:16px;">
            <span style="font-size:44px;">{icon}</span>
            <div>
                <div style="font-size:11px; color:{text}99; font-weight:700;
                            text-transform:uppercase; letter-spacing:0.1em;">
                    Release Decision</div>
                <div style="font-size:28px; font-weight:900; color:{text};
                            letter-spacing:-0.02em;">{label}</div>
                <div style="font-size:13px; color:{text}cc; margin-top:3px;">{subtitle}</div>
            </div>
        </div>
        {f'<div style="margin-top:14px; background:rgba(0,0,0,0.25); border-radius:8px; padding:10px 16px; font-size:13px; color:{text}cc; font-style:italic;">{rdata.get("recommendation_text","")}</div>' if rdata.get("recommendation_text") else ""}
    </div>""", unsafe_allow_html=True)

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Tests", rdata.get("total_tests", 0))
    k2.metric("✅ Passed", rdata.get("passed", 0))
    k3.metric("❌ Failed", rdata.get("failed", 0))
    k4.metric("🐛 Bugs", sum(rdata.get(k, 0) for k in ["critical_bugs","high_bugs","medium_bugs","low_bugs"]))
    k5.metric("⚡ Risk Score", f"{rdata.get('risk_score', 0):.0f} / 100")
else:
    st.markdown("""
    <div style="background:#0F1117; border:1px dashed #1E2337; border-radius:14px;
                padding:48px 32px; text-align:center;">
        <div style="font-size:48px; margin-bottom:12px;">🚀</div>
        <div style="font-size:18px; font-weight:700; color:#F0F4FF; margin-bottom:6px;">
            No reports yet</div>
        <div style="font-size:13px; color:#475569; max-width:360px; margin:0 auto;">
            Run the full pipeline on the <strong style="color:#6C63FF;">AI Test Generator</strong>
            page to generate your first report.
        </div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Agent Activity Feed ───────────────────────────────────────────────────────
st.markdown('<div class="tp-section-title">Agent Activity Feed</div>', unsafe_allow_html=True)

try:
    from core.event_bus import bus
    history = bus.get_history()
except Exception:
    history = []

EVENT_META = {
    "REQUIREMENT_ANALYZED":  ("🔍", "#6C63FF", "Requirement analyzed"),
    "TESTCASES_GENERATED":   ("📝", "#22c55e", "Test cases generated"),
    "VERIFICATION_COMPLETE": ("✅", "#22c55e", "Verification complete"),
    "EXECUTION_APPROVED":    ("👤", "#f59e0b", "Execution approved"),
    "EXECUTION_COMPLETE":    ("▶️", "#3b82f6", "Execution complete"),
    "BUG_ANALYZED":          ("🐛", "#ef4444", "Bug analysis done"),
    "HEALING_COMPLETE":      ("🔧", "#f97316", "Healing complete"),
    "REPORT_GENERATED":      ("📊", "#6C63FF", "Report generated"),
    "AGENT_FAILED":          ("❌", "#ef4444", "Agent failed"),
}

if history:
    for ev in reversed(history[-12:]):
        etype = ev.get("type", "UNKNOWN")
        payload = ev.get("payload", {})
        icon2, color, friendly = EVENT_META.get(etype, ("📌", "#475569", etype))
        payload_str = " · ".join(f"{k}: {v}" for k, v in list(payload.items())[:3]) if payload else ""
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:12px; padding:11px 16px;
                    background:#0F1117; border:1px solid #1E2337;
                    border-left:3px solid {color}; border-radius:0 10px 10px 0;
                    margin-bottom:5px; transition:background 0.15s;">
            <span style="font-size:16px; flex-shrink:0;">{icon2}</span>
            <div style="flex:1; min-width:0;">
                <span style="font-weight:700; font-size:13px; color:{color};">{friendly}</span>
                {f'<span style="color:#475569; font-size:12px; margin-left:10px;">{payload_str}</span>' if payload_str else ""}
            </div>
            <span style="font-size:11px; color:#334155; flex-shrink:0;">{etype}</span>
        </div>""", unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="background:#0F1117; border:1px dashed #1E2337; border-radius:10px;
                padding:24px; text-align:center; color:#334155; font-size:13px;">
        No agent events yet. Run the pipeline to see activity here.
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Agent Performance ─────────────────────────────────────────────────────────
st.markdown('<div class="tp-section-title">Agent Performance</div>', unsafe_allow_html=True)

try:
    import pandas as pd
    from monitoring.metrics import metrics
    agent_data = metrics.get_all()
    if agent_data:
        rows = [{
            "Agent": name,
            "Runs": m.runs,
            "Avg Latency": f"{m.avg_latency_ms:.0f} ms",
            "Error Rate": f"{m.error_rate:.0%}",
            "Health": "🟢 Healthy" if m.error_rate < 0.1 else "🔴 Issues"
        } for name, m in agent_data.items()]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.markdown("""
        <div style="color:#334155; font-size:13px; text-align:center; padding:16px;">
            Agent metrics will appear here after running the pipeline.
        </div>""", unsafe_allow_html=True)
except Exception:
    pass
