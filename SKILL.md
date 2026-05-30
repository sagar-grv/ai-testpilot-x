---
name: ai-testpilot-x
description: >
  Use AI TestPilot X to autonomously generate test cases, run Selenium QA pipelines,
  analyze bugs with RAG correlation, and produce GO/NO GO release decisions from
  plain-English user stories. Works as a CLI, Python API, and CI/CD quality gate.
triggers:
  - /testpilot
  - testpilot run
  - generate test cases
  - run qa pipeline
  - analyze bug
  - release decision
  - go no go
  - selenium test
  - hitl gate
topics:
  - testing
  - qa
  - automation
  - selenium
  - ai
  - ci-cd
agents:
  - claude-code
  - cursor
  - opencode
  - copilot
  - windsurf
  - cline
---

# AI TestPilot X Skill

This skill teaches AI agents how to use AI TestPilot X — an autonomous QA platform
that converts plain-English user stories into full test suites, executes them, analyzes
failures, and produces GO/NO GO release decisions.

**Install:**
```bash
npx skills add sagar-grv/ai-testpilot-x
```

**Docs:** https://sagar-grv.github.io/ai-testpilot-x/
**Repo:** https://github.com/sagar-grv/ai-testpilot-x
**Dashboard:** https://ai-testpilot-x.streamlit.app/

---

## When to use AI TestPilot X

Use the `testpilot` CLI (or Python API) when:

- You have a **user story** and need test cases generated from it
- You need a **CI/CD quality gate** that exits 0/1/2 (GO/RISK/NOGO)
- You have a **stack trace or error log** and want AI root cause analysis
- You want to **generate Selenium scripts** without writing them manually
- You need a **release decision** from existing test results
- You want to **understand why a test failed** and what to fix

Do NOT use testpilot when:
- You already have a specific test framework running fine and just need to extend it
- You need visual regression testing (not supported in v1)
- Your test execution needs real browser on a CI runner (use MOCK mode instead)

---

## Decision tree

```
User story available?
  YES → testpilot run --story "..." --mode MOCK
  NO, have a stack trace → testpilot bugs --log "..."
  NO, have test results JSON → testpilot report results.json
  Want test cases only (no execution) → testpilot analyze --story "..."
  Want visual dashboard → testpilot dashboard
```

---

## CLI Commands — Exact Syntax

### Full pipeline (most common)

```bash
testpilot run --story "User can log in and checkout" --mode MOCK
```

```bash
# With specific URL and output file
testpilot run \
  --story "User can filter and sort product listings" \
  --url https://staging.myapp.com \
  --mode LOCAL \
  --output report.json
```

**Exit codes — wire directly into CI:**
- `0` = GO — all tests pass, release safe
- `1` = GO WITH RISK — high severity bugs, release possible but risky
- `2` = NO GO — critical bugs, release blocked

### Test case generation only

```bash
testpilot analyze --story "User can reset their password"
testpilot analyze --story "Admin manages user accounts" --output test_cases.json
```

### Bug analysis

```bash
# Inline error
testpilot bugs --log "NoSuchElementException: #login-btn at LoginPage.py:42"

# From log file
testpilot bugs --log ./test-output.log
```

### Release decision from existing results

```bash
testpilot report test_results.json
testpilot report test_results.json --output release_report.json
```

### Initialize project config

```bash
testpilot init   # writes testpilot.yaml interactively
```

### Launch Streamlit dashboard

```bash
testpilot dashboard          # default port 8501
testpilot dashboard --port 8080
```

---

## Python API

```python
from config import configure
configure(gemini_api_key="AIzaSy...", execution_mode="MOCK")

from api import run_pipeline, analyze, analyze_bug, generate_report

# Full pipeline
result = run_pipeline("User can log in and checkout")
print(result["decision"])    # "GO" | "GO_WITH_RISK" | "NO_GO"
print(result["exit_code"])   # 0 | 1 | 2

# Test cases only
test_cases = analyze("User can filter results")
for tc in test_cases:
    print(tc.id, tc.priority, tc.title)

# Bug analysis
bug = analyze_bug("NoSuchElementException: Unable to locate element: #submit")
print(bug.severity, bug.root_cause, bug.fix_suggestion)

# Exit with CI-compatible code
import sys
sys.exit(result["exit_code"])
```

### HITL approval callback

```python
def my_approval(context):
    print(f"About to run {len(context['test_cases'])} tests")
    return input("Approve? [y/N]: ").lower() == "y"

result = run_pipeline("...", approval_fn=my_approval)
# None = auto-approve (default for CLI/CI)
```

---

## The 10-Agent Pipeline

Each agent runs in sequence via LangGraph. Understanding what each agent does helps
you interpret output and debug issues.

| # | Agent | Input | Output |
|---|---|---|---|
| 1 | **RequirementAgent** | User story text | Modules, risk areas, acceptance criteria |
| 2 | **TestCaseAgent** | Requirement modules | Structured test cases (UI/API/edge) |
| 3 | **VerificationAgent** | Test cases + requirements | Coverage %, gaps, duplicate flags |
| 4 | **SeleniumAgent** | UI test cases | Python Selenium scripts |
| 5 | **APIAgent** | API test cases | httpx test suites |
| 6 | **ExecutionAgent** | Scripts + HITL gate | Pass/fail results per test |
| 7 | **BugAgent** | Failed tests | Bug reports with root cause + RAG correlation |
| 8 | **HealingAgent** | Locator failures | Patched scripts with healed locators |
| 9 | **ReportAgent** | All results | GO/NO GO decision + risk score |

