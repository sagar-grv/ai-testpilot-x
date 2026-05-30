"""Page 07 — Workflow Studio: live pipeline view + GlobalState inspector."""
import streamlit as st

st.set_page_config(page_title="Workflow Studio | AI TestPilot X", page_icon="🔀", layout="wide")

st.markdown("""
<h1 class="tp-page-title">🔀 Workflow Studio</h1>
<p class="tp-page-subtitle">
    Live view of the LangGraph agent pipeline — see which agents have run and inspect their outputs.
</p>
""", unsafe_allow_html=True)
st.divider()

try:
    from core.event_bus import bus
    event_history = bus.get_history()
except Exception:
    event_history = []

completed_events = {e["type"] for e in event_history}

# ── Pipeline definition ───────────────────────────────────────────────────────
PIPELINE = [
    ("🔍", "RequirementAgent",  "REQUIREMENT_ANALYZED",  "Parses user story into modules & risk areas"),
    ("📝", "TestCaseAgent",     "TESTCASES_GENERATED",   "Generates structured test cases with RAG"),
    ("✅", "VerificationAgent", "VERIFICATION_COMPLETE", "Checks coverage & edge case gaps"),
    ("⚙️", "SeleniumAgent",     None,                    "Generates Python Selenium scripts"),
    ("🌐", "APIAgent",          None,                    "Generates HTTP API test suites"),
    ("👤", "HITL Gate",         "EXECUTION_APPROVED",    "Human approval before execution"),
    ("▶️", "ExecutionAgent",    "EXECUTION_COMPLETE",    "Runs tests — LOCAL / MOCK / GRID"),
    ("🐛", "BugAgent",          "BUG_ANALYZED",          "AI root cause + RAG bug correlation"),
    ("🔧", "HealingAgent",      "HEALING_COMPLETE",      "Auto-recovers broken selectors"),
    ("📊", "ReportAgent",       "REPORT_GENERATED",      "GO / GO_WITH_RISK / NO_GO decision"),
]

# ── Pipeline status grid ──────────────────────────────────────────────────────
st.markdown('<div class="tp-section-title">Pipeline Status</div>', unsafe_allow_html=True)

completed_count = sum(1 for _, _, ev, _ in PIPELINE if ev and ev in completed_events)
total_events = sum(1 for _, _, ev, _ in PIPELINE if ev)

