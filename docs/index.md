---
hide:
  - navigation
  - toc
---

<div class="tp-hero">
  <div class="tp-hero__title">AI TestPilot X</div>
  <div class="tp-hero__subtitle">
    One command. A plain-English user story in. Full QA pipeline out.<br>
    10 AI agents, GO/NO GO release decisions, CI/CD native.
  </div>

  <div class="tp-hero__terminal">
    <span class="prompt">$</span> <span class="cmd">pip install ai-testpilot-x</span><br>
    <span class="prompt">$</span> <span class="cmd">testpilot run --story "User can login and checkout"</span><br><br>
    <span class="out">  Analyzing requirements...   </span><span class="go">done</span>  <span class="out">3 modules</span><br>
    <span class="out">  Generating test cases...    </span><span class="go">done</span>  <span class="out">12 test cases</span><br>
    <span class="out">  Verifying coverage...       </span><span class="go">done</span>  <span class="out">87% coverage</span><br>
    <span class="out">  Executing tests (MOCK)...   </span><span class="go">done</span>  <span class="out">10 passed · 2 failed</span><br>
    <span class="out">  Analyzing bugs...           </span><span class="go">done</span>  <span class="out">2 bugs found</span><br>
    <span class="out">  Generating report...        </span><span class="go">done</span><br><br>
    <span class="out">  Release Decision: </span><span class="risk">GO WITH RISK</span>  <span class="out">exit 1</span>
  </div>
</div>

## Why AI TestPilot X?

<div class="tp-features">
  <div class="tp-feature">
    <div class="tp-feature__icon">🧠</div>
    <div class="tp-feature__title">AI-Generated Tests</div>
    <div class="tp-feature__desc">From a plain-English user story to structured test cases, Selenium scripts, and API tests in seconds.</div>
  </div>
  <div class="tp-feature">
    <div class="tp-feature__icon">🔁</div>
    <div class="tp-feature__title">Self-Healing Locators</div>
    <div class="tp-feature__desc">7-level fallback hierarchy. Tests recover from UI changes automatically without manual maintenance.</div>
  </div>
  <div class="tp-feature">
    <div class="tp-feature__icon">🐛</div>
    <div class="tp-feature__title">RAG Bug Analysis</div>
    <div class="tp-feature__desc">Drop in a stack trace. Get root cause, similar historical bugs, fix suggestions — all AI-correlated.</div>
  </div>
  <div class="tp-feature">
    <div class="tp-feature__icon">🚦</div>
    <div class="tp-feature__title">GO / NO GO Decisions</div>
    <div class="tp-feature__desc">Automated release gate. Exit code 0/1/2 integrates natively with GitHub Actions, GitLab CI, Jenkins.</div>
  </div>
  <div class="tp-feature">
    <div class="tp-feature__icon">🧩</div>
    <div class="tp-feature__title">10-Agent Pipeline</div>
    <div class="tp-feature__desc">LangGraph-orchestrated. Each agent is stateful, checkpointed, and independently verifiable.</div>
  </div>
  <div class="tp-feature">
    <div class="tp-feature__icon">👁️</div>
    <div class="tp-feature__title">Human-in-the-Loop</div>
    <div class="tp-feature__desc">Approval gate before execution. CI auto-approves. Streamlit dashboard shows a confirmation button.</div>
  </div>
</div>

## Quick Install

=== "pip"

    ```bash
    pip install ai-testpilot-x
    ```

=== "With dashboard"

    ```bash
    pip install ai-testpilot-x[ui]
    ```

=== "Everything"

    ```bash
    pip install ai-testpilot-x[all]
    ```

=== "From source"

    ```bash
    git clone https://github.com/sagar-grv/ai-testpilot-x
    cd ai-testpilot-x
    pip install -e .
    ```

## Five commands

| Command | What it does |
|---|---|
| `testpilot init` | Interactive setup — writes `testpilot.yaml` |
| `testpilot run` | Full 10-agent pipeline → GO/NO GO decision |
| `testpilot analyze` | Test case generation only, no execution |
| `testpilot bugs` | AI + RAG bug analysis from a log or stack trace |
| `testpilot report` | Release decision from existing results JSON |
| `testpilot dashboard` | Launch the Streamlit visual dashboard |

## Install the AI Agent Skill

Any AI coding agent (Claude Code, Cursor, OpenCode, Copilot) can learn to use AI TestPilot X:

```bash
npx skills add sagar-grv/ai-testpilot-x
```

After installing, your agent understands all CLI commands, the 10-agent pipeline, exit code semantics, and self-healing locator patterns.

## Links

- **Live Dashboard:** [ai-testpilot-x.streamlit.app](https://ai-testpilot-x.streamlit.app/)
- **GitHub:** [sagar-grv/ai-testpilot-x](https://github.com/sagar-grv/ai-testpilot-x)
- **PyPI:** [ai-testpilot-x](https://pypi.org/project/ai-testpilot-x/)
