"""GlobalState — single source of truth for LangGraph orchestration."""
from __future__ import annotations
from typing import Optional, Any
from typing_extensions import TypedDict


class GlobalState(TypedDict, total=False):
    """LangGraph state dict. All fields optional (total=False) for incremental updates."""
    session_id: str
    session_metadata: dict
    # Agent outputs (stored as dicts for JSON serialization)
    requirement_context: Optional[dict]      # RequirementSchema.model_dump()
    generated_testcases: Optional[list]      # list[TestCaseSchema.model_dump()]
    verification_report: Optional[dict]      # VerificationSchema.model_dump()
    execution_plan: Optional[str]
    selenium_scripts: Optional[dict]         # {tc_id: code_string}
    api_test_suite: Optional[dict]           # {module: list[APITestResultSchema.model_dump()]}
    execution_results: Optional[dict]        # ExecutionSchema.model_dump()
    bugs: Optional[list]                     # list[BugSchema.model_dump()]
    bug_clusters: Optional[list]             # list[BugClusterSchema.model_dump()]
    healing_results: Optional[dict]          # {bug_id: healing_result_dict}
    risk_analysis: Optional[dict]            # V2, nullable
    report: Optional[dict]                   # ReportSchema.model_dump()
    checkpoint: Optional[dict]
    agent_errors: Optional[list]             # list[ErrorSchema.model_dump()]