cols = st.columns(5)
for i, (icon, name, event_key, desc) in enumerate(PIPELINE):
    done = event_key and event_key in completed_events
    is_gate = name == "HITL Gate"
    col = cols[i % 5]
    with col:
        if done:
            bg, border, label_color, badge_bg, badge_text = (
                "#052e16", "#22c55e55", "#4ade80", "#14532d", "#4ade80"
            )
            status = "✓ Done"
        elif is_gate and not done:
            bg, border, label_color, badge_bg, badge_text = (
                "#422006", "#f59e0b44", "#fbbf24", "#78350f", "#fbbf24"
            )
            status = "⏳ Pending"
        else:
            bg, border, label_color, badge_bg, badge_text = (
                "#0F1117", "#1E2337", "#475569", "#1E2337", "#475569"
            )
            status = "○ Pending"

        col.markdown(f"""
        <div style="background:{bg}; border:1px solid {border}; border-radius:12px;
                    padding:16px 12px; text-align:center; margin-bottom:8px;
                    transition:border-color 0.2s;">
            <div style="font-size:26px; margin-bottom:8px;">{icon}</div>
            <div style="font-weight:700; font-size:12px; color:{label_color};
                        margin-bottom:6px; line-height:1.3;">{name}</div>
            <div style="background:{badge_bg}; color:{badge_text};
                        border-radius:20px; padding:2px 8px; font-size:10px;
                        font-weight:700; display:inline-block;">{status}</div>
            <div style="font-size:10px; color:#334155; margin-top:6px;
                        line-height:1.4;">{desc}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.progress(
    completed_count / total_events if total_events > 0 else 0,
    text=f"Pipeline progress: {completed_count} of {total_events} stages complete"
)

st.divider()

# ── Agent flow diagram ────────────────────────────────────────────────────────
st.markdown('<div class="tp-section-title">Agent Flow Diagram</div>', unsafe_allow_html=True)

try:
    from streamlit_agraph import agraph, Node, Edge, Config

    def _node_color(name, ev):
        if ev and ev in completed_events:
            return "#1a4731"
        if name == "HITL Gate":
            return "#422006"
        return "#0F1117"

    def _node_font_color(name, ev):
        if ev and ev in completed_events:
            return "#4ade80"
        if name == "HITL Gate":
            return "#fbbf24"
        return "#475569"

    nodes = [
        Node(
            id=name,
            label=f"{icon} {name}",
            color={"background": _node_color(name, ev),
                   "border": "#22c55e" if (ev and ev in completed_events) else "#1E2337",
                   "highlight": {"background": "#2e1065", "border": "#6C63FF"}},
            font={"color": _node_font_color(name, ev), "size": 11},
            size=22,
            shape="box",
            borderWidth=1.5,
        )
        for icon, name, ev, _ in PIPELINE
    ]

    edges = [
        Edge("RequirementAgent", "TestCaseAgent", color={"color": "#2D3557"}),
        Edge("TestCaseAgent", "VerificationAgent", color={"color": "#2D3557"}),
        Edge("VerificationAgent", "SeleniumAgent", color={"color": "#2D3557"}),
        Edge("VerificationAgent", "APIAgent", color={"color": "#2D3557"}),
        Edge("SeleniumAgent", "HITL Gate", color={"color": "#2D3557"}),
        Edge("APIAgent", "HITL Gate", color={"color": "#2D3557"}),
        Edge("HITL Gate", "ExecutionAgent", color={"color": "#f59e0b44"}),
        Edge("ExecutionAgent", "BugAgent", label="failures",
             color={"color": "#ef444466"}, font={"size": 10, "color": "#64748B"}),
        Edge("ExecutionAgent", "ReportAgent", label="all pass",
             color={"color": "#22c55e44"}, font={"size": 10, "color": "#64748B"}),
        Edge("BugAgent", "HealingAgent", color={"color": "#2D3557"}),
        Edge("BugAgent", "ReportAgent", color={"color": "#2D3557"}),
        Edge("HealingAgent", "ReportAgent", color={"color": "#2D3557"}),
    ]

    config = Config(
        width=920, height=380, directed=True, physics=False,
        nodeHighlightBehavior=True, highlightColor="#6C63FF",
        backgroundColor="#080B12",
        node={"labelProperty": "label"},
        link={"labelProperty": "label", "renderLabel": True,
              "color": "#2D3557", "smooth": {"type": "cubicBezier"}}
    )
    agraph(nodes=nodes, edges=edges, config=config)

except ImportError:
    st.markdown("""
    <div class="tp-card" style="font-family:monospace; font-size:12px; color:#64748B; line-height:2;">
        🔍 RequirementAgent → 📝 TestCaseAgent → ✅ VerificationAgent<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├─▶ ⚙️ SeleniumAgent<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─▶ 🌐 APIAgent<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↓ HITL Gate<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▶️ ExecutionAgent<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↓ (on failures)<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;🐛 BugAgent → 🔧 HealingAgent → 📊 ReportAgent
    </div>""", unsafe_allow_html=True)

st.divider()

# ── GlobalState Inspector ─────────────────────────────────────────────────────
st.markdown('<div class="tp-section-title">GlobalState Inspector</div>', unsafe_allow_html=True)
st.markdown("""
<div style="font-size:12px; color:#475569; margin-bottom:12px;">
    Live view of what each agent has produced in the current session.
    Green = computed, Gray = not yet run.
</div>""", unsafe_allow_html=True)

STATE_MAP = [
    ("requirement_context",  "🔍", "Requirement Analysis"),
    ("generated_testcases",  "📝", "Generated Test Cases"),
    ("verification_report",  "✅", "Verification Report"),
    ("selenium_scripts",     "⚙️", "Selenium Scripts"),
    ("api_test_suite",       "🌐", "API Test Suite"),
    ("execution_results",    "▶️", "Execution Results"),
    ("bugs",                 "🐛", "Bug Analysis"),
    ("bug_clusters",         "🗂️", "Bug Clusters"),
    ("healing_results",      "🔧", "Healing Results"),
    ("report",               "📊", "Report"),
]

gc1, gc2 = st.columns(2)
for i, (key, icon, label) in enumerate(STATE_MAP):
    value = st.session_state.get(key)
    col = gc1 if i % 2 == 0 else gc2
    with col:
        if value is not None:
            with st.expander(f"{icon} ✅ {label}"):
                try:
                    if hasattr(value, "model_dump"):
                        st.json(value.model_dump())
                    elif isinstance(value, list) and value:
                        first = value[0]
                        st.json(first.model_dump() if hasattr(first, "model_dump") else first)
                        if len(value) > 1:
                            st.caption(f"... and {len(value) - 1} more items")
                    elif isinstance(value, dict):
                        st.json(value)
                    else:
                        st.write(str(value)[:200])
                except Exception as e:
                    st.write(f"Display error: {e}")
        else:
            col.markdown(f"""
            <div style="background:#0F1117; border:1px dashed #1E2337; border-radius:8px;
                        padding:10px 14px; color:#334155; font-size:12px;
                        margin-bottom:8px; display:flex; align-items:center; gap:8px;">
                <span>{icon}</span>
                <span>⏳ {label} — not yet computed</span>
            </div>""", unsafe_allow_html=True)

st.divider()

# Controls
ctrl1, ctrl2 = st.columns(2)
if ctrl1.button("💾 Save Checkpoint", use_container_width=True):
    st.session_state["checkpoint"] = {k: st.session_state.get(k) for k, _, _ in STATE_MAP}
    st.success("Session checkpoint saved.")
if ctrl2.button("🗑 Clear Event History", use_container_width=True):
    try:
        bus.clear_history()
        st.success("Event history cleared.")
        st.rerun()
    except Exception:
        st.error("Could not clear history.")
