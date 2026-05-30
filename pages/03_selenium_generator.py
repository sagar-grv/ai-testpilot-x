"""Page 03 — Selenium Script Generator."""
import streamlit as st
from config import settings
from urllib.parse import urlparse

st.set_page_config(page_title="Selenium Generator | AI TestPilot X", page_icon="⚙️", layout="wide")

st.markdown("""
<h2 style='margin:0; font-size:26px; font-weight:700;'>⚙️ Selenium Script Generator</h2>
<p style='color:#718096; margin-top:4px;'>
    Generate Python Selenium scripts from test cases, then execute with human-in-the-loop approval.
</p>
""", unsafe_allow_html=True)
st.divider()

test_cases = st.session_state.get("generated_testcases", [])

if not test_cases:
    st.markdown("""
    <div style='background:#1E2130; border:1px solid #2E3250; border-radius:12px;
         padding:40px; text-align:center;'>
        <div style='font-size:48px;'>⚠️</div>
        <div style='font-size:18px; font-weight:600; margin-top:12px;'>No test cases loaded</div>
        <div style='color:#718096; margin-top:8px;'>
            Go to <strong>AI Test Generator</strong> first to generate test cases.
        </div>
    </div>""", unsafe_allow_html=True)
    st.stop()

# ── Controls ──────────────────────────────────────────────────────────────────
st.markdown("### 🎯 Configuration")
ccol1, ccol2 = st.columns(2)
with ccol1:
    tc_options = {tc.id: f"{tc.id} — {tc.title}" for tc in test_cases}
    selected_tc_id = st.selectbox("Select Test Case", options=list(tc_options.keys()),
                                  format_func=lambda x: tc_options[x])
with ccol2:
    target_url = st.text_input("Target URL", value="https://www.saucedemo.com",
                               placeholder="https://your-app.com")

col_fw, col_mode = st.columns(2)
with col_fw:
    st.radio("Framework", ["Selenium (Python)", "Playwright (coming soon)"],
             horizontal=True)
