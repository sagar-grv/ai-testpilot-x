from unittest.mock import patch, MagicMock


def test_requirement_agent_returns_schema():
    from agents.requirement_agent import RequirementAgent
    from schemas.requirement_schema import RequirementSchema
    mock_response = '{"modules": ["Login", "Cart"], "risk_areas": ["Auth"], "priority": "High", "confidence_score": 0.9}'
    with patch("core.llm_client.LLMClient.generate", return_value=mock_response):
        agent = RequirementAgent()
        result = agent.run("User should login and checkout successfully")
    assert isinstance(result, RequirementSchema)
    assert "Login" in result.modules
    assert result.priority == "High"
    assert result.confidence_score == 0.9


def test_requirement_agent_emits_event():
    from agents.requirement_agent import RequirementAgent
    from core.event_bus import bus, EventType
    bus.clear_history()
    mock_response = '{"modules": ["Login"], "risk_areas": ["Auth"], "priority": "High", "confidence_score": 0.8}'
    with patch("core.llm_client.LLMClient.generate", return_value=mock_response):
        agent = RequirementAgent()
        agent.run("Test story")
    history = bus.get_history()
    assert any(e["type"] == EventType.REQUIREMENT_ANALYZED for e in history)


def test_testcase_agent_returns_list():
    from agents.testcase_agent import TestCaseAgent
    from schemas.requirement_schema import RequirementSchema
    from schemas.testcase_schema import TestCaseSchema
    mock_response = '[{"title":"Valid Login","type":"Positive","priority":"High","steps":["Open /login","Enter credentials"],"expected_result":"Dashboard shown","confidence_score":0.9}]'
    req = RequirementSchema(modules=["Login"], risk_areas=["Auth"], priority="High", raw_input="User logs in")
    with patch("core.llm_client.LLMClient.generate", return_value=mock_response):
        agent = TestCaseAgent()
        result = agent.run(req)
    assert isinstance(result, list)
    assert len(result) >= 1
    assert isinstance(result[0], TestCaseSchema)
    assert result[0].id == "TC01"


def test_testcase_agent_assigns_sequential_ids():
    from agents.testcase_agent import TestCaseAgent
    from schemas.requirement_schema import RequirementSchema
    mock_response = '[{"title":"T1","type":"Positive","priority":"High","steps":["step"],"expected_result":"ok","confidence_score":0.8},{"title":"T2","type":"Negative","priority":"Medium","steps":["step"],"expected_result":"error","confidence_score":0.7}]'
    req = RequirementSchema(modules=["Login"], risk_areas=[], priority="High", raw_input="test")
    with patch("core.llm_client.LLMClient.generate", return_value=mock_response):
        agent = TestCaseAgent()
        result = agent.run(req)
    ids = [tc.id for tc in result]
    assert "TC01" in ids
    assert "TC02" in ids


def test_verification_agent_passes_good_coverage():
    from agents.verification_agent import VerificationAgent
    from schemas.testcase_schema import TestCaseSchema
    tcs = [
        TestCaseSchema(id="TC01", title="Valid Login", module="Login", type="Positive", priority="High", steps=["step"], expected_result="ok"),
        TestCaseSchema(id="TC02", title="Invalid Login", module="Login", type="Negative", priority="High", steps=["step"], expected_result="error"),
        TestCaseSchema(id="TC03", title="SQL Injection", module="Login", type="Security", priority="Critical", steps=["step"], expected_result="blocked"),
        TestCaseSchema(id="TC04", title="Empty Password", module="Login", type="Boundary", priority="Medium", steps=["step"], expected_result="error"),
    ]
    mock_response = '{"coverage_score": 0.95, "duplicate_count": 0, "missing_edge_cases": [], "passed": true}'
    with patch("core.llm_client.LLMClient.generate", return_value=mock_response):
        agent = VerificationAgent()
        result = agent.run(tcs)
    assert result.passed is True
    assert result.coverage_score >= 0.6


def test_verification_agent_fails_low_coverage():
    from agents.verification_agent import VerificationAgent
    from schemas.testcase_schema import TestCaseSchema
    tcs = [
        TestCaseSchema(id="TC01", title="Valid Login", module="Login", type="Positive", priority="High", steps=["step"], expected_result="ok"),
    ]
    mock_response = '{"coverage_score": 0.25, "duplicate_count": 0, "missing_edge_cases": ["Security tests", "Boundary tests"], "passed": false}'
    with patch("core.llm_client.LLMClient.generate", return_value=mock_response):
        agent = VerificationAgent()
        result = agent.run(tcs)
    assert result.passed is False


