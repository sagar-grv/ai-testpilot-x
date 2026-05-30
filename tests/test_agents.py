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
    req = RequirementSchema(
        modules=["Login"],
        risk_areas=["Auth"],
        priority="High",
        raw_input="User logs in",
    )
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
    req = RequirementSchema(
        modules=["Login"], risk_areas=[], priority="High", raw_input="test"
    )
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
        TestCaseSchema(
            id="TC01",
            title="Valid Login",
            module="Login",
            type="Positive",
            priority="High",
            steps=["step"],
            expected_result="ok",
        ),
        TestCaseSchema(
            id="TC02",
            title="Invalid Login",
            module="Login",
            type="Negative",
            priority="High",
            steps=["step"],
            expected_result="error",
        ),
        TestCaseSchema(
            id="TC03",
            title="SQL Injection",
            module="Login",
            type="Security",
            priority="Critical",
            steps=["step"],
            expected_result="blocked",
        ),
        TestCaseSchema(
            id="TC04",
            title="Empty Password",
            module="Login",
            type="Boundary",
            priority="Medium",
            steps=["step"],
            expected_result="error",
        ),
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
        TestCaseSchema(
            id="TC01",
            title="Valid Login",
            module="Login",
            type="Positive",
            priority="High",
            steps=["step"],
            expected_result="ok",
        ),
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
        TestCaseSchema(
            id="TC01",
            title="T1",
            module="M",
            type="Positive",
            priority="High",
            steps=[],
            expected_result="",
        ),
        TestCaseSchema(
            id="TC02",
            title="T2",
            module="M",
            type="Negative",
            priority="High",
            steps=[],
            expected_result="",
        ),
        TestCaseSchema(
            id="TC03",
            title="T3",
            module="M",
            type="Security",
            priority="High",
            steps=[],
            expected_result="",
        ),
        TestCaseSchema(
            id="TC04",
            title="T4",
            module="M",
            type="Boundary",
            priority="High",
            steps=[],
            expected_result="",
        ),
    ]
    result = agent._heuristic_verify(tcs)
    assert result.coverage_score == 1.0
    assert result.passed is True


# ── Task 3.1: SeleniumAgent ──────────────────────────────────────────────────


def test_selenium_agent_returns_code_string():
    from agents.selenium_agent import SeleniumAgent
    from schemas.testcase_schema import TestCaseSchema

    tc = TestCaseSchema(
        id="TC01",
        title="Valid Login",
        module="Login",
        type="Positive",
        priority="High",
        steps=["Open /login", "Enter credentials", "Click submit"],
        expected_result="Dashboard shown",
    )
    with patch(
        "core.llm_client.LLMClient.generate",
        return_value="def test_TC01(driver):\n    driver.get('https://example.com')",
    ):
        agent = SeleniumAgent()
        result = agent.generate_for_tc(tc)
    assert isinstance(result, str)
    assert "def test_TC01" in result


def test_selenium_agent_strips_markdown_fences():
    from agents.selenium_agent import SeleniumAgent
    from schemas.testcase_schema import TestCaseSchema

    tc = TestCaseSchema(
        id="TC01",
        title="T",
        module="M",
        type="Positive",
        priority="High",
        steps=["step"],
        expected_result="ok",
    )
    mock_code = "```python\ndef test_TC01(driver):\n    pass\n```"
    with patch("core.llm_client.LLMClient.generate", return_value=mock_code):
        agent = SeleniumAgent()
        result = agent.generate_for_tc(tc)
    assert "```" not in result


def test_selenium_agent_generate_all():
    from agents.selenium_agent import SeleniumAgent
    from schemas.testcase_schema import TestCaseSchema

    tcs = [
        TestCaseSchema(
            id="TC01",
            title="T1",
            module="M",
            type="Positive",
            priority="High",
            steps=[],
            expected_result="",
        ),
        TestCaseSchema(
            id="TC02",
            title="T2",
            module="M",
            type="Negative",
            priority="High",
            steps=[],
            expected_result="",
        ),
    ]
    with patch(
        "core.llm_client.LLMClient.generate", return_value="def test_TC01(driver): pass"
    ):
        agent = SeleniumAgent()
        result = agent.generate_all(tcs)
    assert "TC01" in result
    assert "TC02" in result


# ── Task 3.4: ExecutionAgent ─────────────────────────────────────────────────


def test_execution_agent_mock_returns_schema():
    from agents.execution_agent import ExecutionAgent
    from schemas.execution_schema import ExecutionSchema

    agent = ExecutionAgent()
    scripts = {
        "TC01": "def test_TC01(driver): pass",
        "TC02": "def test_TC02(driver): pass",
    }
    result = agent.run(
        mode="MOCK", scripts=scripts, target_url="https://example.com", approved=True
    )
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


