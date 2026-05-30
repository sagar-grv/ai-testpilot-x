"""AI TestPilot X — Main entry point with global CSS design system."""
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

# ─── Global Design System CSS ──────────────────────────────────────────────────
GLOBAL_CSS = """
<style>
/* ── Reset & Base ─────────────────────────────────────────── */
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding-top: 1.5rem; padding-bottom: 2rem;}

/* ── Typography ───────────────────────────────────────────── */
.tp-page-title {
    font-size: 28px; font-weight: 800; color: #F0F4FF;
    margin: 0 0 4px 0; letter-spacing: -0.02em;
}
.tp-page-subtitle {
    font-size: 14px; color: #64748B; margin: 0 0 20px 0;
}
.tp-section-title {
    font-size: 13px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.08em; color: #94A3B8; margin: 24px 0 12px 0;
}

/* ── Cards ────────────────────────────────────────────────── */
.tp-card {
    background: #0F1117;
    border: 1px solid #1E2337;
    border-radius: 12px;
    padding: 20px;
}
.tp-card-sm {
    background: #0F1117;
    border: 1px solid #1E2337;
    border-radius: 10px;
    padding: 14px 16px;
}

/* ── Metric cards ─────────────────────────────────────────── */
div[data-testid="metric-container"] {
    background: #0F1117 !important;
    border: 1px solid #1E2337 !important;
    border-radius: 12px !important;
    padding: 18px 20px !important;
    transition: border-color 0.2s;
}
div[data-testid="metric-container"]:hover {
    border-color: #6C63FF55 !important;
}
div[data-testid="metric-container"] [data-testid="stMetricLabel"] p {
    font-size: 11px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    color: #64748B !important;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 26px !important;
    font-weight: 800 !important;
    color: #F0F4FF !important;
}

/* ── Buttons ──────────────────────────────────────────────── */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    letter-spacing: 0.01em !important;
    transition: all 0.15s ease !important;
    border: none !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6C63FF 0%, #8B5CF6 100%) !important;
    color: white !important;
    box-shadow: 0 2px 12px rgba(108,99,255,0.35) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 18px rgba(108,99,255,0.5) !important;
}
.stButton > button[kind="secondary"] {
    background: #1E2337 !important;
    color: #CBD5E1 !important;
    border: 1px solid #2D3557 !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #252A45 !important;
    border-color: #6C63FF88 !important;
    color: white !important;
}

/* ── Inputs ───────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div {
    background: #0F1117 !important;
    border: 1px solid #1E2337 !important;
    border-radius: 8px !important;
    color: #F0F4FF !important;
    font-size: 13px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #6C63FF !important;
    box-shadow: 0 0 0 3px rgba(108,99,255,0.15) !important;
}

/* ── Dataframe / Table ────────────────────────────────────── */
.stDataFrame { border-radius: 10px !important; overflow: hidden !important; }
.stDataFrame th { background: #0F1117 !important; color: #94A3B8 !important;
    font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.06em; }
.stDataFrame td { color: #CBD5E1 !important; font-size: 13px !important; }

/* ── Sidebar ──────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: #080B12 !important;
    border-right: 1px solid #1E2337 !important;
}
section[data-testid="stSidebar"] .stPageLink {
    border-radius: 8px; margin: 2px 0;
}

/* ── Tabs ─────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #1E2337 !important;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px 8px 0 0 !important;
    color: #64748B !important;
    font-weight: 500 !important;
    padding: 8px 16px !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    color: #6C63FF !important;
    border-bottom: 2px solid #6C63FF !important;
}

/* ── Expander ─────────────────────────────────────────────── */
details[data-testid="stExpander"] {
    background: #0F1117 !important;
    border: 1px solid #1E2337 !important;
    border-radius: 10px !important;
    margin-bottom: 6px !important;
}
details[data-testid="stExpander"] summary {
    font-weight: 500 !important;
    font-size: 13px !important;
    color: #CBD5E1 !important;
    padding: 12px 16px !important;
}

/* ── Alert boxes ──────────────────────────────────────────── */
.stAlert { border-radius: 10px !important; font-size: 13px !important; }
div[data-testid="stNotification"] { border-radius: 10px !important; }

/* ── Progress bar ─────────────────────────────────────────── */
.stProgress > div > div {
    background: linear-gradient(90deg, #6C63FF, #8B5CF6) !important;
    border-radius: 4px !important;
}

/* ── Divider ──────────────────────────────────────────────── */
hr[data-testid="stDivider"] {
    border-color: #1E2337 !important;
    margin: 20px 0 !important;
}

/* ── Code block ───────────────────────────────────────────── */
.stCode, pre { border-radius: 8px !important; }

/* ── Spinner ──────────────────────────────────────────────── */
.stSpinner { color: #6C63FF !important; }

/* ── Radio buttons ────────────────────────────────────────── */
.stRadio > div { gap: 8px !important; }
.stRadio label {
    background: #0F1117;
    border: 1px solid #1E2337;
    border-radius: 8px;
    padding: 8px 14px !important;
    cursor: pointer;
    transition: all 0.15s;
    font-size: 13px !important;
}
.stRadio label:has(input:checked) {
    border-color: #6C63FF !important;
    background: rgba(108,99,255,0.1) !important;
    color: #6C63FF !important;
}

/* ── Download button ──────────────────────────────────────── */
.stDownloadButton > button {
    background: #1E2337 !important;
    border: 1px solid #2D3557 !important;
    border-radius: 8px !important;
    color: #CBD5E1 !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}
.stDownloadButton > button:hover {
    background: #252A45 !important;
    border-color: #6C63FF88 !important;
    color: white !important;
}

/* ── Spinner overlay ──────────────────────────────────────── */
.stSpinner > div > div { border-top-color: #6C63FF !important; }

/* ── Scrollbar ────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #080B12; }
::-webkit-scrollbar-thumb { background: #1E2337; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #6C63FF55; }
</style>
"""

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ─── Sidebar branding ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 12px 4px 20px 4px; text-align: center;">
        <div style="font-size: 36px; margin-bottom: 6px;">🧪</div>
        <div style="font-size: 17px; font-weight: 800; color: #6C63FF;
                    letter-spacing: -0.02em;">AI TestPilot X</div>
        <div style="font-size: 11px; color: #475569; margin-top: 3px;">
            Autonomous QA Platform
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Navigation labels
    st.markdown("""
    <div style="font-size: 10px; font-weight: 700; text-transform: uppercase;
                letter-spacing: 0.1em; color: #475569; padding: 0 4px 8px 4px;">
        Navigation
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    from config import settings
    mode_colors = {"MOCK": "#3B82F6", "LOCAL": "#22C55E", "GRID": "#A855F7"}
    mc = mode_colors.get(settings.EXECUTION_MODE, "#64748B")
    st.markdown(f"""
    <div style="padding: 8px 4px; font-size: 12px; color: #64748B;">
        <span style="background: {mc}22; color: {mc}; border: 1px solid {mc}44;
            border-radius: 5px; padding: 3px 8px; font-weight: 700; font-size: 11px;">
            {settings.EXECUTION_MODE}
        </span>
        &nbsp; mode &nbsp;·&nbsp; v1.0.0
    </div>
    """, unsafe_allow_html=True)

# ─── Landing page ──────────────────────────────────────────────────────────────
from config import settings as cfg

st.markdown("""
<div style="padding: 32px 0 8px 0;">
    <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 8px;">
        <span style="font-size: 48px;">🧪</span>
        <div>
            <h1 style="font-size: 38px; font-weight: 900; margin: 0;
                       color: #F0F4FF; letter-spacing: -0.03em;">
                AI TestPilot X
            </h1>
            <p style="font-size: 16px; color: #64748B; margin: 4px 0 0 0;">
                Autonomous AI-Powered Quality Engineering Platform
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Status row
gemini_ok = bool(cfg.GEMINI_API_KEY and cfg.GEMINI_API_KEY.startswith("AIzaSy"))
st.markdown(f"""
<div style="display: flex; gap: 10px; margin-bottom: 28px; flex-wrap: wrap;">
    <span style="background: {'#16a34a22' if gemini_ok else '#dc262622'};
        color: {'#4ade80' if gemini_ok else '#f87171'};
        border: 1px solid {'#16a34a44' if gemini_ok else '#dc262644'};
        border-radius: 20px; padding: 4px 14px; font-size: 12px; font-weight: 600;">
        {'✓ Gemini Connected' if gemini_ok else '✗ Invalid API Key'}
    </span>
    <span style="background: #6C63FF22; color: #a78bfa; border: 1px solid #6C63FF44;
        border-radius: 20px; padding: 4px 14px; font-size: 12px; font-weight: 600;">
        9 AI Agents Active
    </span>
    <span style="background: #0ea5e922; color: #38bdf8; border: 1px solid #0ea5e944;
        border-radius: 20px; padding: 4px 14px; font-size: 12px; font-weight: 600;">
        LangGraph Orchestrated
    </span>
    <span style="background: #f59e0b22; color: #fbbf24; border: 1px solid #f59e0b44;
        border-radius: 20px; padding: 4px 14px; font-size: 12px; font-weight: 600;">
        RAG-Powered
    </span>
</div>
""", unsafe_allow_html=True)

# KPI cards
c1, c2, c3, c4 = st.columns(4)
c1.metric("AI Agents", "9", help="RequirementAgent, TestCaseAgent, VerificationAgent, SeleniumAgent, APIAgent, ExecutionAgent, BugAgent, HealingAgent, ReportAgent")
c2.metric("Execution Mode", cfg.EXECUTION_MODE, help="LOCAL = real Chrome | MOCK = simulated | GRID = Selenium Grid")
c3.metric("LLM", "Gemini 2.5 Flash", help="Google Gemini 2.5 Flash via google-generativeai SDK")
c4.metric("Vector DB", "ChromaDB", help="sentence-transformers all-MiniLM-L6-v2 embeddings, 4 collections")

st.divider()

# Quick start guide
st.markdown("""
<div style="font-size: 13px; font-weight: 700; text-transform: uppercase;
            letter-spacing: 0.08em; color: #475569; margin-bottom: 14px;">
    Quick Start
</div>
""", unsafe_allow_html=True)

qs1, qs2, qs3, qs4 = st.columns(4)

def qs_card(col, step, icon, title, desc, page):
    col.markdown(f"""
    <div style="background: #0F1117; border: 1px solid #1E2337; border-radius: 12px;
                padding: 20px; height: 160px; position: relative; overflow: hidden;">
        <div style="position: absolute; top: 14px; right: 16px; font-size: 10px;
                    font-weight: 800; color: #1E2337;">STEP {step}</div>
        <div style="font-size: 28px; margin-bottom: 10px;">{icon}</div>
        <div style="font-weight: 700; font-size: 14px; color: #F0F4FF;
                    margin-bottom: 6px;">{title}</div>
        <div style="font-size: 12px; color: #64748B; line-height: 1.5;">{desc}</div>
    </div>
    """, unsafe_allow_html=True)

qs_card(qs1, 1, "📝", "Write User Story", "Navigate to AI Test Generator and describe your feature in plain English.", "02_test_generator")
qs_card(qs2, 2, "🤖", "Generate Tests", "AI analyzes requirements and generates comprehensive test cases automatically.", "02_test_generator")
qs_card(qs3, 3, "⚙️", "Run Selenium", "Generate Selenium scripts and execute with HITL approval gate.", "03_selenium_generator")
qs_card(qs4, 4, "📊", "View Reports", "See the GO / GO WITH RISK / NO GO release decision and bug analysis.", "06_reports")

st.divider()

st.markdown("""
<div style="text-align: center; padding: 8px; color: #334155; font-size: 12px;">
    Use the <strong style="color: #6C63FF;">sidebar</strong> to navigate between modules
    &nbsp;·&nbsp; Start with <strong style="color: #6C63FF;">AI Test Generator</strong>
</div>
""", unsafe_allow_html=True)
