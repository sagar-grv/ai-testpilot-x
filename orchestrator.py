"""
orchestrator.py — LangGraph multi-agent workflow for AI TestPilot X.

Graph flow:
  START → requirement → testcase → verification → [selenium, api] → hitl_gate
  → execution → (bug_analysis | report) → (healing | report) → report → END
"""

from __future__ import annotations
from typing import Callable
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from schemas.global_state import GlobalState
from monitoring.logger import get_logger
from core.event_bus import bus, EventType

log = get_logger(__name__)


# ─── HITL approval function ───────────────────────────────────────────────────
# Default: always approve (used in CLI / headless mode).
# Override via build_graph(approval_fn=...) for UI-gated approval.
def _DEFAULT_APPROVAL_FN() -> bool:
    return True


# ─── Node implementations ────────────────────────────────────────────────────


def _run_requirement(state: GlobalState) -> dict:
    from agents.requirement_agent import RequirementAgent

    req_input = state.get("session_metadata", {}).get("user_story", "")
    if not req_input:
        return {}
    agent = RequirementAgent()
    result = agent.run(req_input)
    return {"requirement_context": result.model_dump()}


def _run_testcase(state: GlobalState) -> dict:
    from agents.testcase_agent import TestCaseAgent
    from schemas.requirement_schema import RequirementSchema

    req_data = state.get("requirement_context")
    if not req_data:
        return {}
    req = RequirementSchema(**req_data)
    agent = TestCaseAgent()
    tcs = agent.run(req)
    return {"generated_testcases": [tc.model_dump() for tc in tcs]}


def _run_verification(state: GlobalState) -> dict:
    from agents.verification_agent import VerificationAgent
    from schemas.testcase_schema import TestCaseSchema

    tc_data = state.get("generated_testcases") or []
    if not tc_data:
        return {}
    tcs = [TestCaseSchema(**d) for d in tc_data]
    agent = VerificationAgent()
    report = agent.run(tcs)
    return {"verification_report": report.model_dump()}


def _run_selenium(state: GlobalState) -> dict:
    from agents.selenium_agent import SeleniumAgent
    from schemas.testcase_schema import TestCaseSchema

    tc_data = state.get("generated_testcases") or []
    target_url = state.get("session_metadata", {}).get("target_url", "")
    if not tc_data:
        return {}
    tcs = [TestCaseSchema(**d) for d in tc_data]
    agent = SeleniumAgent()
    scripts = agent.generate_all(tcs, target_url)
    return {"selenium_scripts": scripts}


def _run_api(state: GlobalState) -> dict:
    from agents.api_agent import APIAgent
    from schemas.requirement_schema import RequirementSchema

    req_data = state.get("requirement_context")
    if not req_data:
        return {}
    req = RequirementSchema(**req_data)
    agent = APIAgent()
    suite = agent.run(req)
    return {
        "api_test_suite": {k: [t.model_dump() for t in v] for k, v in suite.items()}
    }


def _run_hitl_gate(state: GlobalState) -> dict:
    """HITL gate — calls the approval function registered at graph build time.

    In CLI/headless mode this always returns True.
    In Streamlit mode, approval_fn blocks until the user clicks Approve.
    """
    approved = state.get("_approval_fn", _DEFAULT_APPROVAL_FN)()
    log.debug(f"HITL gate: approved={approved}")
    if approved:
        bus.emit(EventType.EXECUTION_APPROVED, {})
    return {"_hitl_approved": approved}


def _run_execution(state: GlobalState) -> dict:
    from agents.execution_agent import ExecutionAgent
    from config import settings

    scripts = state.get("selenium_scripts") or {}
    target_url = state.get("session_metadata", {}).get("target_url", "")
    approved = state.get("_hitl_approved", True)
    if not scripts:
        log.warning("ExecutionAgent: no scripts to run")
        return {}
    agent = ExecutionAgent()
    result = agent.run(
        mode=settings.EXECUTION_MODE,
        scripts=scripts,
        target_url=target_url,
        approved=approved,
    )
    return {"execution_results": result.model_dump()}