# ── Task 3.5: HealingAgent ───────────────────────────────────────────────────


def test_healing_agent_returns_dict():
    from agents.healing_agent import HealingAgent

    with patch(
        "core.llm_client.LLMClient.generate", return_value="[data-testid='login-btn']"
    ):
        agent = HealingAgent()
        result = agent.attempt_healing(
            "NoSuchElementException: Unable to locate element: #login-btn",
            "https://example.com",
            tc_id="TC01",
        )
    assert isinstance(result, dict)
    assert "tried_locators" in result
    assert "success" in result
    assert result["success"] is True
    assert result["recovered_selector"] != ""


def test_healing_agent_extracts_selector():
    from agents.healing_agent import _extract_selector

    msg = "NoSuchElementException: Unable to locate element: #login-button"
    sel = _extract_selector(msg)
    assert "#login-button" in sel


def test_healing_agent_returns_success_false_on_empty():
    from agents.healing_agent import HealingAgent

    with patch("core.llm_client.LLMClient.generate", return_value=""):
        agent = HealingAgent()
        result = agent.attempt_healing("NoSuchElement: #btn", "https://example.com")
    assert result["success"] is False
    assert result["recovered_selector"] == ""


# ── Task 4.1: APIAgent + api_runner ─────────────────────────────────────────


def test_api_agent_returns_list():
    from agents.api_agent import APIAgent
    from schemas.api_test_schema import APITestResultSchema
    from schemas.requirement_schema import RequirementSchema

    mock_response = '[{"method":"GET","endpoint":"/api/login","body":null,"expected_status":200,"assertion":"returns 200 OK"}]'
    req = RequirementSchema(
        modules=["Login"], risk_areas=[], priority="High", raw_input="User logs in"
    )
    with patch("core.llm_client.LLMClient.generate", return_value=mock_response):
        agent = APIAgent()
        result = agent.run_for_module("Login", req)
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], APITestResultSchema)
    assert result[0].method == "GET"


def test_api_agent_handles_invalid_method():
    from agents.api_agent import APIAgent
    from schemas.requirement_schema import RequirementSchema

    mock_response = '[{"method":"INVALID","endpoint":"/api/test","body":null,"expected_status":200,"assertion":"test"}]'
    req = RequirementSchema(
        modules=["Test"], risk_areas=[], priority="Medium", raw_input="test"
    )
    with patch("core.llm_client.LLMClient.generate", return_value=mock_response):
        agent = APIAgent()
        result = agent.run_for_module("Test", req)
    assert result[0].method == "GET"  # defaulted to GET


def test_api_runner_is_async():
    import inspect
    from execution.runners.api_runner import run_api_test, run_api_test_sync

    assert inspect.iscoroutinefunction(run_api_test)
    assert not inspect.iscoroutinefunction(run_api_test_sync)


def test_api_agent_run_all_modules():
    from agents.api_agent import APIAgent
    from schemas.requirement_schema import RequirementSchema

    mock_response = '[{"method":"GET","endpoint":"/api/test","body":null,"expected_status":200,"assertion":"ok"}]'
    req = RequirementSchema(
        modules=["Login", "Cart"], risk_areas=[], priority="High", raw_input="test"
    )
    with patch("core.llm_client.LLMClient.generate", return_value=mock_response):
        agent = APIAgent()
        result = agent.run(req)
    assert isinstance(result, dict)
    assert "Login" in result
    assert "Cart" in result


# ── Task 4.2: BugAgent ───────────────────────────────────────────────────────


def test_bug_agent_analyze_single_returns_schema():
    from agents.bug_agent import BugAgent
    from schemas.bug_schema import BugSchema

    mock_response = '{"title":"Login button missing","severity":"High","priority":"P2","failure_signature":"NoSuchElement_login","root_cause":"Button selector changed","root_cause_confidence":0.9,"fix_suggestion":"Update to data-testid","fix_confidence":0.85,"severity_confidence":0.8}'
    mock_db = MagicMock()
    with (
        patch("core.llm_client.LLMClient.generate", return_value=mock_response),
        patch("memory.bug_memory.BugMemory.get_similar_bugs", return_value=[]),
        patch("memory.bug_memory.BugMemory.store_bug"),
        patch("storage.db.get_session", return_value=mock_db),
    ):
        agent = BugAgent()
        result = agent.analyze_single(
            "NoSuchElementException: #login-btn", "sess-001", 0
        )
    assert isinstance(result, BugSchema)
    assert result.severity == "High"
    assert result.root_cause_confidence == 0.9


