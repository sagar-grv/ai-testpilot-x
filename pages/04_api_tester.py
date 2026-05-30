"""Page 04 — API Test Studio."""

import streamlit as st
import json
import pandas as pd

st.set_page_config(
    page_title="API Tester | AI TestPilot X", page_icon="🌐", layout="wide"
)

# ── Inject shared CSS + sidebar ───────────────────────────────────────────────
from pages._css import inject_css, sidebar_branding

inject_css()
sidebar_branding()


st.markdown(
    """
<h1 class="tp-page-title">🌐 API Test Studio</h1>
<p class="tp-page-subtitle">
    Generate HTTP test suites for any module and optionally execute them against live endpoints.
</p>
""",
    unsafe_allow_html=True,
)
st.divider()

# ── Mode + Config ─────────────────────────────────────────────────────────────
st.markdown('<div class="tp-section-title">Configuration</div>', unsafe_allow_html=True)

c_mode, c_url = st.columns([1, 2])
with c_mode:
    mode = st.radio(
        "Execution Mode",
        ["Mock (Generate Only)", "Live (Execute)"],
        horizontal=False,
        label_visibility="collapsed",
    )
    live_mode = mode.startswith("Live")
with c_url:
    base_url = ""
    if live_mode:
        base_url = st.text_input("Base URL", placeholder="https://api.example.com")
    else:
        st.markdown(
            """
        <div class="tp-card-sm" style="margin-top:4px;">
            <div style="font-size:12px; color:#64748B;">
                <strong style="color:#3b82f6;">Mock mode</strong> — generates test definitions
                without hitting any real endpoint. Switch to Live to execute.
            </div>
        </div>""",
            unsafe_allow_html=True,
        )

req = st.session_state.get("requirement_context")
c_mod, c_btn = st.columns([2, 1])
with c_mod:
    module_options = (
        req.modules
        if req and hasattr(req, "modules")
        else ["Login", "Cart", "Checkout", "Payment"]
    )
    selected_module = st.selectbox("Module", module_options)
with c_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    gen_btn = st.button(
        "🔄 Generate API Tests", type="primary", use_container_width=True
    )

if gen_btn:
    with st.spinner(f"Generating API test suite for {selected_module}..."):
        try:
            from agents.api_agent import APIAgent

            suite = APIAgent().run_for_module(selected_module, req)
            st.session_state["api_suite"] = suite
            st.session_state["api_module"] = selected_module
            st.rerun()
        except Exception as e:
            st.error(f"Generation failed: {e}")

