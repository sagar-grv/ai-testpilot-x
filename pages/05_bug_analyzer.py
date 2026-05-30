"""Page 05 — Bug Analyzer with AI + RAG."""

import streamlit as st

st.set_page_config(
    page_title="Bug Analyzer | AI TestPilot X", page_icon="🐛", layout="wide"
)

# ── Inject shared CSS + sidebar ───────────────────────────────────────────────
from pages._css import inject_css, sidebar_branding

inject_css()
sidebar_branding()


st.markdown(
    """
<h1 class="tp-page-title">🐛 Bug Analyzer</h1>
<p class="tp-page-subtitle">
    Paste any error log or stack trace — AI identifies root cause, severity, and fix using RAG-backed analysis.
</p>
""",
    unsafe_allow_html=True,
)
st.divider()

# ── Input ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="tp-section-title">Input</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📋 Paste Log", "📁 Upload File", "🔍 From Last Run"])

log_text = ""
with tab1:
    log_text = st.text_area(
        "Paste error log",
        placeholder="NoSuchElementException: Unable to locate element: #login-btn\n  at LoginPage.py:42...",
        height=140,
        label_visibility="collapsed",
        key="paste_log",
    )

with tab2:
    uploaded = st.file_uploader("Upload a log file (.txt or .log)", type=["txt", "log"])
    if uploaded:
        log_text = uploaded.read().decode("utf-8", errors="ignore")
        st.success(f"Loaded {len(log_text)} characters from {uploaded.name}")
        st.code(
            log_text[:500] + ("..." if len(log_text) > 500 else ""), language="text"
        )

with tab3:
    exec_results = st.session_state.get("execution_results")
    if exec_results:
        failed_tests = [
            r for r in exec_results.results if r.status in ("FAIL", "ERROR")
        ]
        if failed_tests:
            sel_id = st.selectbox("Select failed test", [r.tc_id for r in failed_tests])
            sel = next(r for r in failed_tests if r.tc_id == sel_id)
            log_text = sel.error_message or ""
            if log_text:
                st.markdown(
                    f"""
                <div style="background:#0F1117; border:1px solid #1E2337; border-radius:8px;
                            padding:12px 14px; font-family:monospace; font-size:12px;
                            color:#94A3B8; white-space:pre-wrap; word-break:break-all;">
                    {log_text[:300]}{"..." if len(log_text) > 300 else ""}
                </div>""",
                    unsafe_allow_html=True,
                )
        else:
            st.success("✅ No failed tests in last run!")
    else:
        st.markdown(
            """
        <div style="background:#0F1117; border:1px dashed #1E2337; border-radius:10px;
                    padding:20px; text-align:center; color:#334155; font-size:13px;">
            No execution results yet. Run tests on the Selenium Generator page first.
        </div>""",
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)
analyze_col, _ = st.columns([2, 6])
with analyze_col:
    analyze_btn = st.button(
        "🔍 Analyze with AI",
        type="primary",
        disabled=not (log_text or "").strip(),
        use_container_width=True,
    )

if analyze_btn and log_text.strip():
    with st.spinner("AI analyzing failure with RAG correlation..."):
        try:
            from agents.bug_agent import BugAgent

            session_id = st.session_state.get("session_id", "demo")
            bug = BugAgent().analyze_single(log_text, session_id=session_id)
            st.session_state["current_bug"] = bug
            st.rerun()
        except Exception as e:
            st.error(f"Analysis failed: {e}")

