# AI TestPilot X

> Autonomous AI-Powered Quality Engineering Platform & CLI

[![Live App](https://img.shields.io/badge/Live%20App-ai--testpilot--x.streamlit.app-FF4B4B?logo=streamlit&logoColor=white)](https://ai-testpilot-x.streamlit.app/)
[![Docs](https://img.shields.io/badge/Docs-sagar--grv.github.io-00D9FF?logo=materialformkdocs&logoColor=white)](https://sagar-grv.github.io/ai-testpilot-x/)
[![skills.sh](https://skills.sh/b/sagar-grv/ai-testpilot-x)](https://skills.sh/sagar-grv/ai-testpilot-x)
[![PyPI](https://img.shields.io/badge/PyPI-ai--testpilot--x-blue?logo=pypi)](https://pypi.org/project/ai-testpilot-x/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-red)](https://streamlit.io)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.3.x-green)](https://langchain-ai.github.io/langgraph/)
[![Gemini](https://img.shields.io/badge/Gemini-2.5--Flash-yellow)](https://aistudio.google.com)
[![Tests](https://img.shields.io/badge/Tests-72%20Passing-brightgreen)](https://github.com/sagar-grv/ai-testpilot-x)

**Live Demo:** https://ai-testpilot-x.streamlit.app/

---

## What Is It?

AI TestPilot X turns a plain-English user story into a complete QA pipeline — automatically.

```bash
pip install ai-testpilot-x

testpilot run --story "User can login and checkout a product"
```

```
  Analyzing requirements...   ✓  3 modules · High priority
  Generating test cases...    ✓  12 test cases
  Verifying coverage...       ✓  87% coverage
  Executing tests (MOCK)...   ✓  10 passed · 2 failed
  Analyzing bugs...           ✓  2 bugs found
  Generating report...        ✓

  ┌─────────────────────────────────────────────┐
  │  Release Decision:  ⚠ GO WITH RISK          │
  │  Risk Score:        45 / 100                │
  │  Tests:             10 / 12 passed          │
  │  Bugs:              0 Critical · 2 High     │
  └─────────────────────────────────────────────┘
```

---

## Installation

```bash
# Core CLI (test generation, bug analysis, reports)
pip install ai-testpilot-x

# With visual Streamlit dashboard
pip install ai-testpilot-x[ui]

# With real Selenium browser execution
pip install ai-testpilot-x[selenium]

# Everything
pip install ai-testpilot-x[all]
```

---

## Install the AI Agent Skill

Any AI coding agent (Claude Code, Cursor, OpenCode, Copilot, Windsurf) can learn to
use AI TestPilot X with a single command:

```bash
npx skills add sagar-grv/ai-testpilot-x
```

After installing, your agent understands all CLI commands, the 10-agent pipeline,
exit code semantics, HITL gate usage, and self-healing locator patterns.

Listed on [skills.sh](https://skills.sh/sagar-grv/ai-testpilot-x) — the open agent skills ecosystem.

---

## Documentation

Full docs at **[sagar-grv.github.io/ai-testpilot-x](https://sagar-grv.github.io/ai-testpilot-x/)**:

- [Getting Started](https://sagar-grv.github.io/ai-testpilot-x/getting-started/)
- [CLI Reference](https://sagar-grv.github.io/ai-testpilot-x/cli-reference/)
- [Architecture](https://sagar-grv.github.io/ai-testpilot-x/architecture/)
- [CI/CD Integration](https://sagar-grv.github.io/ai-testpilot-x/ci-cd/)
- [10-Agent Pipeline](https://sagar-grv.github.io/ai-testpilot-x/agents/)

---

## CLI Commands

### `testpilot init` — Setup wizard

Creates `testpilot.yaml` in your project with your API key, target URL, and execution mode.

```bash
testpilot init
```

### `testpilot run` — Full pipeline

Runs the complete 10-agent pipeline: analyze → generate → execute → report.

```bash
testpilot run --story "User can login and checkout"
testpilot run --story "User can reset password" --url https://myapp.com --mode MOCK
testpilot run --story "Admin manages users" --output report.json
```

**Exit codes:**
- `0` = GO — all tests pass
- `1` = GO WITH RISK — high severity bugs
- `2` = NO GO — critical bugs, release blocked

### `testpilot analyze` — Test cases only

Generate test cases from a user story without executing them.

```bash
testpilot analyze --story "User can filter search results"
testpilot analyze --story "Payment flow" --output test_cases.json
```

### `testpilot bugs` — Bug analysis

Analyze any stack trace or error log with AI + RAG correlation.

```bash
testpilot bugs --log "NoSuchElementException: Unable to locate element: #login-btn"
testpilot bugs --log ./test-output.log
cat error.log | testpilot bugs --log -
```

### `testpilot report` — Release decision

Generate a GO/NO GO decision from existing execution results.

```bash
testpilot report results.json
testpilot report results.json --output release_report.json
```

### `testpilot dashboard` — Visual UI

Launch the full Streamlit dashboard (requires `pip install ai-testpilot-x[ui]`).

```bash
testpilot dashboard
testpilot dashboard --port 8080
```

---

## CI/CD Integration

Add AI TestPilot X as a quality gate to any CI pipeline. It exits with code `0` (pass) or `1`/`2` (fail), just like pytest or eslint.

### GitHub Actions

```yaml
# .github/workflows/ai-quality-gate.yml
name: AI Quality Gate
on: [push, pull_request]

jobs:
  quality-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: '3.11'}
      - run: pip install ai-testpilot-x
      - run: testpilot run --story "User can login and checkout"
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
```

### GitLab CI

```yaml
ai-quality-gate:
  stage: test
  script:
    - pip install ai-testpilot-x
    - testpilot run --story "User can login" --mode MOCK
  variables:
    GEMINI_API_KEY: $GEMINI_API_KEY
```

---

## Configuration (`testpilot.yaml`)

Place in your project root. Run `testpilot init` to generate automatically.

```yaml
gemini_api_key: ${GEMINI_API_KEY}   # reads from env var
execution_mode: MOCK                 # MOCK | LOCAL | GRID
target_url: https://your-app.com

db_url: sqlite:///.testpilot/testpilot.db
chroma_path: .testpilot/chroma_db
output_dir: .testpilot/reports
log_level: WARNING
```

---

## Python API

```python
from config import configure
configure(gemini_api_key="AIzaSy...", execution_mode="MOCK")

from api import run_pipeline, analyze, analyze_bug

# Full pipeline
result = run_pipeline("User can login and checkout", target_url="https://myapp.com")
print(result["report"]["decision"])  # "GO" | "GO_WITH_RISK" | "NO_GO"

# Test cases only
test_cases = analyze("User can reset their password")
for tc in test_cases:
    print(tc.id, tc.title, tc.type, tc.priority)

# Bug analysis
bug = analyze_bug("NoSuchElementException: #login-btn at LoginPage.py:42")
print(bug.severity, bug.root_cause, bug.fix_suggestion)
```

---

## Architecture

```
testpilot run --story "..."
       ↓
   LangGraph Orchestrator
   GlobalState + Checkpointing
       ↓
┌──────────────┬──────────────┐
│              │              │
▼              ▼              ▼
Requirements  Selenium     API Tests
Agent         Agent         Agent
│              │              │
▼              ▼              ▼
Test Cases   Execution     Bug Agent
+ Coverage   (HITL Gate)   + Healing
                │
                ▼
          Report Agent
          GO / GO_WITH_RISK / NO_GO
```

### 10 AI Agents

| Agent | What it does |
|---|---|
| RequirementAgent | Parses user story → modules, risk areas, priority |
| TestCaseAgent | Generates structured test cases with RAG context |
| VerificationAgent | Coverage check, duplicate detection, edge case gaps |
| SeleniumAgent | Generates Python Selenium code per test case |
| APIAgent | Generates HTTP test suites with assertions |
| ExecutionAgent | HITL gate, trust domains, LOCAL/MOCK/GRID modes |
| BugAgent | Root cause analysis, RAG correlation, clustering |
| HealingAgent | Self-healing locators (ID → Name → data-* → CSS → XPath → AI) |
| ReportAgent | GO / GO_WITH_RISK / NO_GO decision engine |

---

## Features

| Feature | Status |
|---|---|
| AI Test Case Generation + Coverage Radar | ✅ |
| Selenium Script Generation | ✅ |
| API Test Generation + Live Execution | ✅ |
| Human-in-the-Loop Execution Gate | ✅ |
| Bug Analysis with RAG Correlation | ✅ |
| Self-Healing Locator Recovery | ✅ |
| GO / GO_WITH_RISK / NO_GO Release Decision | ✅ |
| CLI with Rich terminal output | ✅ |
| CI/CD exit code integration | ✅ |
| Streamlit visual dashboard | ✅ |
| Python API | ✅ |
| LangGraph stateful orchestration | ✅ |

---

## Tech Stack

| Layer | Technologies |
|---|---|
| CLI | Typer + Rich |
| AI Orchestration | LangGraph 0.3, LangChain 0.3 |
| LLM | Google Gemini 2.5 Flash |
| RAG | ChromaDB, sentence-transformers (all-MiniLM-L6-v2) |
| UI | Streamlit 1.40+, Plotly, streamlit-agraph |
| Execution | Selenium 4, webdriver-manager, httpx |
| Storage | SQLAlchemy + SQLite |
| Validation | Pydantic v2 |
| Observability | LangSmith, loguru |

---

## Quick Start (Local Development)

```bash
git clone https://github.com/sagar-grv/ai-testpilot-x
cd ai-testpilot-x

python -m venv .venv
.venv\Scripts\activate   # Windows
source .venv/bin/activate  # macOS/Linux

pip install -r requirements.txt

# Initialize config
python -m cli.main init

# Run pipeline
python -m cli.main run --story "User can login and checkout"

# Or launch the dashboard
streamlit run app.py
```

---

## License

MIT
