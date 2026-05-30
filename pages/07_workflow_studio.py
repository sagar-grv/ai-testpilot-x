"""Page 07 — Workflow Studio."""
import streamlit as st
from core.event_bus import bus

st.set_page_config(page_title="Workflow Studio | AI TestPilot X", page_icon="🔀", layout="wide")

st.markdown("""
<h2 style='margin:0; font-size:26px; font-weight:700;'>🔀 Workflow Studio</h2>
<p style='color:#718096; margin-top:4px;'>
    Live view of the LangGraph agent pipeline — see which agents have run and inspect their outputs.
</p>
""", unsafe_allow_html=True)
st.divider()

event_history = bus.get_history()
completed = {e["type"] for e in event_history}

# ── Pipeline Status ───────────────────────────────────────────────────────────
st.markdown("### 🔄 Agent Pipeline Status")

PIPELINE = [
    ("🔍", "RequirementAgent", "REQUIREMENT_ANALYZED", "Parses user story into modules & risk areas"),
    ("📝", "TestCaseAgent", "TESTCASES_GENERATED", "Generates structured test cases with RAG"),
    ("✅", "VerificationAgent", "VERIFICATION_COMPLETE", "Checks coverage and edge case gaps"),
    ("⚙️", "SeleniumAgent", None, "Generates Python Selenium scripts"),
    ("🌐", "APIAgent", None, "Generates HTTP API test suites"),
    ("👤", "HITL Gate", "EXECUTION_APPROVED", "Human approval before execution"),
    ("▶️", "ExecutionAgent", "EXECUTION_COMPLETE", "Runs tests (LOCAL/MOCK/GRID)"),
    ("🐛", "BugAgent", "BUG_ANALYZED", "Analyzes failures with RAG correlation"),
    ("🔧", "HealingAgent", "HEALING_COMPLETE", "Auto-recovers broken selectors"),
    ("📊", "ReportAgent", "REPORT_GENERATED", "Generates GO/NO GO release decision"),
]

# Render pipeline as cards
cols = st.columns(5)
for i, (icon, name, event_key, desc) in enumerate(PIPELINE):
    done = event_key and event_key in completed
    col = cols[i % 5]
    with col:
        bg = "#1A4731" if done else "#1E2130"
        border = "#276749" if done else "#2E3250"
        status_icon = "✅" if done else "⏳"
        status_text = "Complete" if done else "Pending"
        status_color = "#68D391" if done else "#718096"
        st.markdown(f"""
        <div style='background:{bg}; border:1px solid {border}; border-radius:10px;
             padding:14px 12px; margin-bottom:8px; text-align:center;'>
            <div style='font-size:28px;'>{icon}</div>
            <div style='font-weight:600; font-size:12px; margin-top:6px; color:#FAFAFA;'>{name}</div>
            <div style='color:{status_color}; font-size:11px; margin-top:4px;'>{status_icon} {status_text}</div>
        </div>""", unsafe_allow_html=True)

# Progress bar
completed_count = sum(1 for _, _, ev, _ in PIPELINE if ev and ev in completed)
total_with_events = sum(1 for _, _, ev, _ in PIPELINE if ev)
progress_pct = completed_count / total_with_events if total_with_events > 0 else 0

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f"**Pipeline Progress:** {completed_count}/{total_with_events} stages complete")
st.progress(progress_pct)

# ── Agent Flow Diagram (text) ─────────────────────────────────────────────────
st.divider()
st.markdown("### 🗺 Agent Flow")

