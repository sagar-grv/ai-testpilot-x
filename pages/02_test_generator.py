"""Page 02 — AI Test Generator: 4-step wizard."""

import streamlit as st
import uuid
import pandas as pd

st.set_page_config(
    page_title="AI Test Generator | AI TestPilot X", page_icon="🤖", layout="wide"
)

# ── Inject shared CSS + sidebar ───────────────────────────────────────────────
from pages._css import inject_css, sidebar_branding

inject_css()
sidebar_branding()


st.markdown(
    """
<h1 class="tp-page-title">🤖 AI Test Generator</h1>
<p class="tp-page-subtitle">
    Enter a plain-English user story — AI analyzes requirements, generates test cases, and verifies coverage.
</p>
""",
    unsafe_allow_html=True,
)
st.divider()

if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())[:8]


# ── Step indicator ────────────────────────────────────────────────────────────
def _step_indicator(active):
    steps = [
        ("1", "User Story", "analysis_done"),
        ("2", "Requirements", "analysis_done"),
        ("3", "Test Cases", "testcases_done"),
        ("4", "Verification", "verification_done"),
    ]
    parts = []
    for i, (num, label, key) in enumerate(steps):
        done = st.session_state.get(key, False)
        is_active = i + 1 == active
        if done:
            color, bg, border = "#4ade80", "#14532d", "#22c55e55"
            icon = "✓"
        elif is_active:
            color, bg, border = "#a78bfa", "#2e1065", "#6C63FF88"
            icon = num
        else:
            color, bg, border = "#334155", "#0F1117", "#1E2337"
            icon = num
        parts.append(f"""
        <div style="display:flex; align-items:center; gap:8px;">
            <div style="width:28px; height:28px; border-radius:50%;
                        background:{bg}; border:1.5px solid {border};
                        display:flex; align-items:center; justify-content:center;
                        font-size:12px; font-weight:800; color:{color};">{icon}</div>
            <span style="font-size:13px; font-weight:{'700' if is_active or done else '400'};
                         color:{color};">{label}</span>
        </div>""")
        if i < len(steps) - 1:
            parts.append(
                '<div style="flex:1; height:1px; background:#1E2337; margin:0 4px;"></div>'
            )
    return f'<div style="display:flex; align-items:center; gap:4px; margin-bottom:24px;">{"".join(parts)}</div>'


# Determine active step
if not st.session_state.get("analysis_done"):
    active_step = 1
elif not st.session_state.get("testcases_done"):
    active_step = 2
elif not st.session_state.get("verification_done"):
    active_step = 3
else:
    active_step = 4

st.markdown(_step_indicator(active_step), unsafe_allow_html=True)

# ── Step 1: User Story ────────────────────────────────────────────────────────
st.markdown(
    """
<div style="font-size:15px; font-weight:700; color:#F0F4FF; margin-bottom:10px;">
    Step 1 &nbsp;—&nbsp; Describe the feature
</div>""",
    unsafe_allow_html=True,
)

# Example chips
st.markdown(
    """
<div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:10px;">
    <span style="background:#1E2337; color:#94A3B8; border:1px solid #2D3557;
        border-radius:20px; padding:4px 12px; font-size:12px; cursor:default;">
        💡 Examples:
    </span>
    <span style="background:#6C63FF22; color:#a78bfa; border:1px solid #6C63FF44;
        border-radius:20px; padding:4px 12px; font-size:12px;">
        User should login and checkout successfully
    </span>
    <span style="background:#6C63FF22; color:#a78bfa; border:1px solid #6C63FF44;
        border-radius:20px; padding:4px 12px; font-size:12px;">
        Admin can manage user accounts
    </span>
    <span style="background:#6C63FF22; color:#a78bfa; border:1px solid #6C63FF44;
        border-radius:20px; padding:4px 12px; font-size:12px;">
        Search filters work correctly
    </span>
</div>""",
    unsafe_allow_html=True,
)

user_story = st.text_area(
    "User Story",
    placeholder="e.g. User should be able to login with valid credentials and checkout a product successfully",
    height=96,
    label_visibility="collapsed",
    key="user_story_input",
)

btn_col, clear_col = st.columns([2, 6])
with btn_col:
    analyze_btn = st.button(
        "🔍 Analyze Requirements",
        type="primary",
        disabled=not user_story.strip(),
        use_container_width=True,
    )

if analyze_btn and user_story.strip():
    with st.spinner("Analyzing requirements with Gemini AI..."):
        try:
            from agents.requirement_agent import RequirementAgent

            req = RequirementAgent().run(user_story)
            st.session_state["requirement_context"] = req
            st.session_state["analysis_done"] = True
            st.session_state.pop("testcases_done", None)
            st.session_state.pop("generated_testcases", None)
            st.session_state.pop("verification_done", None)
            st.rerun()
        except Exception as e:
            st.error(f"Analysis failed: {e}")

