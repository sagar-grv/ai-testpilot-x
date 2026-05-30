# Changelog

## v1.0.0 — 2026-05-30

Initial production release.

### Features

**10-agent AI pipeline**

- `RequirementAgent` — parses user stories into structured modules and risk areas
- `TestCaseAgent` — generates UI, API, and edge case test cases with RAG enrichment
- `VerificationAgent` — coverage analysis, duplicate detection, gap identification
- `SeleniumAgent` — generates executable Python Selenium scripts per test case
- `APIAgent` — generates httpx HTTP test suites with full assertions
- `ExecutionAgent` — MOCK / LOCAL / GRID execution with HITL approval gate
- `BugAgent` — root cause analysis with RAG correlation and clustering
- `HealingAgent` — 7-level self-healing locator recovery
- `ReportAgent` — GO / GO_WITH_RISK / NO_GO release decision engine

**CLI (`testpilot`)**

- `testpilot init` — interactive setup wizard, writes `testpilot.yaml`
- `testpilot run` — full pipeline with exit codes 0/1/2
- `testpilot analyze` — test case generation only
- `testpilot bugs` — AI + RAG bug analysis
- `testpilot report` — release decision from results JSON
- `testpilot dashboard` — Streamlit visual dashboard

**Python API**

- `run_pipeline()`, `analyze()`, `analyze_bug()`, `generate_report()`, `configure()`
- All Pydantic v2 schemas re-exported as public API surface

**Storage**

- SQLite via SQLAlchemy (6 tables, PostgreSQL-ready via URL swap)
- ChromaDB embedded RAG (4 collections, all-MiniLM-L6-v2)

**Observability**

- LangSmith tracing (optional, free tier)
- Loguru structured logging

**Deployment**

- Streamlit Cloud (live at ai-testpilot-x.streamlit.app)
- Docker Compose for Selenium Grid
- `pyproject.toml` with optional extras: `ui`, `selenium`, `playwright`, `docs`, `all`

**CI/CD**

- GitHub Actions workflow examples
- GitLab CI example
- Jenkins Declarative Pipeline example

### Known limitations (V2 roadmap)

- `RiskAgent` — deferred to V2 (stub present)
- `OptimizationAgent` — deferred to V2 (stub present)
- PostgreSQL — supported via `DB_URL` env var, not tested in CI yet
- Playwright execution — stub only, not wired to execution graph
- PyPI publish — package installable from source, PyPI release pending
