from __future__ import annotations
from typing import Literal
from pydantic import BaseModel


class ReportSchema(BaseModel):
    session_id: str
    total_tests: int
    passed: int
    failed: int
    critical_bugs: int
    high_bugs: int
    medium_bugs: int
    low_bugs: int
    decision: Literal["GO", "GO_WITH_RISK", "NO_GO"]
    recommendation_text: str
    risk_score: float  # 0-100
    created_at: str
    confidence_score: float = 0.0
