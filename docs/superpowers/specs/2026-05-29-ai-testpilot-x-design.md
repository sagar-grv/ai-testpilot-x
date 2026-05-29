# AI TestPilot X — Design Specification
**Date:** 2026-05-29
**Status:** Approved
**Primary LLM:** Gemini (Google)
**Deployment:** Local (dev) + Streamlit Cloud (prod)

---

## 1. Vision

An autonomous AI-powered quality engineering platform where QA engineers input a user story and the system generates test cases, Selenium scripts, API tests, executes them, analyzes failures, and produces executive reports — all orchestrated through a stateful multi-agent pipeline with human-in-the-loop controls.

---

## 2. Project Structure

```
ai-testpilot-x/
├── app.py
├── orchestrator.py
├── config.py
├── agents/
│   ├── base_agent.py
│   ├── requirement_agent.py
│   ├── testcase_agent.py
│   ├── verification_agent.py
│   ├── selenium_agent.py
│   ├── api_agent.py
│   ├── execution_agent.py
│   ├── bug_agent.py
│   ├── healing_agent.py
│   ├── optimization_agent.py  (V2 stub)
│   ├── risk_agent.py          (V2 stub)
│   ├── report_agent.py
│   └── registry.py
├── core/
│   ├── llm_client.py
│   ├── rag_engine.py
│   ├── event_bus.py
│   ├── explain_engine.py
│   └── screenshot_utils.py
├── models/
│   ├── base_model.py
│   ├── gemini.py
│   ├── openai.py  (stub)
│   └── claude.py  (stub)
├── schemas/
│   ├── requirement_schema.py
│   ├── testcase_schema.py
│   ├── verification_schema.py
│   ├── test_result_schema.py
│   ├── execution_schema.py
│   ├── api_test_schema.py
│   ├── bug_schema.py
│   ├── report_schema.py
│   ├── error_schema.py
│   └── global_state.py
├── prompts/
│   ├── requirement_prompt.txt
│   ├── testcase_prompt.txt
│   ├── verification_prompt.txt
│   ├── selenium_prompt.txt
│   ├── api_prompt.txt
│   ├── bug_prompt.txt
│   ├── healing_prompt.txt
│   └── report_prompt.txt
├── memory/
│   ├── conversation_memory.py
│   ├── execution_memory.py
│   └── bug_memory.py
├── execution/
│   ├── runners/
│   │   ├── selenium_runner.py
│   │   ├── playwright_runner.py (stub)
│   │   └── api_runner.py
│   ├── grids/
│   │   └── selenium_grid.py
│   └── artifacts/
│       ├── screenshots/
│       ├── videos/
│       └── logs/
├── storage/
│   ├── db.py
│   └── models/
│       ├── requirements.py
│       ├── testcases.py
│       ├── executions.py
│       ├── bugs.py
│       ├── reports.py
│       └── trust_domains.py
├── knowledge/
│   ├── requirements/
│   ├── bugs/
│   ├── screenshots/
│   ├── api_docs/
│   └── testcases/
├── monitoring/
│   ├── logger.py
│   ├── metrics.py
│   └── tracing.py
├── pages/
│   ├── 01_home.py
│   ├── 02_test_generator.py
│   ├── 03_selenium_generator.py
│   ├── 04_api_tester.py
│   ├── 05_bug_analyzer.py
│   ├── 06_reports.py
│   ├── 07_workflow_studio.py
│   └── 08_knowledge_base.py
├── tests/
│   ├── test_agents.py
│   ├── test_schemas.py
│   ├── test_storage.py
│   ├── test_llm_client.py
│   ├── test_config.py
│   └── test_execution.py
├── .github/
│   └── workflows/
│       └── testpilot-ci.yml
├── docker-compose.yml
├── .env.example
├── requirements.txt
└── README.md
```

---

## 3. Agent Architecture

### 3.1 Base Agent Interface

Every agent implements:
```python
class BaseAgent:
    def run(self, input: PydanticSchema, memory: MemoryContext) -> PydanticSchema
    def _build_prompt(self, input) -> str          # loads from prompts/
    def _call_llm(self, prompt) -> str             # via core/llm_client.py
    def _parse_output(self, raw) -> PydanticSchema # validated via schemas/
```

All outputs include a `confidence_score: float` field (0.0–1.0).
On failure: retry once, then emit AGENT_FAILED event with ErrorSchema.

### 3.2 AgentRegistry

```python
class AgentRegistry:
    @classmethod
    def register(cls, name: str, agent_class): ...
    @classmethod
    def get(cls, name: str): ...
    @classmethod
    def list_agents(cls) -> list[str]: ...
```