with col_mode:
    mode_color = {"LOCAL": "#48BB78", "MOCK": "#4299E1", "GRID": "#9F7AEA"}.get(settings.EXECUTION_MODE, "#A0AEC0")
    st.markdown(f"""
    <div style='background:#1E2130; border:1px solid #2E3250; border-radius:8px; padding:10px 14px; margin-top:28px;'>
        <span style='color:#A0AEC0; font-size:12px;'>EXECUTION MODE</span>
        <span style='background:{mode_color}22; color:{mode_color}; border:1px solid {mode_color}55;
            border-radius:20px; padding:3px 12px; font-size:13px; font-weight:700; margin-left:10px;'>
            {settings.EXECUTION_MODE}
        </span>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Generate ──────────────────────────────────────────────────────────────────
if st.button("⚡ Generate Selenium Script", type="primary", use_container_width=False):
    selected_tc = next(tc for tc in test_cases if tc.id == selected_tc_id)
    with st.spinner(f"Generating script for {selected_tc_id}..."):
        try:
            from agents.selenium_agent import SeleniumAgent
            agent = SeleniumAgent()
            script = agent.generate_for_tc(selected_tc, target_url)
            st.session_state["current_script"] = script
            st.session_state["current_tc_id"] = selected_tc_id
            st.session_state["target_url"] = target_url
            st.session_state["execution_approved"] = None
            st.success(f"✅ Script generated for {selected_tc_id}")
        except Exception as e:
            st.error(f"❌ Generation failed: {e}")

# ── Script Display ────────────────────────────────────────────────────────────
if "current_script" in st.session_state:
    st.divider()
    st.markdown("### 📄 Generated Script")

    script_header_col1, script_header_col2 = st.columns([3, 1])
    with script_header_col1:
        st.markdown(f"""
        <div style='background:#1E2130; border-radius:8px 8px 0 0; padding:10px 16px;
             border-bottom:1px solid #2E3250; display:flex; align-items:center; gap:8px;'>
            <span style='color:#68D391; font-size:12px;'>●</span>
            <span style='color:#FC8181; font-size:12px;'>●</span>
            <span style='color:#ECC94B; font-size:12px;'>●</span>
            <span style='color:#A0AEC0; font-size:12px; margin-left:8px;'>
                test_{st.session_state.get('current_tc_id', 'TC01')}.py — Python</span>
        </div>""", unsafe_allow_html=True)

    try:
        from streamlit_ace import st_ace
        edited_script = st_ace(
            value=st.session_state["current_script"],
            language="python", theme="monokai", height=280,
            key="script_editor", font_size=13,
            show_gutter=True, show_print_margin=False,
        )
    except ImportError:
        edited_script = st.text_area("Script", value=st.session_state["current_script"],
                                     height=280, key="script_editor_fallback",
                                     label_visibility="collapsed")
    st.session_state["edited_script"] = edited_script

    # ── HITL Gate ─────────────────────────────────────────────────────────────
    st.divider()
    st.markdown("### 🔐 Execution Gate")

    from agents.execution_agent import ExecutionAgent
    exec_agent = ExecutionAgent()
    domain = urlparse(target_url).netloc or target_url
    is_trusted = exec_agent.check_trust_domain(domain)

    if is_trusted:
        st.markdown(f"""
        <div style='background:#1A4731; border:1px solid #276749; border-radius:10px; padding:16px 20px;
             display:flex; align-items:center; gap:12px;'>
            <span style='font-size:24px;'>✅</span>
            <div>
                <div style='font-weight:600; color:#68D391;'>Trusted Domain</div>
                <div style='color:#9AE6B4; font-size:13px;'>{domain} — Auto-approved for execution</div>
            </div>
        </div>""", unsafe_allow_html=True)
        st.session_state["execution_approved"] = "auto"
    else:
        st.markdown(f"""
        <div style='background:#2D1B00; border:1px solid #744210; border-radius:10px; padding:16px 20px;
             display:flex; align-items:center; gap:12px;'>
            <span style='font-size:24px;'>⚠️</span>
            <div>
                <div style='font-weight:600; color:#F6AD55;'>Approval Required</div>
                <div style='color:#FBD38D; font-size:13px;'>Domain <strong>{domain}</strong> requires explicit approval before execution.</div>
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        gcol1, gcol2, gcol3 = st.columns(3)
        if gcol1.button("▶ Approve Once", use_container_width=True, type="primary"):
            st.session_state["execution_approved"] = "once"
            st.rerun()
        if gcol2.button("🔒 Approve Always", use_container_width=True):
            exec_agent.add_trust_domain(domain)
            st.session_state["execution_approved"] = "always"
            st.success(f"✅ {domain} added to trusted domains")
            st.rerun()
        if gcol3.button("✖ Reject", use_container_width=True):
            st.session_state["execution_approved"] = None
            st.error("Execution rejected.")

    # ── Run Test ──────────────────────────────────────────────────────────────
    approved = st.session_state.get("execution_approved")
    if approved or is_trusted:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("▶ Run Test", type="primary", use_container_width=False):
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
                            st.markdown(f"""
                            <div style='background:#1A4731; border:1px solid #276749; border-radius:12px;
                                 padding:20px 24px; display:flex; align-items:center; gap:16px;'>
                                <span style='font-size:36px;'>✅</span>
                                <div>
                                    <div style='font-size:20px; font-weight:700; color:#68D391;'>TEST PASSED</div>
                                    <div style='color:#9AE6B4; margin-top:4px;'>Duration: {result.duration_ms:.0f}ms</div>
                                </div>
                            </div>""", unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div style='background:#742A2A; border:1px solid #C53030; border-radius:12px;
                                 padding:20px 24px;'>
                                <div style='display:flex; align-items:center; gap:12px;'>
                                    <span style='font-size:32px;'>❌</span>
                                    <div>
                                        <div style='font-size:18px; font-weight:700; color:#FC8181;'>TEST FAILED</div>
                                        <div style='color:#FEB2B2; font-size:13px; margin-top:4px;'>{result.error_message[:120]}...</div>
                                    </div>
                                </div>
                            </div>""", unsafe_allow_html=True)

                            # Self-healing
                            if "NoSuchElement" in result.error_message or "NoSuch" in result.error_message:
                                st.markdown("<br>", unsafe_allow_html=True)
                                st.markdown("""
                                <div style='background:#1A202C; border:1px solid #4A5568; border-radius:10px; padding:16px 20px;'>
                                    <div style='font-weight:600; font-size:15px;'>🔧 Self-Healing Agent</div>
                                    <div style='color:#718096; font-size:13px; margin-top:4px;'>Attempting automatic locator recovery...</div>
                                </div>""", unsafe_allow_html=True)
                                with st.spinner("Trying locator hierarchy: ID → Name → data-testid → CSS → XPath..."):
                                    try:
                                        from agents.healing_agent import HealingAgent
                                        healing = HealingAgent().attempt_healing(result.error_message, target_url, tc_id=tc_id)
                                        st.session_state["healing_result"] = healing
                                        if healing.get("success"):
                                            st.success(f"🔧 Recovered selector: `{healing['recovered_selector']}`")
                                        else:
                                            st.warning("Could not auto-recover. Manual fix required.")
                                        with st.expander("View Healing Details"):
                                            st.json(healing)
                                    except Exception as he:
                                        st.error(f"Healing failed: {he}")
                except Exception as e:
                    st.error(f"❌ Execution failed: {e}")
