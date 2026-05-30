"""Page 02 — AI Test Generator."""
import streamlit as st
import uuid
import pandas as pd

st.set_page_config(page_title="Test Generator | AI TestPilot X", page_icon="🤖", layout="wide")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<h2 style='margin:0; font-size:26px; font-weight:700;'>🤖 AI Test Generator</h2>
<p style='color:#718096; margin-top:4px;'>
    Enter a plain-English user story and AI generates structured test cases automatically.
</p>
""", unsafe_allow_html=True)
st.divider()

if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())[:8]

# ── Step 1: User Story ────────────────────────────────────────────────────────
st.markdown("""
<div style='display:flex; align-items:center; gap:10px; margin-bottom:12px;'>
    <div style='background:#6C63FF; color:white; border-radius:50%; width:28px; height:28px;
         display:flex; align-items:center; justify-content:center; font-weight:700; font-size:13px;'>1</div>
    <span style='font-weight:600; font-size:16px;'>Enter User Story</span>
</div>
""", unsafe_allow_html=True)

user_story = st.text_area(
    "Describe what the user should be able to do:",
    placeholder="e.g. User should be able to login with valid credentials and checkout a product successfully",
    height=100,
    label_visibility="collapsed"
)

col_btn, col_eg = st.columns([1, 4])
with col_btn:
    analyze_btn = st.button("🔍 Analyze Requirements", type="primary",
                            disabled=not user_story.strip(), use_container_width=True)
with col_eg:
    if st.button("💡 Use Example", use_container_width=True):
        st.session_state["_example"] = True
        st.rerun()

if st.session_state.get("_example") and not user_story.strip():
    user_story = "User should be able to login and checkout successfully"
    st.session_state.pop("_example", None)

# ── Step 2: Requirement Analysis ─────────────────────────────────────────────
if analyze_btn and user_story.strip():
    with st.spinner("🔍 Analyzing requirements with Gemini AI..."):
        try:
            from agents.requirement_agent import RequirementAgent
            agent = RequirementAgent()
            requirement = agent.run(user_story)
            st.session_state["requirement_context"] = requirement
            st.session_state["analysis_done"] = True
            st.session_state.pop("testcases_done", None)
        except Exception as e:
            st.session_state["analysis_done"] = False
            st.error(f"❌ Analysis failed: {e}")

if st.session_state.get("analysis_done") and st.session_state.get("requirement_context"):
    req = st.session_state["requirement_context"]
    st.divider()
    st.markdown("""
    <div style='display:flex; align-items:center; gap:10px; margin-bottom:12px;'>
        <div style='background:#48BB78; color:white; border-radius:50%; width:28px; height:28px;
             display:flex; align-items:center; justify-content:center; font-weight:700; font-size:13px;'>2</div>
        <span style='font-weight:600; font-size:16px;'>Requirement Analysis</span>
        <span style='background:#276749; color:#9AE6B4; border-radius:20px; padding:2px 10px; font-size:12px;'>Complete</span>
    </div>
    """, unsafe_allow_html=True)

    PRIORITY_COLORS = {"Critical": "#FC8181", "High": "#F6AD55", "Medium": "#ECC94B", "Low": "#68D391"}
    pcolor = PRIORITY_COLORS.get(req.priority, "#A0AEC0")

    rc1, rc2, rc3 = st.columns(3)
    with rc1:
        st.markdown(f"""
        <div style='background:#1E2130; border:1px solid #2E3250; border-radius:10px; padding:16px;'>
            <div style='color:#A0AEC0; font-size:11px; text-transform:uppercase; letter-spacing:0.08em;'>Modules Identified</div>
            <div style='margin-top:10px;'>
                {"".join(f'<span style="background:#2D3748; border-radius:6px; padding:4px 10px; margin:3px 3px 3px 0; display:inline-block; font-size:13px;">{m}</span>' for m in req.modules)}
            </div>
        </div>""", unsafe_allow_html=True)
    with rc2:
        st.markdown(f"""
        <div style='background:#1E2130; border:1px solid #2E3250; border-radius:10px; padding:16px;'>
            <div style='color:#A0AEC0; font-size:11px; text-transform:uppercase; letter-spacing:0.08em;'>Risk Areas</div>
            <div style='margin-top:10px;'>
                {"".join(f'<span style="background:#742A2A; color:#FEB2B2; border-radius:6px; padding:4px 10px; margin:3px 3px 3px 0; display:inline-block; font-size:13px;">⚠ {r}</span>' for r in req.risk_areas)}
            </div>
        </div>""", unsafe_allow_html=True)
    with rc3:
        st.markdown(f"""
        <div style='background:#1E2130; border:1px solid #2E3250; border-radius:10px; padding:16px;'>
            <div style='color:#A0AEC0; font-size:11px; text-transform:uppercase; letter-spacing:0.08em;'>Priority & Confidence</div>
            <div style='margin-top:10px; display:flex; align-items:center; gap:12px;'>
                <span style='background:{pcolor}22; color:{pcolor}; border:1px solid {pcolor}55;
                    border-radius:20px; padding:4px 14px; font-weight:700; font-size:14px;'>{req.priority}</span>
                <span style='color:#A0AEC0; font-size:13px;'>{req.confidence_score:.0%} confidence</span>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Step 3: Generate Test Cases ───────────────────────────────────────────
    st.markdown("""
    <div style='display:flex; align-items:center; gap:10px; margin-bottom:12px;'>
        <div style='background:#6C63FF; color:white; border-radius:50%; width:28px; height:28px;
             display:flex; align-items:center; justify-content:center; font-weight:700; font-size:13px;'>3</div>
        <span style='font-weight:600; font-size:16px;'>Generate Test Cases</span>
    </div>
    """, unsafe_allow_html=True)

    gen_btn = st.button("📝 Generate Test Cases with AI", type="primary")
    if gen_btn:
        with st.spinner("📝 Generating comprehensive test cases..."):
            try:
                from agents.testcase_agent import TestCaseAgent
                tc_agent = TestCaseAgent()
                test_cases = tc_agent.run(req)
                st.session_state["generated_testcases"] = test_cases
                st.session_state["testcases_done"] = True
            except Exception as e:
                st.session_state["testcases_done"] = False
                st.error(f"❌ Generation failed: {e}")

    if st.session_state.get("testcases_done") and st.session_state.get("generated_testcases"):
        tcs = st.session_state["generated_testcases"]

        # Summary badges
        type_counts = {}
        for tc in tcs:
            type_counts[tc.type] = type_counts.get(tc.type, 0) + 1

        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#1A365D,#2A4A8E); border-radius:10px;
             padding:16px 20px; margin:12px 0; display:flex; align-items:center; gap:16px;'>
            <span style='font-size:28px;'>📝</span>
            <div>
                <div style='font-size:20px; font-weight:700;'>{len(tcs)} Test Cases Generated</div>
                <div style='color:#90CDF4; font-size:13px; margin-top:4px;'>
                    {" · ".join(f'{v} {k}' for k, v in type_counts.items())}
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        # Test cases table with color-coded priorities
        TYPE_COLORS = {"Positive": "#48BB78", "Negative": "#FC8181", "Security": "#F6AD55",
                       "Performance": "#4299E1", "Boundary": "#ED64A6", "Accessibility": "#9F7AEA"}
        PRIO_COLORS = {"Critical": "#FC8181", "High": "#F6AD55", "Medium": "#ECC94B", "Low": "#68D391"}

        df_data = []
        for tc in tcs:
            tc_color = TYPE_COLORS.get(tc.type, "#A0AEC0")
            p_color = PRIO_COLORS.get(tc.priority, "#A0AEC0")
            df_data.append({
                "ID": tc.id,
                "Title": tc.title,
                "Module": tc.module,
                "Type": tc.type,
                "Priority": tc.priority,
                "Steps": len(tc.steps),
                "Confidence": f"{tc.confidence_score:.0%}"
            })

        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True,
                     column_config={
                         "ID": st.column_config.TextColumn("ID", width="small"),
                         "Title": st.column_config.TextColumn("Title", width="large"),
                         "Type": st.column_config.TextColumn("Type", width="small"),
                         "Priority": st.column_config.TextColumn("Priority", width="small"),
                         "Steps": st.column_config.NumberColumn("Steps", width="small"),
                         "Confidence": st.column_config.TextColumn("Conf.", width="small"),
                     })

        # Coverage radar
        try:
            import plotly.graph_objects as go
            categories = ["Positive", "Negative", "Security", "Performance", "Boundary", "Accessibility"]
            values = [type_counts.get(c, 0) for c in categories]
            fig = go.Figure(data=go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill="toself",
                fillcolor="rgba(108,99,255,0.2)",
                line=dict(color="#6C63FF", width=2),
                marker=dict(size=6, color="#6C63FF")
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, showticklabels=False, gridcolor="#2E3250"),
                    angularaxis=dict(gridcolor="#2E3250"),
                    bgcolor="#1E2130"
                ),
                paper_bgcolor="#0E1117",
                plot_bgcolor="#0E1117",
                title=dict(text="Test Coverage Radar", font=dict(size=14, color="#FAFAFA"), x=0.5),
                height=320,
                margin=dict(l=40, r=40, t=40, b=20),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            pass

        # ── Step 4: Verification ──────────────────────────────────────────────
        st.divider()
        st.markdown("""
        <div style='display:flex; align-items:center; gap:10px; margin-bottom:12px;'>
            <div style='background:#ED8936; color:white; border-radius:50%; width:28px; height:28px;
                 display:flex; align-items:center; justify-content:center; font-weight:700; font-size:13px;'>4</div>
            <span style='font-weight:600; font-size:16px;'>Verify Coverage</span>
        </div>
        """, unsafe_allow_html=True)

        vcol1, vcol2 = st.columns([1, 3])
        with vcol1:
            verify_btn = st.button("✅ Run Verification", use_container_width=True)
        if verify_btn:
            with st.spinner("Checking coverage and edge cases..."):
                try:
                    from agents.verification_agent import VerificationAgent
                    v_agent = VerificationAgent()
                    verification = v_agent.run(tcs)
                    st.session_state["verification_report"] = verification
                except Exception as e:
                    st.error(f"Verification failed: {e}")

        if st.session_state.get("verification_report"):
            v = st.session_state["verification_report"]
            vcols = st.columns(3)
            coverage_pct = int(v.coverage_score * 100)
            vcols[0].metric("Coverage Score", f"{coverage_pct}%",
                            delta="✅ Pass" if v.passed else "⚠ Below threshold")
            vcols[1].metric("Duplicates Found", v.duplicate_count,
                            delta="None" if v.duplicate_count == 0 else "Review needed")
            vcols[2].metric("Edge Case Gaps", len(v.missing_edge_cases))

            if v.missing_edge_cases:
                st.warning("**Missing Edge Cases Detected:**")
                for ec in v.missing_edge_cases:
                    st.markdown(f"- ⚠ {ec}")
            elif v.passed:
                st.success("✅ Coverage verified — all test types present, no critical gaps found.")

        # ── Export ────────────────────────────────────────────────────────────
        st.divider()
        ecol1, ecol2 = st.columns(2)
        with ecol1:
            csv_data = df.to_csv(index=False)
            st.download_button("⬇ Export as CSV", csv_data, "test_cases.csv",
                               "text/csv", use_container_width=True)
        with ecol2:
            if st.button("▶ Send to Selenium Generator →", use_container_width=True, type="primary"):
                st.success("✅ Test cases ready. Navigate to **Selenium Generator** in the sidebar.")
