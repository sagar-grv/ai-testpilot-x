from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, Float, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from storage.db import Base

class BugRecord(Base):
    __tablename__ = "bugs"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    bug_id: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(512))
    severity: Mapped[str] = mapped_column(String(16))
    priority: Mapped[str] = mapped_column(String(8))
    failure_signature: Mapped[str] = mapped_column(Text)
    root_cause: Mapped[str] = mapped_column(Text)
    root_cause_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    fix_suggestion: Mapped[str] = mapped_column(Text)
    fix_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    severity_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
