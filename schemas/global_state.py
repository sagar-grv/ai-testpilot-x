from __future__ import annotations
from typing import Optional, TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
    from schemas.requirement_schema import RequirementSchema
    from schemas.testcase_schema import TestCaseSchema
    from schemas.verification_schema import VerificationSchema
    from schemas.execution_schema import ExecutionSchema
    from schemas.bug_schema import BugSchema, BugClusterSchema
    from schemas.report_schema import ReportSchema
    from schemas.error_schema import ErrorSchema


class GlobalState(TypedDict, total=False):
    session_id: str
    session_metadata: dict
    requirement_context: Optional[dict]
    generated_testcases: Optional[list]
    verification_report: Optional[dict]
    execution_plan: Optional[str]
    selenium_scripts: Optional[dict]
    api_test_suite: Optional[dict]
    execution_results: Optional[dict]
    bugs: Optional[list]
    bug_clusters: Optional[list]
    healing_results: Optional[dict]
    risk_analysis: Optional[dict]
    report: Optional[dict]
    checkpoint: Optional[dict]
    agent_errors: Optional[list]
