from __future__ import annotations
from typing import Literal
from pydantic import BaseModel
from schemas.test_result_schema import TestResultSchema

class ExecutionSchema(BaseModel):
    mode: Literal["LOCAL", "MOCK", "GRID"]
    results: list[TestResultSchema]
    total: int
    passed: int
    failed: int
    screenshots: list[str] = []
    logs: list[str] = []
