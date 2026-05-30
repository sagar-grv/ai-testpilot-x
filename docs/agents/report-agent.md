# ReportAgent

Synthesizes all pipeline results into a GO / GO_WITH_RISK / NO_GO release decision with risk score and recommendations.

## Responsibility

The final agent. Takes execution results, bugs, and coverage data → produces a structured release report with a definitive decision and exit code.

## Input

```python
class ReportInput(BaseModel):
    execution_results: list[ExecutionResult]
    bugs: list[Bug]
    verification: VerificationResult
    session_id: str
```

## Output

```python
class ReportOutput(BaseModel):
    decision: str           # "GO" | "GO_WITH_RISK" | "NO_GO"
    exit_code: int          # 0 | 1 | 2
    risk_score: int         # 0-100
    summary: str
    tests_passed: int
    tests_failed: int
    tests_total: int
    pass_rate: float
    coverage_pct: float
    critical_bugs: int
    high_bugs: int
    medium_bugs: int
    low_bugs: int
    recommendations: list[str]
    generated_at: datetime
```

## Decision logic

```python
def decide(results: ReportInput) -> tuple[str, int]:
    critical = count_bugs(results.bugs, "critical")
    high     = count_bugs(results.bugs, "high")
    pass_rate = results.pass_rate

    if critical > 0:
        return "NO_GO", 2            # any critical bug = blocked

    if high > 0 or pass_rate < 0.8:
        return "GO_WITH_RISK", 1     # high bugs or <80% pass rate = risky

    return "GO", 0                   # all clear
```

## Risk score calculation

```
risk_score = (
    critical_bugs * 30 +
    high_bugs     * 15 +
    medium_bugs   *  5 +
    low_bugs      *  1 +
    (1 - pass_rate) * 25 +
    (1 - coverage_pct/100) * 10
)
clamped to 0-100
```

## Example output

```
Release Decision:  GO WITH RISK     exit 1
Risk Score:        45 / 100
Pass Rate:         83%  (10/12 tests)
Coverage:          87%

Bugs:
  Critical:  0
  High:      2   (Checkout flow, OAuth callback)
  Medium:    1
  Low:       0

Recommendations:
  1. Fix HIGH: Stale locator on checkout submit button before release
  2. Fix HIGH: OAuth callback state parameter not validated
  3. Add test coverage for REQ-008 (Account deletion)
```

## Report storage

The full `ReportOutput` is:
- Saved to SQLite `reports` table
- Written to `{output_dir}/{session_id}_report.json` if `--output` was specified
- Displayed in the Streamlit Reports page (both engineer and executive views)
