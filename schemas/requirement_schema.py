from __future__ import annotations
from typing import Literal
from pydantic import BaseModel


class RequirementSchema(BaseModel):
    modules: list[str]
    risk_areas: list[str]
    priority: Literal["Low", "Medium", "High", "Critical"]
    confidence_score: float = 0.0
    raw_input: str = ""