# ── Step 2: Requirement Analysis ─────────────────────────────────────────────
if st.session_state.get("analysis_done") and (
    req := st.session_state.get("requirement_context")
):
    st.divider()
    st.markdown(
        """
    <div style="font-size:15px; font-weight:700; color:#F0F4FF; margin-bottom:12px;">
        Step 2 &nbsp;—&nbsp; Requirement Analysis
        <span style="background:#14532d; color:#4ade80; border:1px solid #22c55e44;
            border-radius:20px; padding:2px 10px; font-size:11px; font-weight:700;
            margin-left:10px;">Complete</span>
    </div>""",
        unsafe_allow_html=True,
    )

    PRIO_STYLE = {
        "Critical": ("#7f1d1d", "#f87171"),
        "High": ("#78350f", "#fbbf24"),
        "Medium": ("#713f12", "#fde047"),
        "Low": ("#14532d", "#4ade80"),
    }
    pb, pt = PRIO_STYLE.get(req.priority, ("#1e293b", "#94a3b8"))

    rc1, rc2, rc3 = st.columns(3)
    with rc1:
        st.markdown(
            f"""
        <div class="tp-card-sm">
            <div class="tp-section-title" style="margin-top:0;">Modules Identified</div>
            <div style="display:flex; flex-wrap:wrap; gap:6px; margin-top:8px;">
                {"".join(f'<span style="background:#1E2337; color:#94A3B8; border:1px solid #2D3557; border-radius:6px; padding:4px 10px; font-size:12px; font-weight:500;">{m}</span>' for m in req.modules)}
            </div>
        </div>""",
            unsafe_allow_html=True,
        )
    with rc2:
        st.markdown(
            f"""
        <div class="tp-card-sm">
            <div class="tp-section-title" style="margin-top:0;">Risk Areas</div>
            <div style="display:flex; flex-wrap:wrap; gap:6px; margin-top:8px;">
                {"".join(f'<span style="background:#7f1d1d22; color:#fca5a5; border:1px solid #ef444433; border-radius:6px; padding:4px 10px; font-size:12px; font-weight:500;">⚠ {r}</span>' for r in req.risk_areas)}
            </div>
        </div>""",
            unsafe_allow_html=True,
        )
    with rc3:
        st.markdown(
            f"""
        <div class="tp-card-sm">
            <div class="tp-section-title" style="margin-top:0;">Priority & Confidence</div>
            <div style="display:flex; align-items:center; gap:12px; margin-top:10px;">
                <span style="background:{pb}; color:{pt}; border:1px solid {pt}44;
                    border-radius:20px; padding:4px 14px; font-size:13px; font-weight:800;">
                    {req.priority}
                </span>
                <span style="font-size:20px; font-weight:800; color:#F0F4FF;">
                    {req.confidence_score:.0%}
                </span>
                <span style="font-size:12px; color:#64748B;">confidence</span>
            </div>
        </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Step 3: Generate Test Cases ───────────────────────────────────────────
    st.markdown(
        """
    <div style="font-size:15px; font-weight:700; color:#F0F4FF; margin-bottom:12px;">
        Step 3 &nbsp;—&nbsp; Generate Test Cases
    </div>""",
        unsafe_allow_html=True,
    )

    gen_btn = st.button("📝 Generate Test Cases with AI", type="primary")

    if gen_btn:
        with st.spinner("Generating comprehensive test cases with RAG context..."):
            try:
                from agents.testcase_agent import TestCaseAgent

                tcs = TestCaseAgent().run(req)
                st.session_state["generated_testcases"] = tcs
                st.session_state["testcases_done"] = True
                st.session_state.pop("verification_done", None)
                st.rerun()
            except Exception as e:
                st.error(f"Generation failed: {e}")

    if st.session_state.get("testcases_done") and (
        tcs := st.session_state.get("generated_testcases")
    ):
        # Summary banner
        type_counts = {}
        for tc in tcs:
            type_counts[tc.type] = type_counts.get(tc.type, 0) + 1

        chips = " ".join(
            f'<span style="background:#1E2337; color:#94A3B8; border:1px solid #2D3557; border-radius:6px; padding:3px 10px; font-size:12px;">{v}× {k}</span>'
            for k, v in type_counts.items()
        )
        st.markdown(
            f"""
        <div style="background:linear-gradient(135deg,#1e1b4b,#2e1065);
                    border:1px solid #6C63FF44; border-radius:12px;
                    padding:18px 22px; margin:14px 0; display:flex; align-items:center; gap:16px;">
            <span style="font-size:32px;">📝</span>
            <div>
                <div style="font-size:20px; font-weight:800; color:#F0F4FF;">
                    {len(tcs)} Test Cases Generated
                </div>
                <div style="display:flex; flex-wrap:wrap; gap:6px; margin-top:8px;">{chips}</div>
            </div>
        </div>""",
            unsafe_allow_html=True,
        )

        # Test case table
        TYPE_COLORS = {
            "Positive": "#22c55e",
            "Negative": "#ef4444",
            "Security": "#f59e0b",
            "Performance": "#3b82f6",
            "Boundary": "#ec4899",
            "Accessibility": "#a855f7",
        }
        PRIO_COLORS = {
            "Critical": "#ef4444",
            "High": "#f59e0b",
            "Medium": "#eab308",
            "Low": "#22c55e",
        }

        df_rows = []
        for tc in tcs:
            df_rows.append(
                {
                    "ID": tc.id,
                    "Title": tc.title,
                    "Module": tc.module,
                    "Type": tc.type,
                    "Priority": tc.priority,
                    "Steps": len(tc.steps),
                    "Conf.": f"{tc.confidence_score:.0%}",
                }
            )
        df = pd.DataFrame(df_rows)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.TextColumn("ID", width=60),
                "Title": st.column_config.TextColumn("Title"),
                "Module": st.column_config.TextColumn("Module", width=100),
                "Type": st.column_config.TextColumn("Type", width=100),
                "Priority": st.column_config.TextColumn("Priority", width=90),
                "Steps": st.column_config.NumberColumn("Steps", width=60),
                "Conf.": st.column_config.TextColumn("Conf.", width=60),
            },
        )

        # Coverage radar
        try:
            import plotly.graph_objects as go

            cats = [
                "Positive",
                "Negative",
                "Security",
                "Performance",
                "Boundary",
                "Accessibility",
            ]
            vals = [type_counts.get(c, 0) for c in cats]
            fig = go.Figure(
                data=go.Scatterpolar(
                    r=vals + [vals[0]],
                    theta=cats + [cats[0]],
                    fill="toself",
                    fillcolor="rgba(108,99,255,0.15)",
                    line=dict(color="#6C63FF", width=2),
                    marker=dict(size=5, color="#6C63FF"),
                )
            )
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True, showticklabels=False, gridcolor="#1E2337"
                    ),
                    angularaxis=dict(gridcolor="#1E2337"),
                    bgcolor="#0F1117",
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94A3B8", size=12),
                title=dict(
                    text="Coverage Radar", font=dict(size=13, color="#94A3B8"), x=0.5
                ),
                height=300,
                margin=dict(l=50, r=50, t=40, b=20),
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            pass

        # ── Step 4: Verification ──────────────────────────────────────────────
        st.divider()
        st.markdown(
            """
        <div style="font-size:15px; font-weight:700; color:#F0F4FF; margin-bottom:12px;">
            Step 4 &nbsp;—&nbsp; Verify Coverage
        </div>""",
            unsafe_allow_html=True,
        )

        vcol, _ = st.columns([2, 6])
        with vcol:
            verify_btn = st.button(
                "✅ Run Verification Check", use_container_width=True
            )

        if verify_btn:
            with st.spinner("Checking coverage, duplicates, and edge case gaps..."):
                try:
                    from agents.verification_agent import VerificationAgent

                    v = VerificationAgent().run(tcs)
                    st.session_state["verification_report"] = v
                    st.session_state["verification_done"] = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Verification failed: {e}")

        if v_rep := st.session_state.get("verification_report"):
            pct = int(v_rep.coverage_score * 100)
            passed = v_rep.passed
            vrow1, vrow2, vrow3 = st.columns(3)
            vrow1.metric(
                "Coverage Score",
                f"{pct}%",
                delta="✓ Pass" if passed else "Below 60% threshold",
            )
            vrow2.metric(
                "Duplicates Found",
                v_rep.duplicate_count,
                delta=(
                    "None detected" if v_rep.duplicate_count == 0 else "Review needed"
                ),
            )
            vrow3.metric("Edge Case Gaps", len(v_rep.missing_edge_cases))

            if v_rep.missing_edge_cases:
                st.warning("**Missing edge cases detected:**")
                for ec in v_rep.missing_edge_cases:
                    st.markdown(f"- ⚠ {ec}")
            elif passed:
                st.success(
                    "✅ Coverage verified — all test types present, no critical gaps found."
                )

        # Export row
        st.divider()
        ex1, ex2 = st.columns(2)
        with ex1:
            csv = df.to_csv(index=False)
            st.download_button(
                "⬇ Export CSV",
                csv,
                "test_cases.csv",
                "text/csv",
                use_container_width=True,
            )
        with ex2:
            if st.button(
                "▶ Go to Selenium Generator →", type="primary", use_container_width=True
            ):
                st.success(
                    "✅ Test cases saved to session. Open **Selenium Generator** in the sidebar."
                )