All 9 V1 agents registered in `agents/__init__.py`.

### 3.3 Agent Sequence (V1 MVP)

```
[1]  RequirementAgent      → RequirementSchema
[2]  TestCaseAgent         → list[TestCaseSchema]    (RAG: testcases collection)
[2.5] VerificationAgent    → VerificationSchema      (retry loop max 2)
[3]  SeleniumAgent    ─┐   → selenium_scripts dict   (parallel, event-triggered)
[4]  APIAgent         ─┤   → api_test_suite dict
[5]  ExecutionAgent    ←── HITL gate (trust domain aware)
                       → ExecutionSchema
[6]  BugAgent          → list[BugSchema] + list[BugClusterSchema]  (RAG: bugs collection)
[7]  HealingAgent      → healing_results dict  (conditional: NoSuchElement bugs only)
[8]  ReportAgent       → ReportSchema          (GO / GO_WITH_RISK / NO_GO)
```

V2 agents (OptimizationAgent, RiskAgent) are stubbed.

### 3.4 GlobalState (TypedDict)

```python
class GlobalState(TypedDict, total=False):
    session_id: str
    session_metadata: dict
    requirement_context: Optional[RequirementSchema]
    generated_testcases: Optional[list[TestCaseSchema]]
    verification_report: Optional[VerificationSchema]
    execution_plan: Optional[str]
    selenium_scripts: Optional[dict]       # {tc_id: code_string}
    api_test_suite: Optional[dict]         # {module: list[APITestResultSchema]}
    execution_results: Optional[ExecutionSchema]
    bugs: Optional[list[BugSchema]]
    bug_clusters: Optional[list[BugClusterSchema]]
    healing_results: Optional[dict]
    risk_analysis: Optional[dict]          # V2, nullable
    report: Optional[ReportSchema]
    checkpoint: Optional[dict]
    agent_errors: Optional[list[ErrorSchema]]
```

### 3.5 Event Bus Events (V1)

```python
class EventType(str, Enum):
    REQUIREMENT_ANALYZED = "REQUIREMENT_ANALYZED"
    TESTCASES_GENERATED = "TESTCASES_GENERATED"
    VERIFICATION_COMPLETE = "VERIFICATION_COMPLETE"
    EXECUTION_APPROVED = "EXECUTION_APPROVED"
    EXECUTION_COMPLETE = "EXECUTION_COMPLETE"
    BUG_ANALYZED = "BUG_ANALYZED"
    HEALING_COMPLETE = "HEALING_COMPLETE"
    REPORT_GENERATED = "REPORT_GENERATED"
    AGENT_FAILED = "AGENT_FAILED"
```

---

## 4. HITL Execution Gate

1. AI generates test plan and code
2. Streamlit shows: test cases + generated code + target URL + trust domain status
3. User selects: **Approve Once** / **Approve Always** / **Reject**
4. Trust domains stored in SQLite `trust_domains` table — survive session restart
5. "Approve Always": inserts domain into trust_domains table
6. Reject: saves checkpoint to GlobalState.checkpoint, shows edit UI
7. Only on Approve → execution fires

---

## 5. Self-Healing Locator Hierarchy

Order tried: `id` → `name` → `data-testid` → `data-cy` → `css_selector` → `xpath` → `semantic_ai`
Each attempt logged. Stops at first successful suggestion.

---

## 6. RAG Layer

- **Embedding model:** `all-MiniLM-L6-v2` (sentence-transformers)
- **Chunk size:** 512 words, overlap 50
- **Collections:** `testcases`, `bugs`, `requirements`, `reports`
- **No-match fallback:** agent proceeds without RAG context, logs warning
- **Ingestion:** `knowledge/` subdirs → embed → ChromaDB persistent store

RAG used only where historical context improves quality:

| Agent | Collection |
|---|---|
| TestCaseAgent | testcases |
| BugAgent | bugs |
| SeleniumAgent | testcases (for selector patterns) |
| ReportAgent | reports |

---

## 7. Bug Intelligence

BugAgent output per failed test:
- `failure_signature`: extracted from error message (first line, underscored, max 50 chars)
- `severity` + `severity_confidence`
- `priority`
- `root_cause` + `root_cause_confidence`
- `fix_suggestion` + `fix_confidence`
- `rag_matches`: list of similar past bugs with similarity scores

**Bug clustering:** group by first keyword of `root_cause`. Output: `list[BugClusterSchema]`

---

## 8. Report Generation

