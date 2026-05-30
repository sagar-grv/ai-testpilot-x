"""app.py — AI TestPilot X main entry point."""
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

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Hide default Streamlit menu/footer */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Metric card style */
div[data-testid="metric-container"] {
    background: #1E2130;
    border: 1px solid #2E3250;
    border-radius: 12px;
    padding: 16px 20px;
}
div[data-testid="metric-container"] label {
    color: #A0AEC0 !important;
    font-size: 12px !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    font-size: 28px !important;
    font-weight: 700 !important;
    color: #FAFAFA !important;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background: #141625;
    border-right: 1px solid #2E3250;
}
section[data-testid="stSidebar"] .css-1d391kg {
    padding-top: 1rem;
}

/* Button styling */
.stButton > button {
    border-radius: 8px;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6C63FF 0%, #8B5CF6 100%);
    border: none;
    color: white;
}

/* Dataframe */
.dataframe { font-size: 13px; }

/* Code blocks */
.stCode { border-radius: 8px; }

/* Expander */
details { border-radius: 8px !important; border: 1px solid #2E3250 !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 8px 0 16px 0;'>
        <div style='font-size:32px;'>🧪</div>
        <div style='font-size:18px; font-weight:700; color:#6C63FF;'>AI TestPilot X</div>
        <div style='font-size:11px; color:#718096; margin-top:4px;'>Autonomous QA Platform</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.markdown("**Navigation**")
    st.markdown("""
    <style>
    .nav-item { padding: 6px 0; font-size: 13px; color: #A0AEC0; }
    </style>
    <div class='nav-item'>📊 Home — System Overview</div>
    <div class='nav-item'>🤖 AI Test Generator</div>
    <div class='nav-item'>⚙️ Selenium Generator</div>
    <div class='nav-item'>🌐 API Tester</div>
    <div class='nav-item'>🐛 Bug Analyzer</div>
    <div class='nav-item'>📈 Reports & Analytics</div>
    <div class='nav-item'>🔀 Workflow Studio</div>
    <div class='nav-item'>📚 Knowledge Base</div>
    """, unsafe_allow_html=True)
    st.divider()
    st.caption("v1.0.0 · Gemini 2.5 Flash")

# ── Main content ──────────────────────────────────────────────────────────────
st.markdown("""
<div style='padding: 24px 0 8px 0;'>
    <h1 style='font-size:36px; font-weight:800; margin:0;'>
        🧪 AI TestPilot X
    </h1>
    <p style='color:#718096; font-size:16px; margin-top:6px;'>
        Autonomous AI-Powered Quality Engineering Platform
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Platform Status", "✅ Ready")
col2.metric("AI Agents", "9 Active")
col3.metric("Execution Mode", "MOCK")
col4.metric("LLM", "Gemini 2.5")

st.divider()
st.info("👈 **Use the sidebar** to navigate between modules. Start with **AI Test Generator** to generate your first test suite from a user story.")
