"""Page 02 — AI Test Generator: user story → requirements → test cases → verification."""
import streamlit as st
import json
from datetime import datetime
import uuid

st.set_page_config(page_title="Test Generator | AI TestPilot X", layout="wide")
st.title("AI Test Generator")

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())[:8]

# Step 1: User Story Input
st.subheader("Step 1: Enter User Story")
user_story = st.text_area(
    "User Story",
    placeholder="e.g. User should be able to login and checkout successfully",
    height=100,
    key="user_story_input"
)

col_analyze, col_clear = st.columns([1, 4])
with col_analyze:
    analyze_btn = st.button("Analyze Requirements", type="primary", disabled=not user_story.strip())

if analyze_btn and user_story.strip():
    with st.spinner("Analyzing requirements..."):
        try:
            from agents.requirement_agent import RequirementAgent
            agent = RequirementAgent()
            requirement = agent.run(user_story)
            st.session_state["requirement_context"] = requirement
            st.session_state["analysis_done"] = True
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.session_state["analysis_done"] = False

# Step 2: Requirement Analysis Results
if st.session_state.get("analysis_done") and st.session_state.get("requirement_context"):
    req = st.session_state["requirement_context"]
    st.divider()
    st.subheader("Step 2: Requirement Analysis")
    col1, col2, col3 = st.columns(3)
    col1.metric("Priority", req.priority)
    col2.metric("Modules", len(req.modules))
    col3.metric("Confidence", f"{req.confidence_score:.0%}")
    col_m, col_r = st.columns(2)
    with col_m:
        st.markdown("**Modules Identified:**")
        for m in req.modules:
            st.markdown(f"- {m}")
    with col_r:
        st.markdown("**Risk Areas:**")
        for r in req.risk_areas:
            st.markdown(f"- ⚠ {r}")

    # Explain AI button
    with st.expander("Explain AI Decision"):
        if st.button("Explain", key="explain_req"):
            try:
                from core.explain_engine import explain_decision
                explanation = explain_decision(f"Requirement analysis for: {user_story}\nIdentified modules: {req.modules}\nPriority: {req.priority}")
                st.write(explanation)
            except Exception:
                st.info("Explain AI not yet available (Phase 6).")

    # Step 3: Generate Test Cases
    st.divider()
    st.subheader("Step 3: Generate Test Cases")
    gen_btn = st.button("Generate Test Cases", type="primary")

    if gen_btn:
        with st.spinner("Generating test cases with AI..."):
            try:
                from agents.testcase_agent import TestCaseAgent
                tc_agent = TestCaseAgent()
                test_cases = tc_agent.run(req)
                st.session_state["generated_testcases"] = test_cases
                st.session_state["testcases_done"] = True
            except Exception as e:
                st.error(f"Test case generation failed: {e}")
                st.session_state["testcases_done"] = False

    if st.session_state.get("testcases_done") and st.session_state.get("generated_testcases"):
        tcs = st.session_state["generated_testcases"]
        st.success(f"Generated {len(tcs)} test cases")

        # Test cases table
        import pandas as pd
        df = pd.DataFrame([{
            "ID": tc.id, "Title": tc.title, "Module": tc.module,
            "Type": tc.type, "Priority": tc.priority,
            "Confidence": f"{tc.confidence_score:.0%}"
        } for tc in tcs])
        st.dataframe(df, use_container_width=True)

        # Coverage radar chart
        try:
            import plotly.graph_objects as go
            type_counts = {}
            for tc in tcs:
                type_counts[tc.type] = type_counts.get(tc.type, 0) + 1
            categories = ["Positive", "Negative", "Security", "Performance", "Boundary", "Accessibility"]
            values = [type_counts.get(c, 0) for c in categories]
            fig = go.Figure(data=go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill="toself",
                fillcolor="rgba(108,99,255,0.3)",
                line=dict(color="#6C63FF"),
            ))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True)), title="Test Coverage Radar", height=300)
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            pass

        # Verification
        st.divider()
        st.subheader("Step 4: Verification")
        verify_btn = st.button("Verify Coverage", type="secondary")
        if verify_btn:
            with st.spinner("Verifying test coverage..."):
                try:
                    from agents.verification_agent import VerificationAgent
                    v_agent = VerificationAgent()
                    verification = v_agent.run(tcs)
                    st.session_state["verification_report"] = verification
                    if verification.passed:
                        st.success(f"Coverage: {verification.coverage_score:.0%} — PASSED")
                    else:
                        st.warning(f"Coverage: {verification.coverage_score:.0%} — Below threshold")
                    if verification.missing_edge_cases:
                        st.markdown("**Missing Edge Cases:**")
                        for ec in verification.missing_edge_cases:
                            st.markdown(f"- ⚠ {ec}")
                except Exception as e:
                    st.error(f"Verification failed: {e}")

        # Export
        st.divider()
        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            if st.button("Export Test Cases (CSV)"):
                csv = df.to_csv(index=False)
                st.download_button("Download CSV", csv, "test_cases.csv", "text/csv")
        with col_exp2:
            if st.button("Send to Selenium Generator"):
                st.success("Test cases loaded. Navigate to Selenium Generator.")
