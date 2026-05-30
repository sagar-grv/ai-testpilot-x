"""AI TestPilot X — Main entry point."""
import streamlit as st
from monitoring.tracing import configure_tracing
from storage.db import get_engine

configure_tracing()
get_engine()

st.set_page_config(
    page_title="AI TestPilot X",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject shared CSS + sidebar ───────────────────────────────────────────────
from pages._css import inject_css, sidebar_branding
inject_css()
sidebar_branding()

# ── Sidebar bottom status ─────────────────────────────────────────────────────
with st.sidebar:
    from config import settings
    mode_colors = {"MOCK": "#3B82F6", "LOCAL": "#22C55E", "GRID": "#A855F7"}
    mc = mode_colors.get(settings.EXECUTION_MODE, "#64748B")
    st.markdown(f"""
    <div style="padding:8px 4px 4px 4px; font-size:12px; color:#64748B;">
        <span style="background:{mc}22; color:{mc}; border:1px solid {mc}44;
            border-radius:5px; padding:3px 8px; font-weight:700; font-size:11px;">
            {settings.EXECUTION_MODE}
        </span>
        &nbsp;mode &nbsp;·&nbsp; v1.0.0
    </div>
    """, unsafe_allow_html=True)

# ── Landing page ──────────────────────────────────────────────────────────────
from config import settings as cfg

st.markdown("""
<div style="padding:20px 0 8px 0;">
    <div style="display:flex; align-items:center; gap:16px; margin-bottom:8px;">
        <span style="font-size:48px;">🧪</span>
        <div>
            <h1 style="font-size:36px; font-weight:900; margin:0;
                       color:#F0F4FF; letter-spacing:-0.03em;">
                AI TestPilot X
            </h1>
            <p style="font-size:15px; color:#64748B; margin:4px 0 0 0;">
                Autonomous AI-Powered Quality Engineering Platform
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Status pills row ──────────────────────────────────────────────────────────
gemini_ok = bool(cfg.GEMINI_API_KEY and cfg.GEMINI_API_KEY.startswith("AIzaSy"))
st.markdown(f"""
<div style="display:flex; gap:8px; margin-bottom:20px; flex-wrap:wrap; align-items:center;">
    <span style="background:{'#16a34a22' if gemini_ok else '#dc262622'};
        color:{'#4ade80' if gemini_ok else '#f87171'};
        border:1px solid {'#16a34a44' if gemini_ok else '#dc262644'};
        border-radius:20px; padding:4px 14px; font-size:12px; font-weight:600;">
        {'✓ Gemini Connected' if gemini_ok else '✗ Invalid API Key'}
    </span>
    <span style="background:#6C63FF22; color:#a78bfa; border:1px solid #6C63FF44;
        border-radius:20px; padding:4px 14px; font-size:12px; font-weight:600;">
        9 AI Agents
    </span>
    <span style="background:#0ea5e922; color:#38bdf8; border:1px solid #0ea5e944;
        border-radius:20px; padding:4px 14px; font-size:12px; font-weight:600;">
        LangGraph Orchestrated
    </span>
    <span style="background:#f59e0b22; color:#fbbf24; border:1px solid #f59e0b44;
        border-radius:20px; padding:4px 14px; font-size:12px; font-weight:600;">
        RAG-Powered
    </span>
    <a href="https://ai-testpilot-x.streamlit.app/" target="_blank"
       style="background:#FF4B4B22; color:#ff6b6b; border:1px solid #FF4B4B55;
        border-radius:20px; padding:4px 14px; font-size:12px; font-weight:600;
        text-decoration:none; display:inline-flex; align-items:center; gap:5px;">
        🚀 Live Demo
    </a>
</div>
""", unsafe_allow_html=True)

# ── KPI cards ─────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("AI Agents", "9", help="RequirementAgent · TestCaseAgent · VerificationAgent · SeleniumAgent · APIAgent · ExecutionAgent · BugAgent · HealingAgent · ReportAgent")
c2.metric("Execution Mode", cfg.EXECUTION_MODE, help="MOCK = simulated results · LOCAL = real Chrome · GRID = Selenium Grid")
c3.metric("LLM", "Gemini 2.5 Flash", help="Google Gemini 2.5 Flash via google-generativeai SDK")
c4.metric("Vector DB", "ChromaDB", help="sentence-transformers all-MiniLM-L6-v2 · 4 collections")

st.divider()

# ── Quick-start guide ─────────────────────────────────────────────────────────
st.markdown('<div class="tp-section-title">How It Works</div>', unsafe_allow_html=True)

qs1, qs2, qs3, qs4 = st.columns(4)

def _step_card(col, num, icon, title, desc):
    col.markdown(f"""
    <div style="background:#0F1117; border:1px solid #1E2337; border-radius:12px;
                padding:20px 18px; position:relative; overflow:hidden; min-height:155px;">
        <div style="position:absolute; top:12px; right:14px; font-size:10px;
                    font-weight:800; color:#2D3557; letter-spacing:0.05em;">STEP {num}</div>
        <div style="font-size:28px; margin-bottom:10px;">{icon}</div>
        <div style="font-weight:700; font-size:14px; color:#F0F4FF; margin-bottom:6px;">
            {title}</div>
        <div style="font-size:12px; color:#64748B; line-height:1.6;">{desc}</div>
    </div>""", unsafe_allow_html=True)

_step_card(qs1, 1, "📝", "Write User Story",
    "Go to AI Test Generator and describe your feature in plain English.")
_step_card(qs2, 2, "🤖", "Generate Tests",
    "AI analyzes requirements and generates test cases with a live coverage radar.")
_step_card(qs3, 3, "⚙️", "Run & Analyze",
    "Generate Selenium scripts, execute with HITL gate, and auto-analyze failures.")
_step_card(qs4, 4, "📊", "View Reports",
    "See GO / GO WITH RISK / NO GO release decision with full bug analysis.")

st.divider()

# ── Live app CTA ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#1e1b4b,#2e1065);
            border:1px solid #6C63FF44; border-radius:14px;
            padding:24px 28px; text-align:center; margin-bottom:8px;">
    <div style="font-size:20px; font-weight:800; color:#F0F4FF; margin-bottom:6px;">
        Try the Live Demo
    </div>
    <div style="font-size:13px; color:#94A3B8; margin-bottom:16px;">
        Deployed on Streamlit Cloud — no setup required
    </div>
    <a href="https://ai-testpilot-x.streamlit.app/" target="_blank"
       style="display:inline-block; background:linear-gradient(135deg,#FF4B4B,#e03232);
              color:white; font-weight:700; font-size:14px; padding:10px 28px;
              border-radius:8px; text-decoration:none; letter-spacing:0.02em;">
        🚀 &nbsp; Open ai-testpilot-x.streamlit.app
    </a>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; padding:6px; color:#334155; font-size:12px;">
    👈 Use the <strong style="color:#6C63FF;">sidebar</strong> to navigate between modules
</div>
""", unsafe_allow_html=True)
