from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from storage.db import Base

class ExecutionRecord(Base):
    __tablename__ = "executions"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    mode: Mapped[str] = mapped_column(String(16), nullable=False)
    total: Mapped[int] = mapped_column(Integer, default=0)
    passed: Mapped[int] = mapped_column(Integer, default=0)
    failed: Mapped[int] = mapped_column(Integer, default=0)
    results_json: Mapped[str] = mapped_column(Text, default="[]")
    screenshots_json: Mapped[str] = mapped_column(Text, default="[]")
    logs_json: Mapped[str] = mapped_column(Text, default="[]")
    executed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
