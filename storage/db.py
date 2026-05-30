"""storage/db.py — SQLAlchemy engine factory."""

from __future__ import annotations
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from config import settings


class Base(DeclarativeBase):
    pass


def create_engine_and_tables(url: str | None = None):
    db_url = url or settings.DB_URL
    engine = create_engine(db_url, echo=False, future=True)
    # Side-effect imports: register models with Base.metadata before create_all
    import storage.models.requirements  # noqa: F401
    import storage.models.testcases  # noqa: F401
    import storage.models.executions  # noqa: F401
    import storage.models.bugs  # noqa: F401
    import storage.models.reports  # noqa: F401
    import storage.models.trust_domains  # noqa: F401

    Base.metadata.create_all(engine)
    return engine


_engine = None
_SessionFactory = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine_and_tables()
    return _engine


def get_session():
    global _SessionFactory
    if _SessionFactory is None:
        _SessionFactory = sessionmaker(bind=get_engine(), autoflush=False)
    return _SessionFactory()