### GlobalState — what flows between agents

```python
# Every agent reads from and writes to GlobalState
state = {
    "story": str,
    "requirements": list[Requirement],
    "test_cases": list[TestCase],
    "verification": VerificationResult,
    "selenium_scripts": list[SeleniumScript],
    "api_tests": list[APITest],
    "execution_results": list[ExecutionResult],
    "bugs": list[Bug],
    "healed_locators": list[HealedLocator],
    "report": ReportOutput,
    "hitl_approved": bool,
}
```

---

## Execution Modes

| Mode | When to use | Requirements |
|---|---|---|
| `MOCK` | CI/CD, cloud, no real app | None — AI simulates results |
| `LOCAL` | Local dev, app running | Chrome + ChromeDriver |
| `GRID` | Parallel browser CI | Selenium Grid endpoint |

```bash
# MOCK is the default and works everywhere
testpilot run --story "..." --mode MOCK

# LOCAL requires Chrome
testpilot run --story "..." --mode LOCAL --url http://localhost:3000

# GRID for parallel execution
testpilot run --story "..." --mode GRID --url https://staging.myapp.com
```

---

## Self-Healing Locator Hierarchy

When a Selenium test fails with `NoSuchElementException`, HealingAgent tries 7 strategies:

```
1. data-testid    [data-testid='login-btn']        ← most stable, try first
2. data-qa        [data-qa='submit']
3. ID             #login-btn
4. name           name="username"
5. CSS selector   .auth-form button[type=submit]
6. XPath          //button[contains(text(),'Log in')]
7. AI-generated   Gemini analyzes DOM snapshot → generates new locator
```

Healed locators are stored in ChromaDB — the next run starts with the working locator.

---

## CI/CD Integration

```yaml
# GitHub Actions — drop-in quality gate
- name: AI Quality Gate
  run: |
    pip install -r requirements.txt && pip install -e .
    python -m cli.main run \
      --story "User can login and checkout" \
      --mode MOCK
  env:
    GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
    EXECUTION_MODE: MOCK
  # exit 0 = GO (pass), exit 1 = RISK (fail), exit 2 = NOGO (fail)
```

---

## Configuration (`testpilot.yaml`)

```yaml
gemini_api_key: ${GEMINI_API_KEY}  # env var or direct value
execution_mode: MOCK               # MOCK | LOCAL | GRID
target_url: https://your-app.com
db_url: sqlite:///.testpilot/testpilot.db
chroma_path: .testpilot/chroma_db
output_dir: .testpilot/reports
log_level: WARNING
```

---

## Common Patterns

### Pattern 1: CI quality gate on every PR

```bash
# In CI:
testpilot run --story "Core user flows: login, browse, checkout" --mode MOCK
# Fails the build if GO_WITH_RISK (exit 1) or NO_GO (exit 2)
```

### Pattern 2: Analyze failures after your own test suite

```bash
# After pytest or another runner produces a stack trace:
testpilot bugs --log ./pytest-failures.log
```

### Pattern 3: Generate tests before writing code (TDD)

```bash
testpilot analyze --story "User can manage their subscription" --output test_cases.json
# Use test_cases.json as spec for implementation
```

### Pattern 4: Pre-release audit

```bash
testpilot run \
  --story "All critical user journeys: auth, onboarding, checkout, account" \
  --url https://staging.myapp.com \
  --mode LOCAL \
  --output pre_release_report.json

# Check exit code in shell
echo $?   # 0=GO, 1=RISK, 2=NOGO
```

---

## Troubleshooting

### `ModuleNotFoundError` on `testpilot run`

The package isn't installed as editable. Run:
```bash
pip install -e .
# or from installed package:
pip install ai-testpilot-x
```

### `GEMINI_API_KEY not set`

Export the key before running:
```bash
export GEMINI_API_KEY="AIzaSy..."
testpilot run --story "..."
```

### Execution mode `LOCAL` fails — no Chrome

Either install Chrome + ChromeDriver, or switch to MOCK:
```bash
testpilot run --story "..." --mode MOCK
```

### `NoSuchElementException` in execution results

Normal — `HealingAgent` will attempt automatic recovery. If healing also fails, check
the bug report for root cause and suggested fix locator.

### Pipeline hangs

Gemini API latency can be high. Set `LOG_LEVEL=DEBUG` to see which agent is running:
```bash
LOG_LEVEL=DEBUG testpilot run --story "..."
```

---

## Project layout (for code navigation)

```
agents/         10 AI agents (requirement, testcase, verification, ...)
cli/            Typer CLI commands (main.py, cmd_run.py, cmd_analyze.py, ...)
core/           LLM client, RAG engine, event bus, explain engine
schemas/        Pydantic v2 schemas (GlobalState + all agent I/O)
storage/        SQLAlchemy models + SQLite setup
memory/         ChromaDB conversation/execution/bug memory
execution/      Selenium runner, API runner, Selenium Grid client
monitoring/     Loguru logger, LangSmith tracing
prompts/        Gemini prompt templates (*.txt)
pages/          Streamlit pages (8 pages)
tests/          72 pytest tests
api.py          Public Python API surface
config.py       Pydantic-settings config + YAML loader
orchestrator.py LangGraph graph definition
app.py          Streamlit entry point
pyproject.toml  Package config, optional extras, entry points
```
