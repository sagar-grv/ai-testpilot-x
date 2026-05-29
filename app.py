"""AI TestPilot X — Streamlit entry point."""
import streamlit as st
from monitoring.tracing import configure_tracing
from storage.db import get_engine

configure_tracing()
get_engine()

st.set_page_config(page_title="AI TestPilot X", page_icon="🧪", layout="wide", initial_sidebar_state="expanded")
st.title("AI TestPilot X")
st.markdown("**Autonomous AI-powered quality engineering platform.** Use the sidebar to navigate.")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Status", "Ready")
col2.metric("Agents", "9")
col3.metric("Test Cases", "—")
col4.metric("Bugs Found", "—")