def test_bug_agent_run_returns_bugs_and_clusters():
    from agents.bug_agent import BugAgent
    from schemas.execution_schema import ExecutionSchema
    from schemas.test_result_schema import TestResultSchema

    exec_schema = ExecutionSchema(
        mode="MOCK",
        results=[
            TestResultSchema(
                tc_id="TC01",
                status="FAIL",
                duration_ms=1200,
                error_message="NoSuchElementException: Unable to locate element: #login",
            ),
            TestResultSchema(tc_id="TC02", status="PASS", duration_ms=800),
        ],
        total=2,
        passed=1,
        failed=1,
    )
    mock_response = '{"title":"Login broken","severity":"High","priority":"P2","failure_signature":"NoSuchElement","root_cause":"Selector changed","root_cause_confidence":0.8,"fix_suggestion":"Update selector","fix_confidence":0.7,"severity_confidence":0.85}'
    mock_db = MagicMock()
    with (
        patch("core.llm_client.LLMClient.generate", return_value=mock_response),
        patch("memory.bug_memory.BugMemory.get_similar_bugs", return_value=[]),
        patch("memory.bug_memory.BugMemory.store_bug"),
        patch("storage.db.get_session", return_value=mock_db),
    ):
        agent = BugAgent()
        bugs, clusters = agent.run(exec_schema, "sess-001")
    assert len(bugs) == 1  # only 1 failed test
    assert isinstance(clusters, list)


def test_bug_agent_clusters_by_root_cause():
    from agents.bug_agent import BugAgent
    from schemas.bug_schema import BugSchema

    agent = BugAgent.__new__(BugAgent)
    bugs = [
        BugSchema(
            id="B1",
            title="T1",
            severity="High",
            priority="P2",
            failure_signature="s1",
            root_cause="timeout waiting for element",
            root_cause_confidence=0.8,
            fix_suggestion="f",
            fix_confidence=0.7,
            severity_confidence=0.8,
        ),
        BugSchema(
            id="B2",
            title="T2",
            severity="Medium",
            priority="P3",
            failure_signature="s2",
            root_cause="timeout on checkout page",
            root_cause_confidence=0.7,
            fix_suggestion="f",
            fix_confidence=0.6,
            severity_confidence=0.7,
        ),
        BugSchema(
            id="B3",
            title="T3",
            severity="Low",
            priority="P4",
            failure_signature="s3",
            root_cause="selector not found",
            root_cause_confidence=0.9,
            fix_suggestion="f",
            fix_confidence=0.8,
            severity_confidence=0.9,
        ),
    ]
    clusters = agent._cluster_bugs(bugs)
    timeout_cluster = next(
        (c for c in clusters if "timeout" in c.root_cause_summary.lower()), None
    )
    assert timeout_cluster is not None
    assert timeout_cluster.count == 2


def test_bug_agent_failure_signature_extraction():
    from agents.bug_agent import _extract_failure_signature

    msg = "NoSuchElementException: Unable to locate element: #login-btn"
    sig = _extract_failure_signature(msg)
    assert len(sig) <= 50
    assert "_" in sig or len(sig) > 0


# ── Task 5.1: ReportAgent ────────────────────────────────────────────────────


def test_report_agent_decision_no_go():
    from agents.report_agent import ReportAgent
    from schemas.bug_schema import BugSchema

    agent = ReportAgent.__new__(ReportAgent)
    bugs = [
        BugSchema(
            id="B1",
            title="T",
            severity="Critical",
            priority="P1",
            failure_signature="s",
            root_cause="r",
            root_cause_confidence=0.9,
            fix_suggestion="f",
            fix_confidence=0.8,
            severity_confidence=0.9,
        )
    ]
    assert agent._determine_decision(bugs) == "NO_GO"


def test_report_agent_decision_go_with_risk():
    from agents.report_agent import ReportAgent
    from schemas.bug_schema import BugSchema

    agent = ReportAgent.__new__(ReportAgent)
    bugs = [
        BugSchema(
            id="B1",
            title="T",
            severity="High",
            priority="P2",
            failure_signature="s",
            root_cause="r",
            root_cause_confidence=0.8,
            fix_suggestion="f",
            fix_confidence=0.7,
            severity_confidence=0.8,
        )
    ]
    assert agent._determine_decision(bugs) == "GO_WITH_RISK"


def test_report_agent_decision_go():
    from agents.report_agent import ReportAgent
    from schemas.bug_schema import BugSchema

    agent = ReportAgent.__new__(ReportAgent)
    bugs = [
        BugSchema(
            id="B1",
            title="T",
            severity="Low",
            priority="P4",
            failure_signature="s",
            root_cause="r",
            root_cause_confidence=0.6,
            fix_suggestion="f",
            fix_confidence=0.5,
            severity_confidence=0.6,
        )
    ]
    assert agent._determine_decision(bugs) == "GO"


