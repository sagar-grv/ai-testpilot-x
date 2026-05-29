"""Page 06 — Reports & Analytics with Engineer/Executive view toggle."""
import streamlit as st
import json
import pandas as pd

st.set_page_config(page_title="Reports | AI TestPilot X", layout="wide")
st.title("Reports & Analytics")

# View toggle
view = st.radio("View", ["Executive", "Engineer"], horizontal=True)

# Load from session state or SQLite
report = st.session_state.get("report")
bugs = st.session_state.get("bugs", [])
execution = st.session_state.get("execution_results")

# Also try loading last report from DB
if not report:
    try:
        from storage.db import get_session
        from storage.models.reports import ReportRecord
        db = get_session()
        last = db.query(ReportRecord).order_by(ReportRecord.created_at.desc()).first()
        db.close()
        if last:
            report = json.loads(last.report_json)
    except Exception:
        pass

if not report:
    st.info("No reports yet. Run the full pipeline to generate a report.")
    st.stop()

# Ensure report is a dict
if hasattr(report, "model_dump"):
    report = report.model_dump()

# Release Decision Banner
decision = report.get("decision", "GO")
if decision == "NO_GO":
    st.error("🔴 RELEASE DECISION: NO GO")
elif decision == "GO_WITH_RISK":
    st.warning("🟡 RELEASE DECISION: GO WITH RISK")
else:
    st.success("🟢 RELEASE DECISION: GO")

st.caption(report.get("recommendation_text", ""))

if view == "Executive":
    # KPI cards
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Tests", report.get("total_tests", 0))
    col2.metric("Passed", report.get("passed", 0))
    col3.metric("Failed", report.get("failed", 0))
    col4.metric("Risk Score", f"{report.get('risk_score', 0):.0f}/100")
    col5.metric("Confidence", f"{report.get('confidence_score', 0):.0%}")

    # Pass/Fail donut
    try:
        import plotly.express as px
        passed = report.get("passed", 0)
        failed = report.get("failed", 0)
        if passed + failed > 0:
            fig = px.pie(names=["Passed", "Failed"], values=[passed, failed],
                         hole=0.5, color_discrete_sequence=["#00cc44", "#ff4444"],
                         title="Test Results")
            st.plotly_chart(fig, use_container_width=True)
    except Exception:
        pass

    # Bug severity
    try:
        import plotly.graph_objects as go
        severities = ["Critical", "High", "Medium", "Low"]
        counts = [report.get(f"{s.lower()}_bugs", 0) for s in severities]
        colors = ["#cc0000", "#ff6600", "#ffcc00", "#00cc44"]
        if sum(counts) > 0:
            fig2 = go.Figure(go.Bar(x=severities, y=counts, marker_color=colors))
            fig2.update_layout(title="Bug Severity Distribution", height=300)
            st.plotly_chart(fig2, use_container_width=True)
    except Exception:
        pass

else:  # Engineer view
    st.subheader("Test Results Detail")
    if execution:
        exec_data = execution if isinstance(execution, dict) else execution.model_dump()
        results = exec_data.get("results", [])
        if results:
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)

    if bugs:
        st.subheader("Bug List")
        bug_list = [b if isinstance(b, dict) else b.model_dump() for b in bugs]
        bdf = pd.DataFrame(bug_list)
        show_cols = [c for c in ["id", "title", "severity", "priority", "failure_signature"] if c in bdf.columns]
        if show_cols:
            st.dataframe(bdf[show_cols], use_container_width=True)

# Agent performance (both views)
st.divider()
st.subheader("Agent Performance")
try:
    from monitoring.metrics import metrics
    agent_data = metrics.get_all()
    if agent_data:
        rows = [{"Agent": name, "Runs": m.runs, "Avg Latency (ms)": f"{m.avg_latency_ms:.0f}", "Error Rate": f"{m.error_rate:.0%}"}
                for name, m in agent_data.items()]
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.info("No agent metrics yet. Run the pipeline first.")
except Exception:
    pass