# ── Results ───────────────────────────────────────────────────────────────────
suite = st.session_state.get("api_suite", [])
if suite:
    st.divider()

    # API Risk Score — prominent card
    module_lower = selected_module.lower()
    if any(k in module_lower for k in ["pay", "checkout", "billing", "card", "stripe"]):
        risk, risk_bg, risk_border, risk_color = (
            "CRITICAL",
            "#450a0a",
            "#ef4444",
            "#f87171",
        )
    elif any(
        k in module_lower for k in ["login", "auth", "token", "password", "session"]
    ):
        risk, risk_bg, risk_border, risk_color = "HIGH", "#431407", "#f97316", "#fb923c"
    else:
        risk, risk_bg, risk_border, risk_color = (
            "MEDIUM",
            "#422006",
            "#f59e0b",
            "#fbbf24",
        )

    risk_col, count_col = st.columns([1, 3])
    with risk_col:
        st.markdown(
            f"""
        <div style="background:{risk_bg}; border:1px solid {risk_border}44;
                    border-radius:12px; padding:18px 20px; text-align:center;">
            <div style="font-size:10px; color:{risk_color}88; font-weight:700;
                        text-transform:uppercase; letter-spacing:0.1em; margin-bottom:6px;">
                API Risk Score
            </div>
            <div style="font-size:28px; font-weight:900; color:{risk_color};">{risk}</div>
            <div style="font-size:11px; color:{risk_color}88; margin-top:4px;">{selected_module}</div>
        </div>""",
            unsafe_allow_html=True,
        )
    with count_col:
        METHOD_COLORS = {
            "GET": "#3b82f6",
            "POST": "#22c55e",
            "PUT": "#f59e0b",
            "DELETE": "#ef4444",
            "PATCH": "#a855f7",
        }
        method_counts = {}
        for t in suite:
            method_counts[t.method] = method_counts.get(t.method, 0) + 1

        chips = " ".join(
            f'<span style="background:{METHOD_COLORS.get(m,"#64748B")}22; color:{METHOD_COLORS.get(m,"#94A3B8")}; border:1px solid {METHOD_COLORS.get(m,"#64748B")}44; border-radius:6px; padding:4px 12px; font-size:12px; font-weight:700;">{v}× {m}</span>'
            for m, v in method_counts.items()
        )
        st.markdown(
            f"""
        <div class="tp-card" style="height:100%; display:flex; flex-direction:column; justify-content:center;">
            <div style="font-size:20px; font-weight:800; color:#F0F4FF; margin-bottom:10px;">
                {len(suite)} Test Cases Generated
            </div>
            <div style="display:flex; flex-wrap:wrap; gap:8px;">{chips}</div>
        </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Test suite table
    df = pd.DataFrame(
        [
            {
                "Method": t.method,
                "Endpoint": t.endpoint,
                "Expected Status": t.expected_status,
                "Assertion": t.assertion[:60]
                + ("..." if len(t.assertion) > 60 else ""),
            }
            for t in suite
        ]
    )
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Live execution
    if live_mode and base_url:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("▶ Run Live Tests", type="primary"):
            from execution.runners.api_runner import run_api_test_sync

            results, prog = [], st.progress(0, text="Running tests...")
            for i, test in enumerate(suite):
                results.append(run_api_test_sync(base_url, test))
                prog.progress(
                    (i + 1) / len(suite), text=f"Running {i+1}/{len(suite)}..."
                )
            prog.empty()
            st.session_state["api_results"] = results
            passed = sum(1 for r in results if r.passed)
            rc1, rc2, rc3 = st.columns(3)
            rc1.metric("Total", len(results))
            rc2.metric("✅ Passed", passed)
            rc3.metric("❌ Failed", len(results) - passed)
            rdf = pd.DataFrame(
                [
                    {
                        "Method": r.method,
                        "Endpoint": r.endpoint,
                        "Expected": r.expected_status,
                        "Actual": r.actual_status,
                        "Time (ms)": f"{r.response_time_ms:.0f}",
                        "Result": "✅ Pass" if r.passed else "❌ Fail",
                    }
                    for r in results
                ]
            )
            st.dataframe(rdf, use_container_width=True, hide_index=True)

    # Export section
    st.divider()
    st.markdown('<div class="tp-section-title">Export</div>', unsafe_allow_html=True)
    exp1, exp2 = st.columns(2)

    with exp1:
        st.markdown(
            """
        <div class="tp-card-sm" style="margin-bottom:10px;">
            <div style="font-weight:700; font-size:13px; color:#F0F4FF; margin-bottom:4px;">
                🖥 cURL Commands</div>
            <div style="font-size:12px; color:#64748B;">
                Ready-to-run shell commands for each test case</div>
        </div>""",
            unsafe_allow_html=True,
        )
        if st.button("Export cURL", use_container_width=True):
            curls = []
            for t in suite:
                cmd = f"curl -X {t.method} '{base_url or 'https://api.example.com'}{t.endpoint}'"
                if t.body:
                    cmd += f" \\\n  -H 'Content-Type: application/json' \\\n  -d '{json.dumps(t.body)}'"
                curls.append(cmd)
            st.code("\n\n".join(curls), language="bash")

    with exp2:
        st.markdown(
            """
        <div class="tp-card-sm" style="margin-bottom:10px;">
            <div style="font-weight:700; font-size:13px; color:#F0F4FF; margin-bottom:4px;">
                📮 Postman Collection</div>
            <div style="font-size:12px; color:#64748B;">
                Import directly into Postman</div>
        </div>""",
            unsafe_allow_html=True,
        )
        collection = {
            "info": {
                "name": f"AI TestPilot — {selected_module}",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            },
            "item": [
                {
                    "name": f"{t.method} {t.endpoint}",
                    "request": {
                        "method": t.method,
                        "url": f"{{{{base_url}}}}{t.endpoint}",
                        "body": (
                            {"mode": "raw", "raw": json.dumps(t.body)} if t.body else {}
                        ),
                    },
                }
                for t in suite
            ],
        }
        st.download_button(
            "⬇ Download postman_collection.json",
            json.dumps(collection, indent=2),
            "postman_collection.json",
            "application/json",
            use_container_width=True,
        )

else:
    st.markdown(
        """
    <div style="background:#0F1117; border:1px dashed #1E2337; border-radius:14px;
                padding:48px 32px; text-align:center;">
        <div style="font-size:48px; margin-bottom:12px;">🌐</div>
        <div style="font-size:18px; font-weight:700; color:#F0F4FF; margin-bottom:8px;">
            No API tests generated yet</div>
        <div style="font-size:13px; color:#475569;">
            Select a module above and click <strong style="color:#6C63FF;">Generate API Tests</strong>.
        </div>
    </div>""",
        unsafe_allow_html=True,
    )
