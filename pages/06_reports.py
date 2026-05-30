"""Page 06 — Reports & Analytics."""
import streamlit as st
import json
import pandas as pd

st.set_page_config(page_title="Reports | AI TestPilot X", page_icon="📈", layout="wide")

st.markdown("""
<h2 style='margin:0; font-size:26px; font-weight:700;'>📈 Reports & Analytics</h2>
<p style='color:#718096; margin-top:4px;'>Executive summaries, bug analysis, and release decisions.</p>
""", unsafe_allow_html=True)
st.divider()

view = st.radio("View Mode", ["🏢 Executive", "🔧 Engineer"], horizontal=True)

# Load report
report = st.session_state.get("report")
bugs = st.session_state.get("bugs", [])
execution = st.session_state.get("execution_results")

if not report:
    try:
        from storage.db import get_session
        from storage.models.reports import ReportRecord
        db = get_session()
        last = db.query(ReportRecord).order_by(ReportRecord.created_at.desc()).first()
        db.close()
        if last:
            report = json.loads(last.report_json or "{}")
    except Exception:
        pass

if not report:
    st.markdown("""
    <div style='background:#1E2130; border:1px solid #2E3250; border-radius:12px;
         padding:48px; text-align:center;'>
        <div style='font-size:48px;'>📊</div>
        <div style='font-size:20px; font-weight:600; margin-top:16px;'>No reports generated yet</div>
        <div style='color:#718096; margin-top:8px;'>
            Complete a full pipeline run on <strong>AI Test Generator</strong> to see reports here.
        </div>
    </div>""", unsafe_allow_html=True)
    st.stop()

if hasattr(report, "model_dump"):
    rdata = report.model_dump()
else:
    rdata = report if isinstance(report, dict) else {}

decision = rdata.get("decision", "GO")

# ── Release Decision Banner ───────────────────────────────────────────────────
DECISION_STYLES = {
    "NO_GO": ("🚫", "NO GO", "linear-gradient(135deg,#742A2A,#C53030)", "#FEB2B2", "Critical defects block release."),
    "GO_WITH_RISK": ("⚠️", "GO WITH RISK", "linear-gradient(135deg,#744210,#C05621)", "#FBD38D", "High severity issues present. Proceed with caution."),
    "GO": ("✅", "GO", "linear-gradient(135deg,#1A4731,#276749)", "#9AE6B4", "All quality gates passed. Release approved."),
}
icon, label, bg, text_color, subtitle = DECISION_STYLES.get(decision, DECISION_STYLES["GO"])

st.markdown(f"""
<div style='background:{bg}; border-radius:14px; padding:24px 32px; margin-bottom:24px;'>
    <div style='display:flex; align-items:center; gap:16px;'>
        <span style='font-size:48px;'>{icon}</span>
        <div>
            <div style='font-size:13px; color:{text_color}; opacity:0.8; text-transform:uppercase; letter-spacing:0.1em;'>
                RELEASE DECISION
            </div>
            <div style='font-size:32px; font-weight:800; color:white;'>{label}</div>
            <div style='color:{text_color}; margin-top:4px; font-size:14px;'>{subtitle}</div>
        </div>
    </div>
    {f"<div style='margin-top:12px; background:rgba(0,0,0,0.2); border-radius:8px; padding:10px 16px; color:{text_color}; font-size:13px; font-style:italic;'>{rdata.get('recommendation_text','')}</div>" if rdata.get('recommendation_text') else ""}
</div>""", unsafe_allow_html=True)

# ── KPI Cards ─────────────────────────────────────────────────────────────────
kc1, kc2, kc3, kc4, kc5 = st.columns(5)
kc1.metric("📋 Total Tests", rdata.get("total_tests", 0))
kc2.metric("✅ Passed", rdata.get("passed", 0))
kc3.metric("❌ Failed", rdata.get("failed", 0))
total_bugs = sum([rdata.get(k, 0) for k in ["critical_bugs","high_bugs","medium_bugs","low_bugs"]])
kc4.metric("🐛 Total Bugs", total_bugs)
kc5.metric("⚡ Risk Score", f"{rdata.get('risk_score', 0):.0f}/100")

st.divider()

