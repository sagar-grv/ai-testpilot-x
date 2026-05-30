# Getting Started

Get from zero to a running QA pipeline in under 5 minutes.

## Prerequisites

- Python 3.11+
- A [Gemini API key](https://aistudio.google.com/app/apikey) (free tier works)

## 1. Install

```bash
pip install ai-testpilot-x
```

For the visual Streamlit dashboard:

```bash
pip install ai-testpilot-x[ui]
```

For real browser (Selenium) execution:

```bash
pip install ai-testpilot-x[selenium]
```

## 2. Initialize your project

Run the setup wizard in your project directory:

```bash
cd your-project/
testpilot init
```

This creates `testpilot.yaml` with your API key, target URL, and execution mode:

```yaml
# testpilot.yaml
gemini_api_key: ${GEMINI_API_KEY}   # reads from env var
execution_mode: MOCK                 # MOCK | LOCAL | GRID
target_url: https://your-app.com

db_url: sqlite:///.testpilot/testpilot.db
chroma_path: .testpilot/chroma_db
output_dir: .testpilot/reports
log_level: WARNING
```

!!! tip "API Key"
    Store your key as an environment variable — never hardcode it:
    ```bash
    export GEMINI_API_KEY="AIzaSy..."
    ```
    Or add it to a `.env` file (which is gitignored by default).

## 3. Run your first pipeline

```bash
testpilot run --story "User can log in with valid credentials"
```

You'll see a live progress display as each agent completes:

```
  Analyzing requirements...   done  2 modules
  Generating test cases...    done  8 test cases
  Verifying coverage...       done  92% coverage
  Executing tests (MOCK)...   done  8 passed · 0 failed
  Analyzing bugs...           done  0 bugs
  Generating report...        done

  Release Decision:  GO          exit 0
  Risk Score:        12 / 100
  Tests:             8 / 8 passed
```

## 4. Execution modes

| Mode | When to use | Requirements |
|---|---|---|
| `MOCK` | CI/CD, cloud, no real app | None — returns simulated results |
| `LOCAL` | Local dev with app running | Chrome + ChromeDriver installed |
| `GRID` | Parallel real browser testing | Selenium Grid endpoint |

```bash
# Mock (default for CI)
testpilot run --story "..." --mode MOCK

# Local Selenium
testpilot run --story "..." --mode LOCAL --url http://localhost:3000

# Selenium Grid
testpilot run --story "..." --mode GRID --url https://staging.myapp.com
```

## 5. Analyze test cases without executing

```bash
testpilot analyze --story "User can reset their password"
```

Outputs a table of test cases with priority, type, and steps — no execution needed.

## 6. Analyze a bug

```bash
testpilot bugs --log "NoSuchElementException: Unable to locate element: #login-btn at LoginPage.py:42"
```

Returns root cause, severity, and fix suggestion with RAG correlation against historical bugs.

## 7. Launch the visual dashboard

```bash
testpilot dashboard
```

Opens the Streamlit dashboard at `http://localhost:8501` with all 8 pages:
Test Generator, Selenium Generator, API Tester, Bug Analyzer, Reports, Workflow Studio, Knowledge Base.

## Next steps

- [CLI Reference](cli-reference.md) — all commands and flags
- [Architecture](architecture.md) — how the 10-agent pipeline works
- [CI/CD Integration](ci-cd.md) — GitHub Actions, GitLab CI examples