Decision logic (deterministic, no LLM):
- **NO_GO:** any Critical severity bug
- **GO_WITH_RISK:** any High severity, no Critical
- **GO:** only Medium/Low bugs, or zero bugs

LLM generates `recommendation_text` and `risk_score` only.

---

## 9. UI Pages (8 Pages)

| Page | Name | Key Features |
|---|---|---|
| 01 | Home Dashboard | System health (Gemini/ChromaDB/Grid), workflow graph, agent metrics, release banner, event feed |
| 02 | AI Test Generator | User story → requirements → test cases, coverage radar, edge cases, Explain AI |
| 03 | Selenium Generator | Script gen, execution mode selector, HITL gate with trust domains, self-healing panel |
| 04 | API Tester | Mock/live mode, schema validation, API risk score, cURL/Postman export |
| 05 | Bug Analyzer | Log input, bug report, failure timeline, RAG similarity, per-field confidence |
| 06 | Reports | Engineer/Executive toggle, charts, regression intelligence, agent performance |
| 07 | Workflow Studio | Live streamlit-agraph graph, node states, checkpoint controls, GlobalState inspector |
| 08 | Knowledge Base | Browse artifacts, ChromaDB search, ingestion panel, similarity results |

Global Command Bar (Ctrl+K) on all pages.

---

## 10. Tech Stack

```
google-generativeai>=0.8
langchain==0.3.*
langgraph==0.3.*
langchain-google-genai>=2.0
sentence-transformers>=3.0
chromadb>=0.5
streamlit>=1.40
plotly>=5.0
streamlit-agraph>=0.0.45
streamlit-ace>=0.1.1
selenium>=4.0
webdriver-manager>=4.0
playwright>=1.40  (stub)
httpx>=0.27
pytest>=8.0
pytest-html>=4.0
sqlalchemy>=2.0
alembic>=1.13
pydantic>=2.0
pydantic-settings>=2.0
python-dotenv>=1.0
pypdf>=4.0
python-docx>=1.0
langsmith>=0.1
loguru>=0.7
black>=24.0
ruff>=0.4
pre-commit>=3.0
```

---

## 11. Implementation Phases

- **Phase 0.5** (0.5 days): Architecture spike — Gemini + Pydantic + LangGraph + Streamlit
- **Phase 1** (Days 1-3): Foundation — structure, config, SQLite, ChromaDB, LLM client, event bus, Streamlit skeleton, CI
- **Phase 2** (Days 4-8): Core agents — all schemas, prompts, BaseAgent, RequirementAgent, TestCaseAgent, VerificationAgent, Page 02, Page 08
- **Phase 3** (Days 9-13): Automation — SeleniumAgent, selenium_runner, grid connector, ExecutionAgent HITL, HealingAgent, Page 03
- **Phase 4** (Days 14-17): API + Bug — APIAgent, BugAgent (RAG + clustering), ingestion pipeline, Page 04, Page 05
- **Phase 5** (Days 18-21): Reporting + Orchestration — ReportAgent, LangGraph graph, AgentRegistry, Page 06, Page 07, Page 01
- **Phase 6** (Days 22-25): Polish + Deploy — MOCK mode, Docker Compose, Streamlit Cloud, Explain AI, final tests, README

---

## 12. MVP Boundary

**V1 — Must Ship:** RequirementAgent, TestCaseAgent, VerificationAgent, SeleniumAgent, APIAgent, ExecutionAgent (HITL), BugAgent (RAG + clustering), HealingAgent, ReportAgent, all 8 UI pages, ChromaDB RAG, SQLite, LangSmith, CI

**V2:** RiskAgent, OptimizationAgent, Playwright, BrowserStack, Visual AI testing, Voice commands, PostgreSQL

---

## 13. Known Hard Problems

1. **Agent contracts** — Pydantic at every LLM boundary, no raw text between agents
2. **State management** — GlobalState is single source of truth
3. **Workflow orchestration** — LangGraph subgraphs (Selenium flow, API flow separate)
4. **Reliable structured outputs** — Gemini JSON fallback + retry on parse failure
5. **Self-healing logic** — locator hierarchy tried in order, each attempt logged

---

## 14. Deployment Notes

- **Local:** Full Chrome execution via `webdriver-manager`
- **Cloud:** Streamlit Cloud for UI + MOCK mode; real execution via Docker Selenium Grid on VPS
- **Env vars:** `GEMINI_API_KEY`, `LANGSMITH_API_KEY`, `SELENIUM_GRID_URL`, `EXECUTION_MODE` (LOCAL/MOCK/GRID), `APP_ENV`
