# VerificationAgent

Audits the generated test cases for coverage gaps, duplicates, and missing edge cases.

## Responsibility

Quality control on the test suite before execution. Ensures meaningful coverage, flags redundancy, and surfaces paths that are under-tested.

## Input

```python
class VerificationInput(BaseModel):
    test_cases: list[TestCase]
    requirements: list[RequirementModule]
```

## Output

```python
class VerificationResult(BaseModel):
    coverage_pct: float          # 0.0 - 100.0
    covered_modules: list[str]
    uncovered_modules: list[str]
    duplicate_pairs: list[tuple[str, str]]   # TC IDs
    missing_edge_cases: list[str]
    recommendations: list[str]
    approved: bool
```

## What it does

1. Maps test cases to requirement modules → calculates coverage %
2. Detects semantic duplicates using ChromaDB similarity search
3. Checks for missing critical paths: error states, boundary values, auth edge cases
4. Produces recommendations for gaps
5. Sets `approved: True` if coverage >= 70% and no critical modules uncovered

## Coverage calculation

```
coverage_pct = (modules_with_at_least_one_test / total_modules) * 100
```

A module is "covered" if it has at least one test case of any priority. Critical modules failing coverage block the pipeline.

## Example output

```json
{
  "coverage_pct": 87.5,
  "covered_modules": ["REQ-001", "REQ-002", "REQ-003", "REQ-004", "REQ-005", "REQ-006", "REQ-007"],
  "uncovered_modules": ["REQ-008"],
  "duplicate_pairs": [["TC-003", "TC-007"]],
  "missing_edge_cases": [
    "Network timeout during OAuth callback",
    "Concurrent login from multiple devices"
  ],
  "recommendations": [
    "Add test for REQ-008 (Account deletion flow)",
    "Merge TC-003 and TC-007 — near-identical OAuth error scenarios",
    "Add network timeout edge case for OAuth callback"
  ],
  "approved": true
}
```
