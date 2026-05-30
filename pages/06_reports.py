"""Page 06 — Reports & Analytics."""

import streamlit as st
import json
import pandas as pd

st.set_page_config(page_title="Reports | AI TestPilot X", page_icon="📈", layout="wide")

# ── Inject shared CSS + sidebar ───────────────────────────────────────────────
from pages._css import inject_css, sidebar_branding

inject_css()
sidebar_branding()


st.markdown(
    """
<h1 class="tp-page-title">📈 Reports & Analytics</h1>
<p class="tp-page-subtitle">Executive summaries, bug analysis, and GO / NO GO release decisions.</p>
""",
    unsafe_allow_html=True,
)
st.divider()

# ── View toggle ───────────────────────────────────────────────────────────────
view = st.radio(
    "View",
    ["🏢 Executive", "🔧 Engineer"],
    horizontal=True,
    label_visibility="collapsed",
)
st.markdown("<br>", unsafe_allow_html=True)

# ── Load report ───────────────────────────────────────────────────────────────
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
    rdata = (
        session_report
        if isinstance(session_report, dict)
        else session_report.model_dump()
    )

bugs = st.session_state.get("bugs", [])
execution = st.session_state.get("execution_results")

if not rdata:
    st.markdown(
        """
    <div style="background:#0F1117; border:1px dashed #1E2337; border-radius:14px;
                padding:56px 32px; text-align:center;">
        <div style="font-size:52px; margin-bottom:14px;">📊</div>
        <div style="font-size:20px; font-weight:700; color:#F0F4FF; margin-bottom:8px;">
            No reports generated yet</div>
        <div style="font-size:13px; color:#475569; max-width:400px; margin:0 auto;">
            Complete a full pipeline run on
            <strong style="color:#6C63FF;">AI Test Generator</strong>
            to generate your first report here.
        </div>
    </div>""",
        unsafe_allow_html=True,
    )
    st.stop()

decision = rdata.get("decision", "GO")

# ── Release Decision Banner ───────────────────────────────────────────────────
BANNERS = {
    "NO_GO": (
        "#7f1d1d",
        "#ef4444",
        "#fca5a5",
        "🚫",
        "NO GO",
        "Critical defects detected. Release is blocked.",
    ),
    "GO_WITH_RISK": (
        "#78350f",
        "#f59e0b",
        "#fde68a",
        "⚠️",
        "GO WITH RISK",
        "High severity issues present. Proceed with caution.",
    ),
    "GO": (
        "#14532d",
        "#22c55e",
        "#bbf7d0",
        "✅",
        "GO",
        "All quality gates passed. Release is approved.",
    ),
}
bg, accent, text, icon, label, subtitle = BANNERS.get(decision, BANNERS["GO"])

st.markdown(
    f"""
<div style="background:linear-gradient(135deg,{bg},{bg}bb); border:1px solid {accent}44;
            border-radius:16px; padding:28px 32px; margin-bottom:24px;">
    <div style="display:flex; align-items:center; gap:20px;">
        <span style="font-size:52px; flex-shrink:0;">{icon}</span>
        <div style="flex:1;">
            <div style="font-size:11px; color:{text}77; font-weight:700;
                        text-transform:uppercase; letter-spacing:0.12em; margin-bottom:4px;">
                Release Decision</div>
            <div style="font-size:36px; font-weight:900; color:{text};
                        letter-spacing:-0.03em; line-height:1.1;">{label}</div>
            <div style="font-size:14px; color:{text}cc; margin-top:6px;">{subtitle}</div>
        </div>
        {"<div style='text-align:right;'><div style='font-size:11px; color:" + text + "77; margin-bottom:4px;'>Risk Score</div><div style='font-size:42px; font-weight:900; color:" + text + ";'>" + f"{rdata.get('risk_score',0):.0f}" + "</div><div style='font-size:11px; color:" + text + "77;'>out of 100</div></div>" if rdata.get("risk_score") is not None else ""}
    </div>
    {f'<div style="margin-top:16px; background:rgba(0,0,0,0.2); border-radius:8px; padding:12px 16px; font-size:13px; color:{text}cc; font-style:italic; line-height:1.6;">{rdata.get("recommendation_text","")}</div>' if rdata.get("recommendation_text") else ""}
</div>""",
    unsafe_allow_html=True,
)

