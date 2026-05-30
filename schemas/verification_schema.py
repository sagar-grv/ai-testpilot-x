from __future__ import annotations
from pydantic import BaseModel


class VerificationSchema(BaseModel):
    coverage_score: float
    duplicate_count: int
    missing_edge_cases: list[str]
    passed: bool  # True if coverage >= threshold and low-confidence count within limit
    retry_count: int = 0
    confidence_score: float = 0.0
