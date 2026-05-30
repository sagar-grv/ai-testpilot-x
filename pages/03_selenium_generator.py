"""Page 03 — Selenium Script Generator with HITL gate."""
import streamlit as st
from urllib.parse import urlparse
from config import settings

st.set_page_config(page_title="Selenium Generator | AI TestPilot X", page_icon="⚙️", layout="wide")

# ── Inject shared CSS + sidebar ───────────────────────────────────────────────
from pages._css import inject_css, sidebar_branding
inject_css()
sidebar_branding()



st.markdown("""
<h1 class="tp-page-title">⚙️ Selenium Script Generator</h1>
<p class="tp-page-subtitle">
    Generate Python Selenium scripts from test cases and execute with human-in-the-loop approval.
</p>
""", unsafe_allow_html=True)
st.divider()

# ── Empty state ───────────────────────────────────────────────────────────────
test_cases = st.session_state.get("generated_testcases", [])
if not test_cases:
    st.markdown("""
    <div style="background:#0F1117; border:1px dashed #1E2337; border-radius:14px;
                padding:56px 32px; text-align:center;">
        <div style="font-size:52px; margin-bottom:14px;">⚠️</div>
        <div style="font-size:20px; font-weight:700; color:#F0F4FF; margin-bottom:8px;">
            No test cases loaded</div>
        <div style="font-size:14px; color:#475569; max-width:400px; margin:0 auto 20px auto;">
            Go to <strong style="color:#6C63FF;">AI Test Generator</strong> first
            to generate test cases from a user story.
        </div>
    </div>""", unsafe_allow_html=True)
    st.stop()

# ── Configuration ─────────────────────────────────────────────────────────────
st.markdown('<div class="tp-section-title">Configuration</div>', unsafe_allow_html=True)

cfg_c1, cfg_c2 = st.columns(2)
with cfg_c1:
    tc_options = {tc.id: f"{tc.id} — {tc.title}" for tc in test_cases}
    selected_id = st.selectbox(
        "Test Case", options=list(tc_options.keys()),
        format_func=lambda x: tc_options[x]
    )
with cfg_c2:
    target_url = st.text_input("Target URL", value="https://www.saucedemo.com",
                               placeholder="https://your-app.com")

fw_col, mode_col = st.columns(2)
with fw_col:
    st.radio("Framework", ["Selenium (Python)", "Playwright (coming soon)"],
             horizontal=True, label_visibility="collapsed")
