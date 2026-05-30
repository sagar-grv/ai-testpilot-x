"""Page 04 — API Test Studio: generate and optionally execute HTTP tests."""
import streamlit as st
import json
import asyncio
import pandas as pd

st.set_page_config(page_title="API Tester | AI TestPilot X", page_icon="🌐", layout="wide")

st.markdown("""
<h2 style='margin:0; font-size:26px; font-weight:700;'>🌐 API Test Studio</h2>
<p style='color:#718096; margin-top:4px;'>Generate HTTP test suites and optionally run them against live endpoints.</p>
""", unsafe_allow_html=True)
st.divider()

requirement = st.session_state.get("requirement_context")

# Mode toggle
mode = st.radio("Mode", ["Mock (Generate Only)", "Live (Execute)"], horizontal=True)
live_mode = mode.startswith("Live")

if live_mode:
    base_url = st.text_input("Base URL", placeholder="https://api.example.com")
else:
    base_url = ""

# Module selector
if requirement and hasattr(requirement, "modules"):
    module_options = requirement.modules
else:
    module_options = ["Login", "Cart", "Checkout", "Payment"]
selected_module = st.selectbox("Module", module_options)

# Generate
if st.button("Generate API Tests", type="primary"):
    with st.spinner(f"Generating API test suite for {selected_module}..."):
        try:
            from agents.api_agent import APIAgent
            agent = APIAgent()
            suite = agent.run_for_module(selected_module, requirement)
            st.session_state["api_suite"] = suite
            st.session_state["api_module"] = selected_module
            st.success(f"Generated {len(suite)} test cases for {selected_module}")
        except Exception as e:
            st.error(f"Generation failed: {e}")

# Display suite
suite = st.session_state.get("api_suite", [])
if suite:
    st.subheader("Generated Test Suite")
    df = pd.DataFrame([t.model_dump() for t in suite])
    display_cols = [c for c in ["method", "endpoint", "expected_status", "assertion"] if c in df.columns]
    st.dataframe(df[display_cols], use_container_width=True)

    # API Risk Score
    module_lower = selected_module.lower()
    payment_kw = ["pay", "checkout", "billing", "card", "stripe"]
    auth_kw = ["login", "auth", "token", "password", "session"]
    if any(k in module_lower for k in payment_kw):
        risk, color = "CRITICAL", "🔴"
    elif any(k in module_lower for k in auth_kw):
        risk, color = "HIGH", "🟠"
    else:
        risk, color = "MEDIUM", "🟡"
    st.metric(f"{color} API Risk Score", risk)

    # Live execution
    if live_mode and base_url:
        if st.button("Run Live Tests", type="primary"):
            from execution.runners.api_runner import run_api_test_sync
            results = []
            with st.spinner("Executing API tests..."):
                for test in suite:
                    result = run_api_test_sync(base_url, test)
                    results.append(result)
            st.session_state["api_results"] = results
            passed = sum(1 for r in results if r.passed)
            col1, col2, col3 = st.columns(3)
            col1.metric("Total", len(results))
            col2.metric("Passed", passed)
            col3.metric("Failed", len(results) - passed)
            rdf = pd.DataFrame([r.model_dump() for r in results])
            show_cols = [c for c in ["method", "endpoint", "expected_status", "actual_status", "passed", "response_time_ms"] if c in rdf.columns]
            st.dataframe(rdf[show_cols], use_container_width=True)

    # Export
    st.divider()
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        if st.button("Export cURL Commands"):
            curls = []
            for t in suite:
                cmd = f"curl -X {t.method} '{base_url or 'https://api.example.com'}{t.endpoint}'"
                if t.body:
                    cmd += f" -H 'Content-Type: application/json' -d '{json.dumps(t.body)}'"
                curls.append(cmd)
            st.code("\n".join(curls), language="bash")
    with col_e2:
        if st.button("Export Postman Collection"):
            collection = {
                "info": {"name": f"AI TestPilot - {selected_module}", "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"},
                "item": [{
                    "name": f"{t.method} {t.endpoint}",
                    "request": {
                        "method": t.method,
                        "url": f"{{{{base_url}}}}{t.endpoint}",
                        "body": {"mode": "raw", "raw": json.dumps(t.body)} if t.body else {}
                    }
                } for t in suite]
            }
            st.download_button("Download postman_collection.json", json.dumps(collection, indent=2),
                               "postman_collection.json", "application/json")
