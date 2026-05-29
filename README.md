# AI TestPilot X

> Autonomous AI-Powered Quality Engineering Platform

**Status:** Under active development

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env
# Add GEMINI_API_KEY to .env
streamlit run app.py
```

## Tech Stack
- LangGraph 0.3 + LangChain 0.3 + Gemini 1.5 Flash
- ChromaDB + sentence-transformers
- Selenium 4 + Streamlit 1.40+
- SQLAlchemy + SQLite + Pydantic v2
