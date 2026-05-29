"""Page 03 — Selenium Script Generator with HITL gate and self-healing."""
import streamlit as st
from config import settings
from urllib.parse import urlparse

st.set_page_config(page_title="Selenium Generator | AI TestPilot X", layout="wide")
st.title("Selenium Script Generator")

test_cases = st.session_state.get("generated_testcases", [])

if not test_cases:
    st.warning("No test cases loaded. Go to **AI Test Generator** first.")
    st.stop()

# Controls
col1, col2 = st.columns(2)
with col1:
    tc_options = {tc.id: f"{tc.id} — {tc.title}" for tc in test_cases}
    selected_tc_id = st.selectbox(
        "Select Test Case",
        options=list(tc_options.keys()),
        format_func=lambda x: tc_options[x]
    )
with col2:
    target_url = st.text_input("Target URL", value="https://www.saucedemo.com")

st.radio("Framework", ["Selenium (Python)", "Playwright (coming soon)"], horizontal=True)
st.caption(f"Execution Mode: **{settings.EXECUTION_MODE}**")

# Generate Script
if st.button("Generate Script", type="primary"):
    selected_tc = next(tc for tc in test_cases if tc.id == selected_tc_id)
    with st.spinner(f"Generating Selenium script for {selected_tc_id}..."):
        try:
            from agents.selenium_agent import SeleniumAgent
            agent = SeleniumAgent()
            script = agent.generate_for_tc(selected_tc, target_url)
            st.session_state["current_script"] = script
            st.session_state["current_tc_id"] = selected_tc_id
            st.session_state["target_url"] = target_url
            st.session_state["execution_approved"] = None
            st.success(f"Script generated for {selected_tc_id}")
        except Exception as e:
            st.error(f"Script generation failed: {e}")

# Display Script
if "current_script" in st.session_state:
    st.subheader("Generated Script")
    try:
        from streamlit_ace import st_ace
        edited_script = st_ace(
            value=st.session_state["current_script"],
            language="python",
            theme="monokai",
            height=300,
            key="script_editor"
        )
    except ImportError:
        edited_script = st.text_area(
            "Script (edit before running)",
            value=st.session_state["current_script"],
            height=300,
            key="script_editor"
        )
    st.session_state["edited_script"] = edited_script

    st.divider()
    st.subheader("Execution Gate")

    from agents.execution_agent import ExecutionAgent
    exec_agent = ExecutionAgent()
    domain = urlparse(target_url).netloc or target_url
    is_trusted = exec_agent.check_trust_domain(domain)

    if is_trusted:
        st.success(f"TRUSTED DOMAIN: {domain} — Auto-approved")
        st.session_state["execution_approved"] = "auto"
    else:
        st.warning(f"Domain **{domain}** requires approval before execution.")
        col_a, col_b, col_c = st.columns(3)
        if col_a.button("Approve Once"):
            st.session_state["execution_approved"] = "once"
            st.rerun()
        if col_b.button("Approve Always"):
            exec_agent.add_trust_domain(domain)
            st.session_state["execution_approved"] = "always"
            st.success(f"{domain} added to trusted domains")
            st.rerun()
        if col_c.button("Reject"):
            st.session_state["execution_approved"] = None
            st.error("Execution rejected")

    # Run button — only show after approval
    approved = st.session_state.get("execution_approved")
    if approved or is_trusted:
        if st.button("Run Test", type="primary"):
            tc_id = st.session_state.get("current_tc_id", "TC01")
            script_to_run = st.session_state.get("edited_script") or st.session_state.get("current_script", "")
            with st.spinner("Executing test..."):
                try:
                    result_schema = exec_agent.run(
                        mode=settings.EXECUTION_MODE,
                        scripts={tc_id: script_to_run},
                        target_url=target_url,
                        approved=True,
                    )
                    st.session_state["execution_results"] = result_schema
                    result = result_schema.results[0] if result_schema.results else None
                    if result:
                        if result.status == "PASS":
                            st.success(f"\u2705 PASSED in {result.duration_ms:.0f}ms")
                        else:
                            st.error(f"\u274c FAILED: {result.error_message}")
                            # Self-healing panel
                            if "NoSuchElement" in result.error_message or "NoSuch" in result.error_message:
                                st.subheader("Self-Healing Agent")
                                with st.spinner("Attempting locator recovery..."):
                                    try:
                                        from agents.healing_agent import HealingAgent
                                        healing_agent = HealingAgent()
                                        healing = healing_agent.attempt_healing(
                                            result.error_message, target_url, tc_id=tc_id
                                        )
                                        st.session_state["healing_result"] = healing
                                        if healing.get("success"):
                                            st.success(f"Recovered selector: `{healing['recovered_selector']}`")
                                        else:
                                            st.warning("Could not recover selector automatically")
                                        with st.expander("Healing Attempt Details"):
                                            st.json(healing)
                                    except Exception as e:
                                        st.error(f"Healing failed: {e}")
                except Exception as e:
                    st.error(f"Execution failed: {e}")
