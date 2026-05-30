# Python API

Use AI TestPilot X programmatically in your own scripts, notebooks, or agents.

## Setup

```python
from config import configure

configure(
    gemini_api_key="AIzaSy...",
    execution_mode="MOCK",           # MOCK | LOCAL | GRID
    target_url="https://myapp.com",  # optional
    log_level="WARNING",
)
```

!!! tip "Environment variables"
    If `GEMINI_API_KEY` is already set in the environment, you can skip `configure()` — the package reads it automatically.

---

## `run_pipeline()`

Run the full 10-agent QA pipeline.

```python
from api import run_pipeline

result = run_pipeline(
    story="User can log in and checkout a product",
    target_url="https://myapp.com",   # optional override
    mode="MOCK",                       # optional override
    session_id="my-session-001",       # optional
    approval_fn=None,                  # None = auto-approve HITL gate
)
```

### Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `story` | `str` | Yes | Plain-English user story |
| `target_url` | `str` | No | Target URL (overrides config) |
| `mode` | `str` | No | `MOCK` / `LOCAL` / `GRID` |
| `session_id` | `str` | No | Custom session identifier |
| `approval_fn` | `Callable[[], bool]` | No | HITL gate callback. `None` = auto-approve |

### Return value

```python
{
    "session_id": "abc123",
    "decision": "GO_WITH_RISK",       # GO | GO_WITH_RISK | NO_GO
    "exit_code": 1,                   # 0 | 1 | 2
    "risk_score": 45,
    "test_cases": [...],              # list of TestCase objects
    "execution_results": [...],       # list of ExecutionResult objects
    "bugs": [...],                    # list of Bug objects
    "report": { ... },               # full ReportOutput dict
}
```

### HITL gate callback

Supply a custom `approval_fn` to control the Human-in-the-Loop execution gate:

```python
def my_approval(context: dict) -> bool:
    print(f"About to execute {len(context['test_cases'])} tests.")
    answer = input("Approve? [y/N]: ")
    return answer.lower() == "y"

result = run_pipeline(story="...", approval_fn=my_approval)
```

In CLI mode, `approval_fn=None` auto-approves. In Streamlit, the approval button is wired automatically.

---

## `analyze()`

Generate test cases from a user story. No execution.

```python
from api import analyze

test_cases = analyze("User can filter and sort product listings")

for tc in test_cases:
    print(tc.id, tc.title, tc.type, tc.priority)
```

### Return value

A list of `TestCase` Pydantic objects:

```python
class TestCase:
    id: str                  # e.g. "TC-001"
    title: str
    type: str                # "ui" | "api" | "edge"
    priority: str            # "critical" | "high" | "medium" | "low"
    preconditions: list[str]
    steps: list[str]
    expected_result: str
    module: str
    tags: list[str]
```

---

## `analyze_bug()`

Analyze a stack trace or error log.

```python
from api import analyze_bug

bug = analyze_bug(
    "NoSuchElementException: Unable to locate element: #login-btn at LoginPage.py:42"
)

print(bug.severity)       # "high"
print(bug.root_cause)     # "Stale locator — element ID changed after last deploy"
print(bug.fix_suggestion) # "Update locator to data-testid='login-button'"
```

### Return value

A `BugReport` Pydantic object:

```python
class BugReport:
    id: str
    severity: str            # "critical" | "high" | "medium" | "low"
    root_cause: str
    affected_component: str
    fix_suggestion: str
    similar_bugs: list[str]  # IDs of related bugs from RAG knowledge base
    confidence: float        # 0.0 - 1.0
```

---

## `generate_report()`

Generate a GO/NO GO release decision from existing execution results.

```python
from api import generate_report

report = generate_report(
    execution_results=result["execution_results"],
    bugs=result["bugs"],
)

print(report.decision)    # "NO_GO"
print(report.risk_score)  # 78
print(report.summary)     # "2 critical bugs in checkout flow..."
```

### Return value

A `ReportOutput` Pydantic object:

```python
class ReportOutput:
    decision: str           # "GO" | "GO_WITH_RISK" | "NO_GO"
    exit_code: int          # 0 | 1 | 2
    risk_score: int         # 0-100
    summary: str
    critical_bugs: int
    high_bugs: int
    tests_passed: int
    tests_failed: int
    coverage_pct: float
    recommendations: list[str]
```

---

## Full example

```python
from config import configure
from api import run_pipeline, analyze_bug

# Configure once
configure(gemini_api_key="AIzaSy...", execution_mode="MOCK")

# Run a full pipeline
result = run_pipeline("User can register, log in, and purchase a subscription")

# Inspect
print(f"Decision:   {result['decision']}")
print(f"Risk score: {result['report']['risk_score']}")
print(f"Tests:      {result['report']['tests_passed']}/{result['report']['tests_passed'] + result['report']['tests_failed']} passed")

# Exit with the right code for CI
import sys
sys.exit(result["exit_code"])
```