def test_verification_agent_heuristic_fallback():
    from agents.verification_agent import VerificationAgent
    from schemas.testcase_schema import TestCaseSchema
    agent = VerificationAgent()
    tcs = [
        TestCaseSchema(id="TC01", title="T1", module="M", type="Positive", priority="High", steps=[], expected_result=""),
        TestCaseSchema(id="TC02", title="T2", module="M", type="Negative", priority="High", steps=[], expected_result=""),
        TestCaseSchema(id="TC03", title="T3", module="M", type="Security", priority="High", steps=[], expected_result=""),
        TestCaseSchema(id="TC04", title="T4", module="M", type="Boundary", priority="High", steps=[], expected_result=""),
    ]
    result = agent._heuristic_verify(tcs)
    assert result.coverage_score == 1.0
    assert result.passed is True


# ── Task 3.1: SeleniumAgent ──────────────────────────────────────────────────

def test_selenium_agent_returns_code_string():
    from agents.selenium_agent import SeleniumAgent
    from schemas.testcase_schema import TestCaseSchema
    tc = TestCaseSchema(id="TC01", title="Valid Login", module="Login", type="Positive",
                        priority="High", steps=["Open /login", "Enter credentials", "Click submit"],
                        expected_result="Dashboard shown")
    with patch("core.llm_client.LLMClient.generate", return_value="def test_TC01(driver):\n    driver.get('https://example.com')"):
        agent = SeleniumAgent()
        result = agent.generate_for_tc(tc)
    assert isinstance(result, str)
    assert "def test_TC01" in result


def test_selenium_agent_strips_markdown_fences():
    from agents.selenium_agent import SeleniumAgent
    from schemas.testcase_schema import TestCaseSchema
    tc = TestCaseSchema(id="TC01", title="T", module="M", type="Positive", priority="High",
                        steps=["step"], expected_result="ok")
    mock_code = "```python\ndef test_TC01(driver):\n    pass\n```"
    with patch("core.llm_client.LLMClient.generate", return_value=mock_code):
        agent = SeleniumAgent()
        result = agent.generate_for_tc(tc)
    assert "```" not in result


def test_selenium_agent_generate_all():
    from agents.selenium_agent import SeleniumAgent
    from schemas.testcase_schema import TestCaseSchema
    tcs = [
        TestCaseSchema(id="TC01", title="T1", module="M", type="Positive", priority="High", steps=[], expected_result=""),
        TestCaseSchema(id="TC02", title="T2", module="M", type="Negative", priority="High", steps=[], expected_result=""),
    ]
    with patch("core.llm_client.LLMClient.generate", return_value="def test_TC01(driver): pass"):
        agent = SeleniumAgent()
        result = agent.generate_all(tcs)
    assert "TC01" in result
    assert "TC02" in result


# ── Task 3.4: ExecutionAgent ─────────────────────────────────────────────────

def test_execution_agent_mock_returns_schema():
    from agents.execution_agent import ExecutionAgent
    from schemas.execution_schema import ExecutionSchema
    agent = ExecutionAgent()
    scripts = {"TC01": "def test_TC01(driver): pass", "TC02": "def test_TC02(driver): pass"}
    result = agent.run(mode="MOCK", scripts=scripts, target_url="https://example.com", approved=True)
    assert isinstance(result, ExecutionSchema)
    assert result.mode == "MOCK"
    assert result.total == 2
    assert result.passed + result.failed == result.total


def test_execution_agent_raises_when_not_approved():
    from agents.execution_agent import ExecutionAgent
    agent = ExecutionAgent()
    with __import__("pytest").raises(ValueError, match="not approved"):
        agent.run(mode="MOCK", scripts={"TC01": ""}, target_url="", approved=False)


def test_execution_agent_trust_domain_crud(tmp_path):
    from agents.execution_agent import ExecutionAgent
    from storage.db import create_engine_and_tables
    from sqlalchemy.orm import Session
    from storage.models.trust_domains import TrustDomain
    # Use in-memory DB for isolation
    eng = create_engine_and_tables(url="sqlite:///:memory:")
    agent = ExecutionAgent()
    # Patch get_session to use in-memory engine
    with patch("agents.execution_agent.get_session") as mock_session:
        with Session(eng) as s:
            mock_session.return_value = s
            assert agent.check_trust_domain("testdomain.com") is False
            agent.add_trust_domain("testdomain.com")
        with Session(eng) as s:
            mock_session.return_value = s
            # Should now be trusted
            result = s.query(TrustDomain).filter_by(domain="testdomain.com").first()
            assert result is not None
