"""
Shared CSS design system for AI TestPilot X.
Import this in every page: from pages._css import inject_css
"""
import streamlit as st


DESIGN_CSS = """
<style>
/* ── Hide only hamburger-menu and footer, NOT the header/sidebar toggle ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Keep the sidebar collapse/expand button visible */
button[data-testid="collapsedControl"] {display: flex !important;}

/* ── Page layout ─────────────────────────────────────────── */
.block-container {
    padding-top: 1.8rem !important;
    padding-bottom: 2rem !important;
    max-width: 1200px;
}

/* ── Custom typography classes ───────────────────────────── */
.tp-page-title {
    font-size: 28px; font-weight: 800; color: #F0F4FF;
    margin: 0 0 4px 0; letter-spacing: -0.02em;
}
.tp-page-subtitle {
    font-size: 14px; color: #64748B; margin: 0 0 20px 0;
}
.tp-section-title {
    font-size: 11px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.1em; color: #64748B;
    margin: 24px 0 12px 0; padding-bottom: 6px;
    border-bottom: 1px solid #1E2337;
}

/* ── Card classes ────────────────────────────────────────── */
.tp-card {
    background: #0F1117; border: 1px solid #1E2337;
    border-radius: 12px; padding: 20px;
}
.tp-card-sm {
    background: #0F1117; border: 1px solid #1E2337;
    border-radius: 10px; padding: 14px 16px;
}

/* ── Metric cards ────────────────────────────────────────── */
div[data-testid="metric-container"] {
    background: #0F1117 !important;
    border: 1px solid #1E2337 !important;
    border-radius: 12px !important;
    padding: 18px 20px !important;
    transition: border-color 0.2s ease;
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

/* ── Sidebar ─────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: #080B12 !important;
    border-right: 1px solid #1E2337 !important;
}
section[data-testid="stSidebar"] > div:first-child {
    padding-top: 1rem !important;
}
/* Sidebar nav links */
section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] {
    background: transparent !important;
    border-radius: 8px !important;
    margin: 2px 8px !important;
    padding: 8px 12px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #94A3B8 !important;
    transition: background 0.15s, color 0.15s !important;
}
section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover {
    background: #1E2337 !important;
    color: #F0F4FF !important;
}
section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"] {
    background: #6C63FF22 !important;
    color: #a78bfa !important;
    border-left: 2px solid #6C63FF !important;
}

/* ── Buttons ─────────────────────────────────────────────── */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    transition: all 0.15s ease !important;
    border: none !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6C63FF 0%, #8B5CF6 100%) !important;
    color: white !important;
    box-shadow: 0 2px 12px rgba(108,99,255,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(108,99,255,0.5) !important;
}
.stButton > button[kind="secondary"] {
    background: #1E2337 !important;
    color: #CBD5E1 !important;
    border: 1px solid #2D3557 !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #252A45 !important;
    color: white !important;
}

/* ── Inputs ──────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
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
.stSelectbox > div > div {
    background: #0F1117 !important;
    border: 1px solid #1E2337 !important;
    border-radius: 8px !important;
}

/* ── Tabs ────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #1E2337 !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 0 !important;
    color: #64748B !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    padding: 10px 18px !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #a78bfa !important;
    border-bottom: 2px solid #6C63FF !important;
    background: transparent !important;
}

/* ── Expander ────────────────────────────────────────────── */
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

/* ── Dataframe ───────────────────────────────────────────── */
.stDataFrame { border-radius: 10px !important; overflow: hidden !important; }

/* ── Progress bar ────────────────────────────────────────── */
.stProgress > div > div {
    background: linear-gradient(90deg, #6C63FF, #8B5CF6) !important;
    border-radius: 4px !important;
}

/* ── Divider ─────────────────────────────────────────────── */
hr[data-testid="stDivider"] {
    border-color: #1E2337 !important;
    margin: 20px 0 !important;
}

/* ── Radio ───────────────────────────────────────────────── */
.stRadio label {
    cursor: pointer;
    font-size: 13px !important;
    transition: color 0.15s;
}

/* ── Download button ─────────────────────────────────────── */
.stDownloadButton > button {
    background: #1E2337 !important;
    border: 1px solid #2D3557 !important;
    border-radius: 8px !important;
    color: #CBD5E1 !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    transition: all 0.15s !important;
}
.stDownloadButton > button:hover {
    background: #252A45 !important;
    color: white !important;
}

/* ── Alert / Info boxes ──────────────────────────────────── */
.stAlert {
    border-radius: 10px !important;
    font-size: 13px !important;
}

/* ── Scrollbar ───────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #080B12; }
::-webkit-scrollbar-thumb { background: #2D3557; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #6C63FF77; }
</style>
"""


def inject_css():
    """Inject the shared design system CSS. Call at the top of every page."""
    st.markdown(DESIGN_CSS, unsafe_allow_html=True)


def sidebar_branding():
    """Inject sidebar logo/branding. Call once per page."""
    with st.sidebar:
        st.markdown("""
        <div style="padding: 4px 4px 16px 4px; text-align: center;">
            <div style="font-size: 32px; margin-bottom: 6px;">🧪</div>
            <div style="font-size: 16px; font-weight: 800; color: #6C63FF;
                        letter-spacing: -0.02em;">AI TestPilot X</div>
            <div style="font-size: 11px; color: #475569; margin-top: 2px;">
                Autonomous QA Platform
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.divider()
