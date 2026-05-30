"""
ai_testpilot_x public Python API
=================================

Quick start::

    from config import configure
    configure(gemini_api_key="AIzaSy...", execution_mode="MOCK")

    from api import run_pipeline, analyze, analyze_bug

    # Full pipeline
    result = run_pipeline("User should login and checkout", target_url="https://myapp.com")
    print(result["report"]["decision"])  # "GO" | "GO_WITH_RISK" | "NO_GO"

    # Test cases only
    tcs = analyze("User should reset their password")
    for tc in tcs:
        print(tc.id, tc.title)

    # Bug analysis
    bug = analyze_bug("NoSuchElementException: #login-btn at LoginPage.py:42")
    print(bug.severity, bug.fix_suggestion)
"""

from __future__ import annotations
from typing import Any


def run_pipeline(
    user_story: str,
    target_url: str = "",
    session_id: str | None = None,
    approval_fn=None,
) -> dict[str, Any]:
    """Run the full 10-agent pipeline and return the complete GlobalState dict.

    Args:
        user_story: Plain-English description of the feature to test.
        target_url: URL of the application under test (used by Selenium agent).
        session_id: Optional identifier for this test run. Auto-generated if None.
        approval_fn: Optional callable for the HITL gate. Defaults to always-approve.

    Returns:
        dict with keys: ``requirement_context``, ``generated_testcases``,
        ``selenium_scripts``, ``api_test_suite``, ``execution_results``,
        ``bugs``, ``bug_clusters``, ``report``.

    The most important key is ``report["decision"]``: ``"GO"``, ``"GO_WITH_RISK"``,
    or ``"NO_GO"``.

    Exit-code mapping (used by CLI):
        GO          → 0
        GO_WITH_RISK → 1
        NO_GO        → 2
    """
    import uuid
    from orchestrator import build_graph

    sid = session_id or f"run-{uuid.uuid4().hex[:8]}"
    graph = build_graph(approval_fn=approval_fn)
    result = graph.invoke(
        {
            "session_id": sid,
            "session_metadata": {
                "user_story": user_story,
                "target_url": target_url,
            },
        },
        config={"configurable": {"thread_id": sid}},
    )
    return result


def analyze(user_story: str) -> list:
    """Analyze a user story and return generated test cases (no execution).

    Args:
        user_story: Plain-English feature description.

    Returns:
        list of :class:`schemas.testcase_schema.TestCaseSchema` objects.
    """
    from agents.requirement_agent import RequirementAgent
    from agents.testcase_agent import TestCaseAgent

    req = RequirementAgent().run(user_story)
    test_cases = TestCaseAgent().run(req)
    return test_cases


def analyze_requirements(user_story: str):
    """Parse a user story into structured requirement schema.

    Returns:
        :class:`schemas.requirement_schema.RequirementSchema`
    """
    from agents.requirement_agent import RequirementAgent

    return RequirementAgent().run(user_story)


def analyze_bug(error_log: str, session_id: str = "api") -> Any:
    """Analyze an error log or stack trace with AI + RAG.

    Args:
        error_log: Stack trace, error message, or log text.
        session_id: Optional session identifier for RAG storage.

    Returns:
        :class:`schemas.bug_schema.BugSchema` with severity, root_cause,
        fix_suggestion, and confidence scores.
    """
    from agents.bug_agent import BugAgent

    return BugAgent().analyze_single(error_log, session_id=session_id)


def generate_report(
    execution_results, bugs=None, clusters=None, session_id: str = "api"
):
    """Generate a release report from execution results.

    Args:
        execution_results: :class:`schemas.execution_schema.ExecutionSchema` or dict.
        bugs: Optional list of :class:`schemas.bug_schema.BugSchema`.
        session_id: Identifier for this session.

    Returns:
        :class:`schemas.report_schema.ReportSchema` with GO/NO_GO decision.
    """
    from agents.report_agent import ReportAgent
    from schemas.execution_schema import ExecutionSchema
    from schemas.bug_schema import BugSchema, BugClusterSchema

    if isinstance(execution_results, dict):
        execution_results = ExecutionSchema(**execution_results)
    bugs = bugs or []
    clusters = clusters or []
    if bugs and isinstance(bugs[0], dict):
        bugs = [BugSchema(**b) for b in bugs]
    if clusters and isinstance(clusters[0], dict):
        clusters = [BugClusterSchema(**c) for c in clusters]
    return ReportAgent().run(execution_results, bugs, clusters, session_id)


def configure(**kwargs) -> None:
    """Programmatically configure settings before running any agents.

    Example::

        from api import configure
        configure(gemini_api_key="AIzaSy...", execution_mode="MOCK")

    All keyword arguments become uppercase environment variables.
    """
    from config import configure as _configure

    _configure(**kwargs)


# ── Schema re-exports for type hints ─────────────────────────────────────────
from schemas.requirement_schema import RequirementSchema
from schemas.testcase_schema import TestCaseSchema
from schemas.verification_schema import VerificationSchema
from schemas.execution_schema import ExecutionSchema
from schemas.bug_schema import BugSchema, BugClusterSchema
from schemas.report_schema import ReportSchema
from schemas.api_test_schema import APITestResultSchema
from schemas.test_result_schema import TestResultSchema

__version__ = "1.0.0"
__author__ = "sagar-grv"
__all__ = [
    # Functions
    "run_pipeline",
    "analyze",
    "analyze_requirements",
    "analyze_bug",
    "generate_report",
    "configure",
    # Schemas
    "RequirementSchema",
    "TestCaseSchema",
    "VerificationSchema",
    "ExecutionSchema",
    "BugSchema",
    "BugClusterSchema",
    "ReportSchema",
    "APITestResultSchema",
    "TestResultSchema",
    # Meta
    "__version__",
    "__author__",
]
