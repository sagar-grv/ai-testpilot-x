# BugAgent

Analyzes test failures with AI root cause analysis and RAG correlation against historical bugs.

## Responsibility

For every failed test, produce a structured bug report with root cause, severity, fix suggestion, and similar historical bugs from the knowledge base.

## Input

```python
class BugInput(BaseModel):
    execution_results: list[ExecutionResult]   # failed tests only
    test_cases: list[TestCase]
```

## Output

```python
class Bug(BaseModel):
    id: str                    # "BUG-001"
    test_case_id: str
    severity: str              # "critical" | "high" | "medium" | "low"
    title: str
    root_cause: str
    affected_component: str
    error_message: str
    fix_suggestion: str
    similar_bugs: list[str]    # IDs of RAG-matched historical bugs
    confidence: float          # 0.0 - 1.0
    cluster: str | None        # bug cluster ID (grouped by component)
```

## Root cause analysis

For each failure, Gemini analyzes:

1. The error message and stack trace
2. The test steps that preceded the failure
3. The expected vs actual behavior
4. RAG-retrieved similar bugs from ChromaDB

```
[Error] NoSuchElementException: Unable to locate element: #google-signin
[Steps] Navigate to /login → Click #google-signin (FAILED)
[Similar bugs from knowledge base]
  BUG-047: Same error after Google button ID changed in deploy 2025-11-01
  BUG-089: #google-signin missing after A/B test rollout

[Analysis] The element ID has likely changed. Check recent frontend deploys.
[Root cause] Stale locator — element ID changed after frontend update
[Fix] Update locator: By.CSS_SELECTOR, "[data-testid='google-signin-btn']"
```

## RAG correlation

BugAgent queries ChromaDB `bugs` collection with the error message + component:

```python
similar = rag.query(
    collection="bugs",
    query=f"{error_message} {affected_component}",
    n_results=5
)
```

Returns previously seen bugs with same root cause, linking new bugs to known patterns.

## Bug clustering

Bugs from the same session are clustered by `affected_component` to surface systemic issues:

```
Cluster: Authentication (3 bugs)
  BUG-001: Stale locator on #google-signin
  BUG-002: OAuth callback missing CSRF state
  BUG-003: Session not persisted after login

Cluster: Checkout (1 bug)
  BUG-004: Payment form submit button not found
```

Visible in the Streamlit Bug Analyzer page.
