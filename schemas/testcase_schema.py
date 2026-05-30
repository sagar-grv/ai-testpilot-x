from __future__ import annotations
from typing import Literal
from pydantic import BaseModel


class TestCaseSchema(BaseModel):
    id: str  # TC01, TC02...
    title: str
    module: str
    type: Literal[
        "Positive", "Negative", "Security", "Performance", "Boundary", "Accessibility"
    ]
    priority: Literal["Low", "Medium", "High", "Critical"]
    steps: list[str]
    expected_result: str
    confidence_score: float = 0.0
