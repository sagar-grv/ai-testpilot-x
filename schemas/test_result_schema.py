from __future__ import annotations
from typing import Literal
from pydantic import BaseModel

class TestResultSchema(BaseModel):
    tc_id: str
    status: Literal["PASS", "FAIL", "SKIP", "ERROR"]
    duration_ms: float
    error_message: str = ""
    screenshot_path: str = ""