if view == "🏢 Executive":
    # ── Charts ────────────────────────────────────────────────────────────────
    try:
        import plotly.express as px
        import plotly.graph_objects as go

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown("**Test Results Distribution**")
            passed = rdata.get("passed", 0)
            failed = rdata.get("failed", 0)
            if passed + failed > 0:
                fig1 = go.Figure(go.Pie(
                    labels=["Passed", "Failed"],
                    values=[passed, failed],
                    hole=0.55,
                    marker=dict(colors=["#48BB78", "#FC8181"]),
                    textinfo="label+percent",
                    textfont=dict(color="white", size=13),
                ))
                fig1.update_layout(
                    paper_bgcolor="#0E1117", plot_bgcolor="#0E1117",
                    font=dict(color="#FAFAFA"),
                    showlegend=False, height=280,
                    margin=dict(l=20, r=20, t=20, b=20),
                    annotations=[dict(text=f"<b>{passed+failed}</b><br>Tests",
                                      x=0.5, y=0.5, font_size=14, showarrow=False,
                                      font=dict(color="#FAFAFA"))]
                )
                st.plotly_chart(fig1, use_container_width=True)

        with chart_col2:
            st.markdown("**Bug Severity Breakdown**")
            severities = ["Critical", "High", "Medium", "Low"]
            counts = [rdata.get(f"{s.lower()}_bugs", 0) for s in severities]
            colors = ["#FC8181", "#F6AD55", "#ECC94B", "#68D391"]
            if sum(counts) > 0:
                fig2 = go.Figure(go.Bar(
                    x=severities, y=counts,
                    marker_color=colors,
                    text=counts, textposition="outside",
                    textfont=dict(color="white"),
                ))
                fig2.update_layout(
                    paper_bgcolor="#0E1117", plot_bgcolor="#1E2130",
                    font=dict(color="#FAFAFA"),
                    xaxis=dict(gridcolor="#2E3250"),
                    yaxis=dict(gridcolor="#2E3250"),
                    height=280, margin=dict(l=20, r=20, t=20, b=20),
                    showlegend=False
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("✅ No bugs found!")
    except Exception:
        pass

    # ── Bug severity summary table ────────────────────────────────────────────
    if bugs:
        st.markdown("**Bug Summary**")
        bug_rows = []
        for b in (bugs if isinstance(bugs[0], dict) else [bx.model_dump() for bx in bugs]):
            SEV_ICONS = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}
            bug_rows.append({
                "Severity": f"{SEV_ICONS.get(b.get('severity',''),'⚪')} {b.get('severity','')}",
                "Priority": b.get("priority", ""),
                "Title": b.get("title", "")[:60],
                "Fix Confidence": f"{b.get('fix_confidence', 0):.0%}",
            })
        st.dataframe(pd.DataFrame(bug_rows), use_container_width=True, hide_index=True)

else:
    # ── Engineer View ─────────────────────────────────────────────────────────
    st.markdown("### 🔍 Test Results Detail")
    if execution:
        exec_data = execution if isinstance(execution, dict) else execution.model_dump()
        results = exec_data.get("results", [])
        if results:
            STATUS_ICONS = {"PASS": "✅", "FAIL": "❌", "ERROR": "⚠️", "SKIP": "⏭"}
            rows = [{
                "Status": f"{STATUS_ICONS.get(r.get('status',''), '❓')} {r.get('status','')}",
                "Test ID": r.get("tc_id", ""),
                "Duration": f"{r.get('duration_ms', 0):.0f}ms",
                "Error": (r.get("error_message", "") or "—")[:80],
            } for r in results]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown("### 🐛 Bug Details")
    if bugs:
        bug_list = bugs if isinstance(bugs[0], dict) else [b.model_dump() for b in bugs]
        for i, b in enumerate(bug_list):
            SEV_COLORS = {"Critical": "#FC8181", "High": "#F6AD55", "Medium": "#ECC94B", "Low": "#68D391"}
            sev = b.get("severity", "Medium")
            sc = SEV_COLORS.get(sev, "#A0AEC0")
            with st.expander(f"🐛 {b.get('id','')} — {b.get('title','')[:60]}"):
                dc1, dc2 = st.columns(2)
                dc1.markdown(f"**Severity:** <span style='color:{sc};'>{sev}</span>", unsafe_allow_html=True)
                dc2.markdown(f"**Priority:** {b.get('priority','')}")
                st.markdown(f"**Root Cause:** {b.get('root_cause','')}")
                st.markdown(f"**Fix Suggestion:** {b.get('fix_suggestion','')}")
                conf_col1, conf_col2, conf_col3 = st.columns(3)
                conf_col1.progress(b.get("root_cause_confidence", 0), text=f"Root Cause: {b.get('root_cause_confidence',0):.0%}")
                conf_col2.progress(b.get("fix_confidence", 0), text=f"Fix: {b.get('fix_confidence',0):.0%}")
                conf_col3.progress(b.get("severity_confidence", 0), text=f"Severity: {b.get('severity_confidence',0):.0%}")
    else:
        st.success("✅ No bugs found in last run.")

    st.markdown("### 📊 Agent Performance")
    try:
        from monitoring.metrics import metrics
        agent_data = metrics.get_all()
        if agent_data:
            rows = [{"Agent": n, "Runs": m.runs, "Avg Latency": f"{m.avg_latency_ms:.0f}ms",
                     "Error Rate": f"{m.error_rate:.0%}", "Status": "🟢 OK" if m.error_rate < 0.1 else "🔴 Issues"}
                    for n, m in agent_data.items()]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.caption("No agent metrics yet.")
    except Exception:
        pass
