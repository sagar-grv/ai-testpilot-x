from __future__ import annotations
from typing import Literal
from pydantic import BaseModel

class APITestResultSchema(BaseModel):
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"]
    endpoint: str
    body: dict = {}
    expected_status: int
    assertion: str
    actual_status: int = 0
    response_body: str = ""
    response_time_ms: float = 0.0
    passed: bool = False
    schema_valid: bool = False
