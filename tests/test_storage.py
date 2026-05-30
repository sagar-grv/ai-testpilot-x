import pytest

@pytest.fixture
def engine():
    from storage.db import create_engine_and_tables
    eng = create_engine_and_tables(url="sqlite:///:memory:")
    yield eng

def test_all_tables_created(engine):
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    expected = {"requirements", "testcases", "executions", "bugs", "reports", "trust_domains"}
    assert expected.issubset(tables)

def test_trust_domain_crud(engine):
    from sqlalchemy.orm import Session
    from storage.models.trust_domains import TrustDomain
    with Session(engine) as session:
        session.add(TrustDomain(domain="example.com"))
        session.commit()
        result = session.query(TrustDomain).filter_by(domain="example.com").first()
        assert result is not None

def test_requirement_record_insert(engine):
    from sqlalchemy.orm import Session
    from storage.models.requirements import RequirementRecord
    with Session(engine) as session:
        session.add(RequirementRecord(session_id="s1", raw_input="test", priority="High", confidence_score=0.9))
        session.commit()
        r = session.query(RequirementRecord).filter_by(session_id="s1").first()
        assert r.priority == "High"

def test_rag_engine_creates_collections():
    from core.rag_engine import RAGEngine
    engine = RAGEngine(path=None)
    cols = engine.list_collections()
    assert {"testcases", "bugs", "requirements", "reports"}.issubset(set(cols))

def test_rag_engine_upsert_and_query():
    from core.rag_engine import RAGEngine
    engine = RAGEngine(path=None)
    engine.upsert("testcases", "tc-001", "User login with valid credentials", {"tc_id": "TC01"})
    results = engine.query("testcases", "user login", n=1)
    assert len(results) == 1
    assert results[0]["id"] == "tc-001"

def test_rag_engine_ingest_dir(tmp_path):
    from core.rag_engine import RAGEngine
    engine = RAGEngine(path=None)
    (tmp_path / "doc.txt").write_text("Authentication login failure test " * 50)
    count = engine.ingest_knowledge_dir("requirements", tmp_path)
    assert count > 0


def test_rag_ingest_dir_returns_count(tmp_path):
    from core.rag_engine import RAGEngine
    engine = RAGEngine(path=None)
    (tmp_path / "bugs.txt").write_text("Authentication failure on login. " * 50)
    (tmp_path / "testcases.txt").write_text("Valid login test case. " * 50)
    count = engine.ingest_knowledge_dir("bugs", tmp_path)
    assert count >= 2  # at least 2 chunks from 2 files