def test_report_agent_go_when_no_bugs():
    from agents.report_agent import ReportAgent

    agent = ReportAgent.__new__(ReportAgent)
    assert agent._determine_decision([]) == "GO"


def test_report_agent_run_returns_schema():
    from agents.report_agent import ReportAgent
    from schemas.report_schema import ReportSchema
    from schemas.execution_schema import ExecutionSchema
    from schemas.test_result_schema import TestResultSchema

    execution = ExecutionSchema(
        mode="MOCK",
        results=[TestResultSchema(tc_id="TC01", status="PASS", duration_ms=500)],
        total=1,
        passed=1,
        failed=0,
    )
    mock_llm = (
        '{"recommendation_text":"All good.","risk_score":5,"confidence_score":0.9}'
    )
    with (
        patch("core.llm_client.LLMClient.generate", return_value=mock_llm),
        patch("storage.db.get_session"),
        patch("core.rag_engine.rag_engine.upsert"),
    ):
        agent = ReportAgent()
        report = agent.run(execution, [], [], "test-session")
    assert isinstance(report, ReportSchema)
    assert report.decision == "GO"
    assert report.total_tests == 1


# ── Task 5.2: AgentRegistry ──────────────────────────────────────────────────


def test_agent_registry_registers_all():
    from agents.registry import AgentRegistry

    agent_names = AgentRegistry.list_agents()
    expected = {
        "requirement",
        "testcase",
        "verification",
        "selenium",
        "api",
        "execution",
        "bug",
        "healing",
        "report",
    }
    assert expected.issubset(set(agent_names))


def test_agent_registry_get():
    from agents.registry import AgentRegistry
    from agents.requirement_agent import RequirementAgent

    AgentRegistry.register("requirement", RequirementAgent)
    cls = AgentRegistry.get("requirement")
    assert cls is RequirementAgent


def test_agent_registry_get_unknown():
    from agents.registry import AgentRegistry

    assert AgentRegistry.get("nonexistent") is None


# ── Task 5.4: Orchestrator ───────────────────────────────────────────────────


def test_orchestrator_builds_without_error():
    """Orchestrator must compile without raising."""
    import orchestrator

    assert orchestrator.graph is not None


def test_should_analyze_bugs_routing():
    """Routing: failed tests -> bug_analysis, all pass -> report."""
    from orchestrator import _should_analyze_bugs

    state_with_failures = {
        "execution_results": {
            "failed": 2,
            "passed": 1,
            "total": 3,
            "mode": "MOCK",
            "results": [],
        }
    }
    state_no_failures = {
        "execution_results": {
            "failed": 0,
            "passed": 3,
            "total": 3,
            "mode": "MOCK",
            "results": [],
        }
    }
    assert _should_analyze_bugs(state_with_failures) == "bug_analysis"
    assert _should_analyze_bugs(state_no_failures) == "report"


# ── Task 6.1: Explain Engine ─────────────────────────────────────────────────


def test_explain_engine_returns_string():
    from core.explain_engine import explain_decision
    from unittest.mock import patch

    with patch(
        "core.llm_client.LLMClient.generate",
        return_value="The AI identified Login as high priority because it is a critical user flow.",
    ):
        result = explain_decision("Priority: High, Modules: Login, Risk: Auth")
    assert isinstance(result, str)
    assert len(result) > 0


# ── Task 6.3: Coverage Polish ────────────────────────────────────────────────


def test_bug_memory_get_similar_returns_list():
    """BugMemory must return list even on empty DB."""
    from memory.bug_memory import BugMemory

    mem = BugMemory()
    result = mem.get_similar_bugs("test_signature", n=3)
    assert isinstance(result, list)


def test_event_bus_singleton():
    """bus singleton must be the same object every import."""
    from core.event_bus import bus as bus1
    from core.event_bus import bus as bus2

    assert bus1 is bus2


def test_event_bus_history_grows():
    """Emitting events grows history."""
    from core.event_bus import bus, EventType

    initial_count = len(bus.get_history())
    bus.emit(EventType.AGENT_FAILED, {"test": True})
    assert len(bus.get_history()) == initial_count + 1


def test_metrics_timer_records_run():
    """timer context manager must record a run for the agent."""
    from monitoring.metrics import metrics, timer

    initial_runs = metrics.get_all().get("TestAgent", None)
    initial = initial_runs.runs if initial_runs else 0
    with timer("TestAgent"):
        pass
    m = metrics.get_all().get("TestAgent")
    assert m is not None
    assert m.runs == initial + 1


def test_rag_engine_count_returns_int():
    from core.rag_engine import RAGEngine

    engine = RAGEngine(path=None)
    count = engine.count("testcases")
    assert isinstance(count, int)
    assert count >= 0