# ── KPI row ───────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("📋 Total Tests", rdata.get("total_tests", 0))
k2.metric("✅ Passed", rdata.get("passed", 0))
k3.metric("❌ Failed", rdata.get("failed", 0))
k4.metric("🔴 Critical", rdata.get("critical_bugs", 0))
k5.metric("🟠 High", rdata.get("high_bugs", 0))

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
if view == "🏢 Executive":
    try:
        import plotly.graph_objects as go

        chart1, chart2 = st.columns(2)

        with chart1:
            st.markdown(
                '<div class="tp-section-title">Test Results</div>',
                unsafe_allow_html=True,
            )
            passed = rdata.get("passed", 0)
            failed = rdata.get("failed", 0)
            total = passed + failed
            if total > 0:
                fig = go.Figure(
                    go.Pie(
                        labels=["Passed", "Failed"],
                        values=[passed, failed],
                        hole=0.6,
                        marker=dict(
                            colors=["#22c55e", "#ef4444"],
                            line=dict(color="#0F1117", width=2),
                        ),
                        textinfo="label+percent",
                        textfont=dict(color="white", size=12),
                    )
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#94A3B8"),
                    showlegend=False,
                    height=260,
                    margin=dict(l=20, r=20, t=20, b=20),
                    annotations=[
                        dict(
                            text=f"<b>{total}</b><br><span style='font-size:10px;'>Tests</span>",
                            x=0.5,
                            y=0.5,
                            font=dict(size=16, color="#F0F4FF"),
                            showarrow=False,
                        )
                    ],
                )
                st.plotly_chart(fig, use_container_width=True)

        with chart2:
            st.markdown(
                '<div class="tp-section-title">Bug Severity Breakdown</div>',
                unsafe_allow_html=True,
            )
            sev_labels = ["Critical", "High", "Medium", "Low"]
            sev_values = [rdata.get(f"{s.lower()}_bugs", 0) for s in sev_labels]
            sev_colors = ["#ef4444", "#f97316", "#eab308", "#22c55e"]
            if sum(sev_values) > 0:
                fig2 = go.Figure(
                    go.Bar(
                        x=sev_labels,
                        y=sev_values,
                        marker_color=sev_colors,
                        text=sev_values,
                        textposition="outside",
                        textfont=dict(color="white", size=13),
                    )
                )
                fig2.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#94A3B8"),
                    xaxis=dict(gridcolor="#1E2337", color="#64748B"),
                    yaxis=dict(gridcolor="#1E2337", color="#64748B"),
                    height=260,
                    margin=dict(l=20, r=20, t=20, b=20),
                    showlegend=False,
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.markdown(
                    """
                <div class="tp-card" style="height:200px; display:flex;
                     align-items:center; justify-content:center; text-align:center;">
                    <div>
                        <div style="font-size:32px; margin-bottom:8px;">🎉</div>
                        <div style="color:#4ade80; font-weight:700;">Zero bugs found!</div>
                    </div>
                </div>""",
                    unsafe_allow_html=True,
                )
    except Exception:
        pass

    # Bug summary table
    if bugs:
        st.markdown(
            '<div class="tp-section-title">Bug Summary</div>', unsafe_allow_html=True
        )
        SEV_ICONS = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}
        bug_list = bugs if isinstance(bugs[0], dict) else [b.model_dump() for b in bugs]
        rows = [
            {
                "": SEV_ICONS.get(b.get("severity", ""), "⚪"),
                "ID": b.get("id", ""),
                "Title": b.get("title", "")[:55]
                + ("..." if len(b.get("title", "")) > 55 else ""),
                "Severity": b.get("severity", ""),
                "Priority": b.get("priority", ""),
                "Fix Conf.": f"{b.get('fix_confidence',0):.0%}",
            }
            for b in bug_list
        ]
        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True,
            column_config={"": st.column_config.TextColumn("", width=30)},
        )