def _should_analyze_bugs(state: GlobalState) -> str:
    exec_data = state.get("execution_results") or {}
    if exec_data.get("failed", 0) > 0:
        return "bug_analysis"
    return "report"


def _run_bug_analysis(state: GlobalState) -> dict:
    from agents.bug_agent import BugAgent
    from schemas.execution_schema import ExecutionSchema

    exec_data = state.get("execution_results")
    if not exec_data:
        return {}
    session_id = state.get("session_id", "unknown")
    execution = ExecutionSchema(**exec_data)
    agent = BugAgent()
    bugs, clusters = agent.run(execution, session_id)
    return {
        "bugs": [b.model_dump() for b in bugs],
        "bug_clusters": [c.model_dump() for c in clusters],
    }


def _should_heal(state: GlobalState) -> str:
    bugs = state.get("bugs") or []
    if any("NoSuchElement" in b.get("failure_signature", "") for b in bugs):
        return "healing"
    return "report"


def _run_healing(state: GlobalState) -> dict:
    from agents.healing_agent import HealingAgent
    from schemas.bug_schema import BugSchema

    bugs_data = state.get("bugs") or []
    healing_results = {}
    agent = HealingAgent()
    for bug_data in bugs_data:
        bug = BugSchema(**bug_data)
        if "NoSuchElement" in bug.failure_signature:
            healing = agent.attempt_healing(bug.failure_signature, "")
            healing_results[bug.id] = healing
    return {"healing_results": healing_results}


def _run_report(state: GlobalState) -> dict:
    from agents.report_agent import ReportAgent
    from schemas.execution_schema import ExecutionSchema
    from schemas.bug_schema import BugSchema, BugClusterSchema

    session_id = state.get("session_id", "unknown")
    exec_data = state.get("execution_results")
    execution = ExecutionSchema(**exec_data) if exec_data else None
    bugs_data = state.get("bugs") or []
    clusters_data = state.get("bug_clusters") or []
    bugs = [BugSchema(**d) for d in bugs_data]
    clusters = [BugClusterSchema(**d) for d in clusters_data]
    agent = ReportAgent()
    report = agent.run(execution, bugs, clusters, session_id)
    return {"report": report.model_dump()}


# ─── Graph builder ────────────────────────────────────────────────────────────


def build_graph(approval_fn: Callable[[], bool] | None = None):
    """Build and compile the LangGraph state machine.

    Args:
        approval_fn: Called at the HITL gate to decide if execution proceeds.
            Defaults to ``lambda: True`` (always approve — CLI / headless mode).
            Pass a custom callable for UI-gated approval (e.g., Streamlit button).
    """
    _approval = approval_fn or _DEFAULT_APPROVAL_FN
    builder = StateGraph(GlobalState)

    # Nodes
    builder.add_node("requirement", _run_requirement)
    builder.add_node("testcase", _run_testcase)
    builder.add_node("verification", _run_verification)
    builder.add_node("selenium", _run_selenium)
    builder.add_node("api", _run_api)
    builder.add_node("hitl_gate", _run_hitl_gate)
    builder.add_node("execution", _run_execution)
    builder.add_node("bug_analysis", _run_bug_analysis)
    builder.add_node("healing", _run_healing)
    builder.add_node("reporting", _run_report)

    # Edges
    builder.add_edge(START, "requirement")
    builder.add_edge("requirement", "testcase")
    builder.add_edge("testcase", "verification")
    builder.add_edge("verification", "selenium")
    builder.add_edge("verification", "api")
    builder.add_edge("selenium", "hitl_gate")
    builder.add_edge("api", "hitl_gate")
    builder.add_edge("hitl_gate", "execution")
    builder.add_conditional_edges(
        "execution",
        _should_analyze_bugs,
        {"bug_analysis": "bug_analysis", "report": "reporting"},
    )
    builder.add_conditional_edges(
        "bug_analysis", _should_heal, {"healing": "healing", "report": "reporting"}
    )
    builder.add_edge("healing", "reporting")
    builder.add_edge("reporting", END)

    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory)
    log.info("LangGraph orchestrator compiled successfully")
    return graph


# Module-level compiled graph
graph = build_graph()