try:
    from streamlit_agraph import agraph, Node, Edge, Config

    EVENT_MAP = {name: ev for _, name, ev, _ in PIPELINE}

    def node_color(name):
        ev = EVENT_MAP.get(name)
        if name in ("HITL Gate",):
            return "#ECC94B" if ev and ev in completed else "#744210"
        if ev and ev in completed:
            return "#276749"
        return "#2D3748"

    nodes = []
    for icon, name, ev, _ in PIPELINE:
        color = node_color(name)
        label = f"{icon} {name}"
        nodes.append(Node(id=name, label=label, color=color, size=18,
                          font={"size": 11, "color": "#FAFAFA"}))

    edges = [
        Edge("RequirementAgent", "TestCaseAgent"),
        Edge("TestCaseAgent", "VerificationAgent"),
        Edge("VerificationAgent", "SeleniumAgent"),
        Edge("VerificationAgent", "APIAgent"),
        Edge("SeleniumAgent", "HITL Gate"),
        Edge("APIAgent", "HITL Gate"),
        Edge("HITL Gate", "ExecutionAgent"),
        Edge("ExecutionAgent", "BugAgent", label="failures"),
        Edge("ExecutionAgent", "ReportAgent", label="all pass"),
        Edge("BugAgent", "HealingAgent"),
        Edge("BugAgent", "ReportAgent"),
        Edge("HealingAgent", "ReportAgent"),
    ]

    config = Config(
        width=900, height=380, directed=True, physics=False,
        nodeHighlightBehavior=True, highlightColor="#6C63FF",
        backgroundColor="#0E1117", node={"labelProperty": "label"},
        link={"labelProperty": "label", "renderLabel": True, "color": "#4A5568"}
    )
    agraph(nodes=nodes, edges=edges, config=config)
except ImportError:
    st.markdown("""
    <div style='background:#1E2130; border:1px solid #2E3250; border-radius:10px; padding:20px; font-family:monospace; font-size:13px; color:#A0AEC0;'>
    RequirementAgent → TestCaseAgent → VerificationAgent<br>
    &nbsp;&nbsp;&nbsp;&nbsp;↓ (parallel)<br>
    SeleniumAgent + APIAgent → HITL Gate → ExecutionAgent<br>
    &nbsp;&nbsp;&nbsp;&nbsp;↓ (on failures)<br>
    BugAgent → HealingAgent → ReportAgent
    </div>""", unsafe_allow_html=True)

# ── GlobalState Inspector ─────────────────────────────────────────────────────
st.divider()
st.markdown("### 🔎 GlobalState Inspector")
st.caption("Live view of what each agent has produced in the current session.")

STATE_MAP = [
    ("requirement_context", "🔍 Requirement Analysis"),
    ("generated_testcases", "📝 Generated Test Cases"),
    ("verification_report", "✅ Verification Report"),
    ("selenium_scripts", "⚙️ Selenium Scripts"),
    ("api_test_suite", "🌐 API Test Suite"),
    ("execution_results", "▶️ Execution Results"),
    ("bugs", "🐛 Bugs"),
    ("bug_clusters", "🗂 Bug Clusters"),
    ("healing_results", "🔧 Healing Results"),
    ("report", "📊 Report"),
]

gcol1, gcol2 = st.columns(2)
for i, (key, label) in enumerate(STATE_MAP):
    value = st.session_state.get(key)
    col = gcol1 if i % 2 == 0 else gcol2
    with col:
        if value is not None:
            with st.expander(f"✅ {label}"):
                if hasattr(value, "model_dump"):
                    st.json(value.model_dump())
                elif isinstance(value, list) and value:
                    first = value[0]
                    st.json(first.model_dump() if hasattr(first, "model_dump") else first)
                    if len(value) > 1:
                        st.caption(f"... and {len(value)-1} more items")
                elif isinstance(value, dict):
                    st.json(value)
                else:
                    st.write(value)
        else:
            st.markdown(f"""
            <div style='background:#1E2130; border:1px dashed #2E3250; border-radius:8px;
                 padding:10px 14px; color:#4A5568; font-size:13px; margin-bottom:8px;'>
                ⏳ {label} — not yet computed
            </div>""", unsafe_allow_html=True)

# ── Controls ──────────────────────────────────────────────────────────────────
st.divider()
ctrl1, ctrl2 = st.columns(2)
if ctrl1.button("💾 Save Checkpoint", use_container_width=True):
    checkpoint = {k: st.session_state.get(k) for k, _ in STATE_MAP}
    st.session_state["checkpoint"] = checkpoint
    st.success("Checkpoint saved to session state.")
if ctrl2.button("🗑 Clear Event History", use_container_width=True):
    bus.clear_history()
    st.success("Event history cleared.")
    st.rerun()