# ── Bug Report ────────────────────────────────────────────────────────────────
bug = st.session_state.get("current_bug")
if bug:
    st.divider()

    SEV_STYLES = {
        "Critical": ("#450a0a", "#ef4444", "#fca5a5", "🔴"),
        "High": ("#431407", "#f97316", "#fdba74", "🟠"),
        "Medium": ("#422006", "#f59e0b", "#fde68a", "🟡"),
        "Low": ("#052e16", "#22c55e", "#bbf7d0", "🟢"),
    }
    sb, sa, st2, sicon = SEV_STYLES.get(
        bug.severity, ("#1e293b", "#94a3b8", "#cbd5e1", "⚪")
    )

    # Severity header band
    st.markdown(
        f"""
    <div style="background:{sb}; border:1px solid {sa}44; border-radius:12px;
                padding:18px 22px; margin-bottom:20px;
                display:flex; align-items:center; gap:14px;">
        <span style="font-size:36px;">{sicon}</span>
        <div>
            <div style="font-size:11px; color:{st2}88; font-weight:700;
                        text-transform:uppercase; letter-spacing:0.1em;">Bug Report</div>
            <div style="font-size:22px; font-weight:800; color:{st2};">
                {bug.severity} Severity &nbsp;·&nbsp; {bug.priority}</div>
            <div style="font-size:13px; color:{st2}99; margin-top:3px;">
                {bug.title}</div>
        </div>
        <div style="margin-left:auto; text-align:right;">
            <div style="font-size:11px; color:{st2}66;">Bug ID</div>
            <div style="font-family:monospace; font-size:13px; color:{st2}99;">{bug.id}</div>
        </div>
    </div>""",
        unsafe_allow_html=True,
    )

    # Failure signature
    st.markdown(
        '<div class="tp-section-title">Failure Signature</div>', unsafe_allow_html=True
    )
    st.code(bug.failure_signature, language="text")

    # Root cause + Fix side by side
    rc_col, fix_col = st.columns(2)
    with rc_col:
        st.markdown(
            """
        <div style="font-size:13px; font-weight:700; color:#F0F4FF; margin-bottom:10px;">
            🔍 Root Cause</div>""",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
        <div class="tp-card" style="margin-bottom:12px; min-height:80px;">
            <div style="font-size:13px; color:#CBD5E1; line-height:1.6;">{bug.root_cause}</div>
        </div>""",
            unsafe_allow_html=True,
        )
        st.progress(
            bug.root_cause_confidence,
            text=f"Root cause confidence: {bug.root_cause_confidence:.0%}",
        )

    with fix_col:
        st.markdown(
            """
        <div style="font-size:13px; font-weight:700; color:#F0F4FF; margin-bottom:10px;">
            🔧 Fix Suggestion</div>""",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
        <div class="tp-card" style="margin-bottom:12px; min-height:80px;">
            <div style="font-size:13px; color:#CBD5E1; line-height:1.6;">{bug.fix_suggestion}</div>
        </div>""",
            unsafe_allow_html=True,
        )
        st.progress(
            bug.fix_confidence, text=f"Fix confidence: {bug.fix_confidence:.0%}"
        )

    # Confidence breakdown
    st.markdown(
        '<div class="tp-section-title">Confidence Breakdown</div>',
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Root Cause", f"{bug.root_cause_confidence:.0%}")
    c2.metric("Fix Suggestion", f"{bug.fix_confidence:.0%}")
    c3.metric("Severity", f"{bug.severity_confidence:.0%}")

    # RAG matches
    if bug.rag_matches:
        st.markdown(
            '<div class="tp-section-title">Similar Past Bugs (RAG)</div>',
            unsafe_allow_html=True,
        )
        for i, match in enumerate(bug.rag_matches[:5]):
            similarity = max(0.0, 1.0 - float(match.get("distance", 0.5)))
            sim_color = (
                "#22c55e"
                if similarity > 0.7
                else "#f59e0b" if similarity > 0.4 else "#64748B"
            )
            with st.expander(
                f"Match #{i+1}  ·  Similarity: {similarity:.0%}  ·  {match.get('id','unknown')}"
            ):
                st.markdown(
                    f"""
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
                    <div style="flex:1; height:6px; background:#1E2337; border-radius:3px; overflow:hidden;">
                        <div style="width:{similarity*100:.0f}%; height:100%;
                                    background:{sim_color}; border-radius:3px;"></div>
                    </div>
                    <span style="color:{sim_color}; font-weight:700; font-size:12px;">
                        {similarity:.0%}</span>
                </div>""",
                    unsafe_allow_html=True,
                )
                st.write(match.get("text", "")[:250])
                if match.get("metadata"):
                    st.json(match["metadata"])

    # Actions
    st.divider()
    act1, act2 = st.columns(2)
    if act1.button(
        "🔧 Send to Healing Agent", use_container_width=True, type="primary"
    ):
        st.session_state["healing_bug"] = bug
        st.success(
            "Sent to Healing Agent. Navigate to **Selenium Generator** to apply the fix."
        )
    if act2.button("⬇ Export Bug Report (Markdown)", use_container_width=True):
        md = f"""# Bug Report — {bug.id}

**Severity:** {bug.severity}  
**Priority:** {bug.priority}  
**Confidence:** {bug.severity_confidence:.0%}

## Failure Signature
```
{bug.failure_signature}
```

## Root Cause
{bug.root_cause}

*Confidence: {bug.root_cause_confidence:.0%}*

## Fix Suggestion
{bug.fix_suggestion}

*Confidence: {bug.fix_confidence:.0%}*
"""
        st.download_button(
            "Download bug_report.md",
            md,
            "bug_report.md",
            "text/markdown",
            use_container_width=True,
        )

else:
    if not log_text.strip():
        st.markdown(
            """
        <div style="background:#0F1117; border:1px dashed #1E2337; border-radius:14px;
                    padding:48px 32px; text-align:center;">
            <div style="font-size:48px; margin-bottom:12px;">🐛</div>
            <div style="font-size:18px; font-weight:700; color:#F0F4FF; margin-bottom:8px;">
                Ready to analyze</div>
            <div style="font-size:13px; color:#475569; max-width:360px; margin:0 auto;">
                Paste a stack trace or error log above, then click
                <strong style="color:#6C63FF;">Analyze with AI</strong>.
            </div>
        </div>""",
            unsafe_allow_html=True,
        )
