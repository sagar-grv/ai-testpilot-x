# AI TestPilot X

> Autonomous AI-Powered Quality Engineering Platform

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-red)
![LangGraph](https://img.shields.io/badge/LangGraph-0.3.x-green)
![Gemini](https://img.shields.io/badge/Gemini-1.5--Flash-yellow)
![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen)

## Overview

AI TestPilot X is an autonomous quality engineering platform that transforms a plain-English user story into a complete test suite, executes it, analyzes failures, and produces an executive report — all through a stateful 10-agent LangGraph pipeline with human-in-the-loop controls.

## Architecture

```
Frontend (Streamlit — 8 pages)
           ↓
   LangGraph Orchestrator
   GlobalState + Checkpointing
           ↓
┌──────────┼──────────┐
│          │          │
▼          ▼          ▼
Test     Selenium   API
Agents   Agent      Agent
│          │          │
▼          ▼          ▼
ChromaDB  Selenium  httpx
RAG       Grid/Local Runner
           ↓
    SQLite Storage
           ↓
  Executive Dashboard
```

## Features

| Feature | Status |
|---|---|
| Requirement Analysis Agent | ✅ |
| AI Test Case Generation + Coverage Radar | ✅ |
| Test Verification (coverage, edge cases) | ✅ |
| Selenium Script Generation | ✅ |
| API Test Generation + Live Execution | ✅ |
| Human-in-the-Loop Execution Gate | ✅ |
| Trust Domain Management | ✅ |
| Bug Analysis with RAG Correlation | ✅ |
| Bug Clustering by Root Cause | ✅ |
| Self-Healing Locator Recovery | ✅ |
| Executive Report (GO / GO_WITH_RISK / NO_GO) | ✅ |
| Workflow Studio (Live Agent Graph) | ✅ |
| Knowledge Base (ChromaDB search + ingestion) | ✅ |
| LangSmith Tracing | ✅ |
| Agent Performance Metrics | ✅ |
| Explain AI Decision | ✅ |

## Platform Pages

| Page | Description |
|---|---|
| Home | System health, last release decision, agent activity feed |
| AI Test Generator | User story → requirements → test cases → verification |
| Selenium Generator | Script gen, HITL gate, self-healing panel |
| API Tester | API test generation + live execution + Postman export |
| Bug Analyzer | Log analysis, RAG-backed root cause, fix suggestions |
| Reports | Engineer/Executive views, GO/NO GO decision, charts |
| Workflow Studio | Live LangGraph graph, GlobalState inspector |
| Knowledge Base | ChromaDB search, document ingestion |

## Quick Start

```bash
git clone https://github.com/your-username/ai-testpilot-x
cd ai-testpilot-x

python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env — add your GEMINI_API_KEY

streamlit run app.py
```

Open: **http://localhost:8501**

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `GEMINI_API_KEY` | Yes | — | Google AI Studio API key |
| `EXECUTION_MODE` | No | MOCK | `LOCAL`, `MOCK`, or `GRID` |
| `SELENIUM_GRID_URL` | Grid only | `http://localhost:4444/wd/hub` | Grid hub URL |
| `LANGSMITH_API_KEY` | No | — | LangSmith tracing |
| `LANGSMITH_TRACING` | No | false | Enable tracing |

## Selenium Grid (Real Execution)

```bash
docker-compose up -d
# Set EXECUTION_MODE=GRID in .env
```

## Tech Stack

| Layer | Technologies |
|---|---|
| AI Orchestration | LangGraph 0.3, LangChain 0.3 |
| LLM | Google Gemini 1.5 Flash |
| RAG | ChromaDB, sentence-transformers (all-MiniLM-L6-v2) |
| UI | Streamlit 1.40+, Plotly, streamlit-agraph |
| Execution | Selenium 4, webdriver-manager, httpx |
| Storage | SQLAlchemy + SQLite |
| Validation | Pydantic v2 |
| Observability | LangSmith, loguru |

## Agents

| Agent | Role |
|---|---|
| RequirementAgent | Parses user story → modules, risk areas, priority |
| TestCaseAgent | Generates structured test cases with RAG context |
| VerificationAgent | Coverage check, duplicate detection, edge case gaps |
| SeleniumAgent | Generates Python Selenium code per test case |
| APIAgent | Generates HTTP test suites, supports live execution |
| ExecutionAgent | HITL gate, trust domains, LOCAL/MOCK/GRID modes |
| BugAgent | Root cause analysis, RAG correlation, clustering |
| HealingAgent | Self-healing locators (ID→Name→data-*→CSS→XPath→AI) |
| ReportAgent | GO / GO_WITH_RISK / NO_GO decision engine |

## Resume Entry

> Architected and developed an autonomous AI-driven software testing platform integrating Selenium WebDriver, Streamlit, LangGraph, LangChain, and Gemini/Google AI APIs. Designed a 10-agent multi-agent architecture with stateful LangGraph workflows, checkpointing, and human-in-the-loop approval gates. Implemented retrieval-augmented generation (RAG) pipelines using ChromaDB and sentence-transformers for context-aware test creation and bug correlation. Built intelligent bug clustering, self-healing locator recovery, and deterministic GO/NO_GO release decision engine.

## License

MIT
