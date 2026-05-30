from __future__ import annotations
from typing import Literal
from pydantic import BaseModel


class BugSchema(BaseModel):
    id: str
    title: str
    severity: Literal["Critical", "High", "Medium", "Low"]
    priority: Literal["P1", "P2", "P3", "P4"]
    failure_signature: str
    root_cause: str
    root_cause_confidence: float
    fix_suggestion: str
    fix_confidence: float
    severity_confidence: float
    rag_matches: list[dict] = []


class BugClusterSchema(BaseModel):
    cluster_id: str
    root_cause_summary: str
    bug_ids: list[str]
    severity: str
    count: int
