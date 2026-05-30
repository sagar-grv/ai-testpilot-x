from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from storage.db import Base


class RequirementRecord(Base):
    __tablename__ = "requirements"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    raw_input: Mapped[str] = mapped_column(Text, nullable=False)
    modules: Mapped[str] = mapped_column(Text, default="[]")
    risk_areas: Mapped[str] = mapped_column(Text, default="[]")
    priority: Mapped[str] = mapped_column(String(16), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
