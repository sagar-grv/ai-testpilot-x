# AI TestPilot X

A Python QA-workflow CLI and Streamlit interface using LangGraph and retrieval-assisted model calls. It turns user stories into test-case proposals, execution results, bug summaries and release recommendations.

Generated tests and GO/NO GO recommendations require review. A mock execution is not evidence that an application passed real browser tests.

## Workflow

```text
story -> requirements -> test cases -> execution -> bug analysis -> release report
```

The repository includes model adapters, schemas, storage/memory modules, Selenium execution support, API/CLI entry points and documentation.

## Install from source

Requires Python 3.11+.

```bash
git clone https://github.com/sagar-grv/ai-testpilot-x.git
cd ai-testpilot-x
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -e '.[ui,selenium,dev]'
```

Configure your own `GEMINI_API_KEY` and any optional model/observability settings. Model calls may incur provider charges. Do not commit keys, target credentials or sensitive execution logs. `testpilot init` creates a configuration file; review it before sharing.

## Start with mock execution

```bash
testpilot run --story 'User can reset a password' --mode MOCK
testpilot analyze --story 'User can filter search results'
testpilot dashboard
```

The default execution mode in `config.py` is `MOCK`. `LOCAL` and `GRID` are browser-execution modes; use them only on applications you are authorized to test. `SELENIUM_GRID_URL` controls the remote grid endpoint.

Other commands include `testpilot bugs`, `testpilot report` and `testpilot init`. Use `testpilot --help` and the repository's `docs/` for arguments and exit-code details.

## Checks

```bash
pytest
```

This audit did not run the full suite or regenerate a test-count badge. Remove the old static '72 Passing' badge unless it is replaced by a current CI result.

## Boundaries

- Generated coverage percentages and sample console output are illustrative unless backed by a saved run.
- Mock-mode results do not measure real UI reliability.
- Locator repair and AI analysis can be wrong. Review generated actions and reports before making a release decision.
- Browser tests can change application data; use a controlled test environment.
- Optional Playwright dependencies in packaging do not by themselves establish a completed Playwright execution path.

See [getting started](docs/getting-started.md), [configuration](docs/configuration.md), [architecture](docs/architecture.md), [CLI reference](docs/cli-reference.md) and [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE).