# ─────────────────────────────────────────────────────────────────────────────
else:  # Engineer view
    # Test results detail
    st.markdown(
        '<div class="tp-section-title">Test Results Detail</div>',
        unsafe_allow_html=True,
    )
    if execution:
        exec_data = execution if isinstance(execution, dict) else execution.model_dump()
        results = exec_data.get("results", [])
        if results:
            STATUS_ICONS = {"PASS": "✅", "FAIL": "❌", "ERROR": "⚠️", "SKIP": "⏭"}
            rows = [
                {
                    "Status": f"{STATUS_ICONS.get(r.get('status',''), '?')} {r.get('status','')}",
                    "Test ID": r.get("tc_id", ""),
                    "Duration": f"{r.get('duration_ms',0):.0f} ms",
                    "Error": (r.get("error_message", "") or "—")[:80],
                }
                for r in results
            ]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.caption("No individual test results available.")
    else:
        st.caption("No execution results in current session.")

    # Bug detail cards
    st.markdown(
        '<div class="tp-section-title">Bug Analysis</div>', unsafe_allow_html=True
    )
    if bugs:
        bug_list2 = (
            bugs if isinstance(bugs[0], dict) else [b.model_dump() for b in bugs]
        )
        SEV_STYLES2 = {
            "Critical": ("#450a0a", "#ef4444"),
            "High": ("#431407", "#f97316"),
            "Medium": ("#422006", "#f59e0b"),
            "Low": ("#052e16", "#22c55e"),
        }
        for b in bug_list2:
            sev = b.get("severity", "Medium")
            sb2, sa2 = SEV_STYLES2.get(sev, ("#1e293b", "#94a3b8"))
            with st.expander(f"🐛 {b.get('id','')} — {b.get('title','')[:55]}"):
                d1, d2 = st.columns(2)
                d1.markdown(
                    f"**Severity:** <span style='color:{sa2};'>{sev}</span>",
                    unsafe_allow_html=True,
                )
                d2.markdown(f"**Priority:** {b.get('priority','')}")
                st.markdown(f"**Root Cause:** {b.get('root_cause','')}")
                st.markdown(f"**Fix:** {b.get('fix_suggestion','')}")
                pc1, pc2, pc3 = st.columns(3)
                pc1.progress(
                    b.get("root_cause_confidence", 0),
                    text=f"Root Cause {b.get('root_cause_confidence',0):.0%}",
                )
                pc2.progress(
                    b.get("fix_confidence", 0),
                    text=f"Fix {b.get('fix_confidence',0):.0%}",
                )
                pc3.progress(
                    b.get("severity_confidence", 0),
                    text=f"Severity {b.get('severity_confidence',0):.0%}",
                )
    else:
        st.success("✅ No bugs found in last run.")

    # Agent performance
    st.markdown(
        '<div class="tp-section-title">Agent Performance</div>', unsafe_allow_html=True
    )
    try:
        from monitoring.metrics import metrics

        agent_data = metrics.get_all()
        if agent_data:
            rows2 = [
                {
                    "Agent": n,
                    "Runs": m.runs,
                    "Avg Latency": f"{m.avg_latency_ms:.0f} ms",
                    "Error Rate": f"{m.error_rate:.0%}",
                    "Health": "🟢 Healthy" if m.error_rate < 0.1 else "🔴 Issues",
                }
                for n, m in agent_data.items()
            ]
            st.dataframe(pd.DataFrame(rows2), use_container_width=True, hide_index=True)
        else:
            st.caption("No agent metrics yet.")
    except Exception:
        pass
