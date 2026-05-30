# TestCaseAgent

Generates structured test cases from requirement modules, enriched with RAG context from historical tests.

## Responsibility

Converts structured requirements into actionable test cases covering UI flows, API calls, and edge cases.

## Input

```python
class TestCaseInput(BaseModel):
    requirements: list[RequirementModule]
    session_id: str
```

## Output

```python
class TestCase(BaseModel):
    id: str              # "TC-001"
    title: str
    type: str            # "ui" | "api" | "edge"
    priority: str        # "critical" | "high" | "medium" | "low"
    module: str          # links back to RequirementModule.id
    preconditions: list[str]
    steps: list[str]
    expected_result: str
    tags: list[str]
```

## What it does

1. For each `RequirementModule`, queries ChromaDB `test_cases` collection for similar past test cases
2. Calls Gemini with requirement + RAG context → generates test cases
3. Produces a mix of: happy path, negative, edge case, security, performance
4. Stores to SQLite `testcases` table
5. Embeds into ChromaDB for future RAG correlation

## RAG enrichment

Similar historical test cases are retrieved and injected into the Gemini prompt as few-shot examples:

```
[Context from knowledge base]
Similar test for OAuth login (ran 2025-11-03, passed):
  Steps: Navigate to /login → Click "Sign in with Google" → Complete OAuth → Assert redirect to /dashboard

Generate a test case for: [current requirement]
```

This produces higher-quality test cases by building on what worked before.

## Example output (3 of ~12 cases)

```
TC-001  [CRITICAL]  Happy path: Google OAuth login and dashboard redirect    ui
TC-002  [HIGH]      Negative: OAuth cancelled by user                        ui
TC-003  [HIGH]      Negative: OAuth token expired mid-flow                   edge
TC-004  [MEDIUM]    Security: CSRF token validation on callback              api
TC-005  [LOW]       Performance: Login completes within 3 seconds            edge
```
