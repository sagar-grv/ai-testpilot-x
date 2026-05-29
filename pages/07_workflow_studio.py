"""Page 07 — Workflow Studio: live LangGraph agent graph + GlobalState inspector."""
import streamlit as st

st.set_page_config(page_title="Workflow Studio | AI TestPilot X", layout="wide")
st.title("Workflow Studio")

from core.event_bus import bus

event_history = bus.get_history()
completed = {e["type"] for e in event_history}

# Build graph visualization
try:
    from streamlit_agraph import agraph, Node, Edge, Config

    NODE_EVENTS = {
        "START": None,
        "RequirementAgent": "REQUIREMENT_ANALYZED",
        "TestCaseAgent": "TESTCASES_GENERATED",
        "VerificationAgent": "VERIFICATION_COMPLETE",
        "SeleniumAgent": None,
        "APIAgent": None,
        "HITL Gate": "EXECUTION_APPROVED",
        "ExecutionAgent": "EXECUTION_COMPLETE",
        "BugAgent": "BUG_ANALYZED",
        "HealingAgent": "HEALING_COMPLETE",
        "ReportAgent": "REPORT_GENERATED",
        "END": None,
    }

    def node_color(name, event):
        if name in ("START", "END"):
            return "#888888"
        if event and event in completed:
            return "#00cc44"
        return "#cccccc"

    nodes = []
    for name, event in NODE_EVENTS.items():
        color = node_color(name, event)
        label = f"✓ {name}" if event and event in completed else name
        nodes.append(Node(id=name, label=label, color=color, size=25, font={"size": 12}))

    edges = [
        Edge("START", "RequirementAgent"),
        Edge("RequirementAgent", "TestCaseAgent"),
        Edge("TestCaseAgent", "VerificationAgent"),
        Edge("VerificationAgent", "SeleniumAgent"),
        Edge("VerificationAgent", "APIAgent"),
        Edge("SeleniumAgent", "HITL Gate"),
        Edge("APIAgent", "HITL Gate"),
        Edge("HITL Gate", "ExecutionAgent"),
        Edge("ExecutionAgent", "BugAgent", label="failures"),
        Edge("ExecutionAgent", "ReportAgent", label="all pass"),
        Edge("BugAgent", "HealingAgent", label="NoSuchElement"),
        Edge("BugAgent", "ReportAgent"),
        Edge("HealingAgent", "ReportAgent"),
        Edge("ReportAgent", "END"),
    ]

    config = Config(width=900, height=500, directed=True, physics=False,
                    nodeHighlightBehavior=True, highlightColor="#F7A7A6")
    agraph(nodes=nodes, edges=edges, config=config)

except ImportError:
    st.info("Install `streamlit-agraph` for interactive workflow graph.")
    # Fallback: text representation
    st.code("""
START → RequirementAgent → TestCaseAgent → VerificationAgent
  → [SeleniumAgent + APIAgent] → HITL Gate → ExecutionAgent
  → BugAgent → HealingAgent → ReportAgent → END
    """)

# Agent Activity Feed
st.divider()
st.subheader("Agent Activity Feed")
if event_history:
    for event in reversed(event_history[-15:]):
        event_type = event.get("type", "UNKNOWN")
        payload = event.get("payload", {})
        icon = "✅" if "FAILED" not in event_type else "❌"
        st.text(f"{icon} {event_type} — {payload}")
else:
    st.info("No agent activity yet. Run the pipeline to see events here.")

# GlobalState Inspector
st.divider()
st.subheader("GlobalState Inspector")
state_fields = {
    "requirement_context": "Requirement Analysis",
    "generated_testcases": "Test Cases",
    "verification_report": "Verification Report",
    "selenium_scripts": "Selenium Scripts",
    "execution_results": "Execution Results",
    "bugs": "Bug List",
    "bug_clusters": "Bug Clusters",
    "healing_results": "Healing Results",
    "report": "Report",
}
for key, label in state_fields.items():
    value = st.session_state.get(key)
    if value is not None:
        with st.expander(f"✅ {label}"):
            if hasattr(value, "model_dump"):
                st.json(value.model_dump())
            elif isinstance(value, list):
                st.json([v.model_dump() if hasattr(v, "model_dump") else v for v in value])
            elif isinstance(value, dict):
                st.json(value)
            else:
                st.write(value)
    else:
        st.text(f"⏳ {label} — not yet computed")

# Checkpoint controls
st.divider()
col1, col2 = st.columns(2)
if col1.button("Save Checkpoint"):
    checkpoint = {k: st.session_state.get(k) for k in state_fields}
    st.session_state["checkpoint"] = checkpoint
    st.success("Checkpoint saved to session state")
if col2.button("Clear Event History"):
    bus.clear_history()
    st.success("Event history cleared")
    st.rerun()
