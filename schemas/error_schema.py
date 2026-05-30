from __future__ import annotations
from pydantic import BaseModel


class ErrorSchema(BaseModel):
    agent_name: str
    error_type: str
    message: str
    timestamp: str
