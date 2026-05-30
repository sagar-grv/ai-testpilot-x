"""Page 05 — Bug Analyzer: analyze failures with AI + RAG."""
import streamlit as st

st.set_page_config(page_title="Bug Analyzer | AI TestPilot X", page_icon="🐛", layout="wide")

st.markdown("""
<h2 style='margin:0; font-size:26px; font-weight:700;'>🐛 Bug Analyzer</h2>
<p style='color:#718096; margin-top:4px;'>Paste a stack trace or error log — AI identifies root cause, severity, and fix suggestion using RAG.</p>
""", unsafe_allow_html=True)
st.divider()

# Input tabs
tab1, tab2, tab3 = st.tabs(["Paste Log", "Upload File", "From Last Run"])

log_text = ""
with tab1:
    log_text = st.text_area("Paste error log or stack trace", height=150, key="paste_log")

with tab2:
    uploaded = st.file_uploader("Upload log file", type=["txt", "log"])
    if uploaded:
        log_text = uploaded.read().decode("utf-8", errors="ignore")

with tab3:
    exec_results = st.session_state.get("execution_results")
    if exec_results:
        failed = [r for r in exec_results.results if r.status in ("FAIL", "ERROR")]
        if failed:
            sel_fail = st.selectbox("Select failed test", [r.tc_id for r in failed])
            sel = next(r for r in failed if r.tc_id == sel_fail)
            log_text = sel.error_message
            st.code(log_text)
        else:
            st.info("No failed tests in last run")
    else:
        st.info("No execution results. Run tests on Selenium Generator first.")

# Analyze
if st.button("Analyze Bug", type="primary", disabled=not log_text.strip()):
    with st.spinner("AI analyzing failure..."):
        try:
            from agents.bug_agent import BugAgent
            session_id = st.session_state.get("session_id", "demo")
            agent = BugAgent()
            bug = agent.analyze_single(log_text, session_id=session_id)
            st.session_state["current_bug"] = bug
        except Exception as e:
            st.error(f"Analysis failed: {e}")

# Display bug report
bug = st.session_state.get("current_bug")
if bug:
    severity_icons = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}
    icon = severity_icons.get(bug.severity, "⚪")

    # KPI cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Severity", f"{icon} {bug.severity}")
    col2.metric("Priority", bug.priority)
    col3.metric("Root Cause Conf.", f"{bug.root_cause_confidence:.0%}")
    col4.metric("Fix Confidence", f"{bug.fix_confidence:.0%}")

    # Failure signature
    st.subheader("Failure Signature")
    st.code(bug.failure_signature)

    # Root cause + fix
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("Root Cause")
        st.write(bug.root_cause)
        st.progress(bug.root_cause_confidence, text=f"Confidence: {bug.root_cause_confidence:.0%}")
    with col_r:
        st.subheader("Fix Suggestion")
        st.write(bug.fix_suggestion)
        st.progress(bug.fix_confidence, text=f"Confidence: {bug.fix_confidence:.0%}")

    # RAG matches
    if bug.rag_matches:
        st.subheader("Similar Past Bugs (RAG)")
        for match in bug.rag_matches[:5]:
            similarity = 1.0 - float(match.get("distance", 0.5))
            with st.expander(f"{match.get('id', 'unknown')} — Similarity: {similarity:.0%}"):
                st.write(match.get("text", "")[:200])
                if match.get("metadata"):
                    st.json(match["metadata"])

    # Actions
    st.divider()
    col_h, col_e = st.columns(2)
    if col_h.button("Send to Healing Agent"):
        st.session_state["healing_bug"] = bug
        st.success("Bug sent to Healing Agent. Navigate to Selenium Generator.")
    if col_e.button("Export Bug Report"):
        report_md = f"""# Bug Report

**ID:** {bug.id}
**Severity:** {bug.severity}
**Priority:** {bug.priority}

## Failure Signature
`{bug.failure_signature}`

## Root Cause
{bug.root_cause}
*Confidence: {bug.root_cause_confidence:.0%}*

## Fix Suggestion
{bug.fix_suggestion}
*Confidence: {bug.fix_confidence:.0%}*
"""
        st.download_button("Download bug_report.md", report_md, "bug_report.md", "text/markdown")
