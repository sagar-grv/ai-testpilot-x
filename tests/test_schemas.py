from schemas.requirement_schema import RequirementSchema
from schemas.testcase_schema import TestCaseSchema
from schemas.verification_schema import VerificationSchema
from schemas.test_result_schema import TestResultSchema
from schemas.execution_schema import ExecutionSchema
from schemas.api_test_schema import APITestResultSchema
from schemas.bug_schema import BugSchema, BugClusterSchema
from schemas.report_schema import ReportSchema
from schemas.error_schema import ErrorSchema

def test_requirement_schema():
    r = RequirementSchema(modules=["Login"], risk_areas=["Auth"], priority="High", raw_input="test")
    assert r.priority == "High"
    assert r.confidence_score == 0.0

def test_testcase_schema():
    tc = TestCaseSchema(id="TC01", title="Valid Login", module="Login", type="Positive", priority="High", steps=["Go to /login"], expected_result="Dashboard shown")
    assert tc.id == "TC01"
    assert tc.confidence_score == 0.0

def test_verification_schema():
    v = VerificationSchema(coverage_score=0.9, duplicate_count=0, missing_edge_cases=[], passed=True)
    assert v.passed is True

def test_test_result_schema():
    r = TestResultSchema(tc_id="TC01", status="PASS", duration_ms=1200)
    assert r.status == "PASS"

def test_execution_schema():
    results = [TestResultSchema(tc_id="TC01", status="PASS", duration_ms=100)]
    e = ExecutionSchema(mode="MOCK", results=results, total=1, passed=1, failed=0)
    assert e.total == 1

def test_api_test_result_schema():
    a = APITestResultSchema(method="GET", endpoint="/api/login", expected_status=200, assertion="returns 200")
    assert a.method == "GET"

def test_bug_schema():
    b = BugSchema(id="BUG-1", title="Login broken", severity="High", priority="P2",
                  failure_signature="NoSuchElement_login", root_cause="Selector changed",
                  root_cause_confidence=0.9, fix_suggestion="Update selector",
                  fix_confidence=0.8, severity_confidence=0.85)
    assert b.severity == "High"

def test_bug_cluster_schema():
    c = BugClusterSchema(cluster_id="C1", root_cause_summary="Timeout issues", bug_ids=["BUG-1"], severity="High", count=1)
    assert c.count == 1

def test_report_schema():
    from datetime import datetime
    r = ReportSchema(session_id="s1", total_tests=10, passed=8, failed=2,
                     critical_bugs=0, high_bugs=1, medium_bugs=1, low_bugs=0,
                     decision="GO_WITH_RISK", recommendation_text="Risk present",
                     risk_score=45.0, created_at=datetime.utcnow().isoformat())
    assert r.decision == "GO_WITH_RISK"

def test_error_schema():
    e = ErrorSchema(agent_name="RequirementAgent", error_type="RuntimeError", message="API failed", timestamp="2026-01-01")
    assert e.agent_name == "RequirementAgent"


def test_global_state_is_typed_dict():
    from schemas.global_state import GlobalState
    # GlobalState is a TypedDict — test that it can be used as a type
    state: GlobalState = {"session_id": "test-001", "session_metadata": {}}
    assert state["session_id"] == "test-001"
    # Optional fields should default to absent (total=False)
    assert state.get("bugs") is None