with mode_col:
    MODE_COLORS = {"LOCAL": "#22c55e", "MOCK": "#3b82f6", "GRID": "#a855f7"}
    mc = MODE_COLORS.get(settings.EXECUTION_MODE, "#64748B")
    st.markdown(f"""
    <div style="background:#0F1117; border:1px solid #1E2337; border-radius:8px;
                padding:12px 16px; margin-top:4px; display:flex; align-items:center; gap:10px;">
        <span style="font-size:11px; color:#64748B; font-weight:700;
                     text-transform:uppercase; letter-spacing:0.08em;">Execution</span>
        <span style="background:{mc}22; color:{mc}; border:1px solid {mc}44;
                     border-radius:20px; padding:3px 12px; font-size:12px; font-weight:700;">
            {settings.EXECUTION_MODE}
        </span>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Generate button ───────────────────────────────────────────────────────────
gen_btn = st.button("⚡ Generate Selenium Script", type="primary")

if gen_btn:
    selected_tc = next(tc for tc in test_cases if tc.id == selected_id)
    with st.spinner(f"Generating Selenium script for {selected_id}..."):
        try:
            from agents.selenium_agent import SeleniumAgent
            script = SeleniumAgent().generate_for_tc(selected_tc, target_url)
            st.session_state.update({
                "current_script": script,
                "current_tc_id": selected_id,
                "target_url": target_url,
                "execution_approved": None,
            })
            st.rerun()
        except Exception as e:
            st.error(f"Generation failed: {e}")

# ── Script display ────────────────────────────────────────────────────────────
if "current_script" in st.session_state:
    st.divider()
    st.markdown('<div class="tp-section-title">Generated Script</div>', unsafe_allow_html=True)

    # Window chrome
    tc_id = st.session_state.get("current_tc_id", "TC01")
    st.markdown(f"""
    <div style="background:#161B2C; border:1px solid #1E2337;
                border-bottom:none; border-radius:10px 10px 0 0;
                padding:10px 16px; display:flex; align-items:center; gap:8px;">
        <span style="width:11px;height:11px;background:#ef4444;border-radius:50%;display:inline-block;"></span>
        <span style="width:11px;height:11px;background:#fbbf24;border-radius:50%;display:inline-block;"></span>
        <span style="width:11px;height:11px;background:#22c55e;border-radius:50%;display:inline-block;"></span>
        <span style="color:#475569; font-size:12px; margin-left:8px; font-family:monospace;">
            test_{tc_id}.py</span>
    </div>""", unsafe_allow_html=True)

    try:
        from streamlit_ace import st_ace
        edited_script = st_ace(
            value=st.session_state["current_script"],
            language="python", theme="monokai", height=280,
            key="script_ace", font_size=13, show_gutter=True,
            show_print_margin=False, wrap=False,
        )
    except ImportError:
        edited_script = st.text_area(
            "script", value=st.session_state["current_script"],
            height=280, label_visibility="collapsed", key="script_ta"
        )
    st.session_state["edited_script"] = edited_script

    # ── HITL Gate ─────────────────────────────────────────────────────────────
    st.divider()
    st.markdown('<div class="tp-section-title">Execution Gate</div>', unsafe_allow_html=True)

    from agents.execution_agent import ExecutionAgent
    exec_agent = ExecutionAgent()
    domain = urlparse(st.session_state.get("target_url", target_url)).netloc or target_url
    is_trusted = exec_agent.check_trust_domain(domain)

    if is_trusted:
        st.markdown(f"""
        <div style="background:#052e16; border:1px solid #16a34a44;
                    border-radius:12px; padding:18px 22px;
                    display:flex; align-items:center; gap:14px; margin-bottom:16px;">
            <span style="font-size:28px;">✅</span>
            <div>
                <div style="font-weight:700; color:#4ade80; font-size:14px;">
                    Trusted Domain</div>
                <div style="color:#86efac; font-size:13px; margin-top:2px;">
                    <code style="background:#0F1117; padding:1px 6px; border-radius:4px;">{domain}</code>
                    is in your trusted domains list — auto-approved.
                </div>
            </div>
        </div>""", unsafe_allow_html=True)
        st.session_state["execution_approved"] = "auto"
    else:
        st.markdown(f"""
        <div style="background:#431407; border:1px solid #f9731644;
                    border-radius:12px; padding:18px 22px; margin-bottom:16px;">
            <div style="display:flex; align-items:center; gap:14px;">
                <span style="font-size:28px;">🔐</span>
                <div>
                    <div style="font-weight:700; color:#fb923c; font-size:14px;">
                        Approval Required</div>
                    <div style="color:#fdba74; font-size:13px; margin-top:2px;">
                        <code style="background:#0F1117; padding:1px 6px; border-radius:4px;">{domain}</code>
                        requires explicit approval before test execution.
                    </div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        a1, a2, a3 = st.columns(3)
        if a1.button("▶ Approve Once", type="primary", use_container_width=True):
            st.session_state["execution_approved"] = "once"
            st.rerun()
        if a2.button("🔒 Approve Always (Trust Domain)", use_container_width=True):
            exec_agent.add_trust_domain(domain)
            st.session_state["execution_approved"] = "always"
            st.success(f"✅ {domain} added to trusted domains.")
            st.rerun()
        if a3.button("✖ Reject", use_container_width=True):
            st.session_state["execution_approved"] = None
            st.error("Execution rejected.")

    # ── Run ───────────────────────────────────────────────────────────────────
    approved = st.session_state.get("execution_approved")
    if approved or is_trusted:
        st.markdown("<br>", unsafe_allow_html=True)
        run_btn = st.button("▶ Run Test Now", type="primary")

        if run_btn:
            script_run = st.session_state.get("edited_script") or st.session_state.get("current_script", "")
            with st.spinner(f"Executing test in {settings.EXECUTION_MODE} mode..."):
                try:
                    result_schema = exec_agent.run(
                        mode=settings.EXECUTION_MODE,
                        scripts={tc_id: script_run},
                        target_url=st.session_state.get("target_url", target_url),
                        approved=True,
                    )
                    st.session_state["execution_results"] = result_schema
                    result = result_schema.results[0] if result_schema.results else None

                    if result:
                        if result.status == "PASS":
                            st.markdown(f"""
                            <div style="background:#052e16; border:1px solid #16a34a55;
                                        border-radius:14px; padding:24px 28px;
                                        display:flex; align-items:center; gap:18px; margin:16px 0;">
                                <span style="font-size:44px;">✅</span>
                                <div>
                                    <div style="font-size:22px; font-weight:900; color:#4ade80;">
                                        TEST PASSED</div>
                                    <div style="color:#86efac; font-size:13px; margin-top:4px;">
                                        Completed in {result.duration_ms:.0f} ms
                                        &nbsp;·&nbsp; Mode: {settings.EXECUTION_MODE}
                                    </div>
                                </div>
                            </div>""", unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div style="background:#450a0a; border:1px solid #ef444455;
                                        border-radius:14px; padding:24px 28px; margin:16px 0;">
                                <div style="display:flex; align-items:flex-start; gap:16px;">
                                    <span style="font-size:36px; flex-shrink:0;">❌</span>
                                    <div>
                                        <div style="font-size:20px; font-weight:800; color:#f87171;">
                                            TEST FAILED</div>
                                        <div style="color:#fca5a5; font-size:13px; margin-top:6px;
                                                    font-family:monospace; background:#0F1117;
                                                    padding:8px 12px; border-radius:6px; margin-top:10px;">
                                            {(result.error_message or "Unknown error")[:160]}
                                        </div>
                                    </div>
                                </div>
                            </div>""", unsafe_allow_html=True)

                            if any(kw in (result.error_message or "") for kw in
                                   ["NoSuchElement", "ElementNotFound", "NoSuch"]):
                                st.markdown('<div class="tp-section-title">Self-Healing Agent</div>',
                                            unsafe_allow_html=True)
                                st.markdown("""
                                <div class="tp-card-sm" style="margin-bottom:12px;">
                                    <div style="font-size:13px; color:#94A3B8;">
                                        🔧 Attempting automatic locator recovery using hierarchy:
                                        <code>id → name → data-testid → data-cy → css → xpath → AI</code>
                                    </div>
                                </div>""", unsafe_allow_html=True)
                                with st.spinner("Trying locator hierarchy..."):
                                    try:
                                        from agents.healing_agent import HealingAgent
                                        healing = HealingAgent().attempt_healing(
                                            result.error_message, target_url, tc_id=tc_id
                                        )
                                        st.session_state["healing_result"] = healing
                                        if healing.get("success"):
                                            st.success(f"🔧 Recovered: `{healing['recovered_selector']}`")
                                        else:
                                            st.warning("Auto-recovery failed. Manual fix required.")
                                        with st.expander("View healing attempt details"):
                                            tried = healing.get("tried_locators", [])
                                            for attempt in tried:
                                                icon3 = "✅" if attempt.get("suggestion") else "❌"
                                                st.markdown(
                                                    f"{icon3} **{attempt['type']}**: "
                                                    f"`{attempt.get('suggestion') or 'no suggestion'}`"
                                                )
                                    except Exception as he:
                                        st.error(f"Healing error: {he}")
                except Exception as e:
                    st.error(f"Execution failed: {e}")
