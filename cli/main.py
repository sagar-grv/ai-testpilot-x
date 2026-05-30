"""CLI main entry point — AI TestPilot X."""
import os
import sys
import typer
from typing import Optional

# Force UTF-8 output on Windows so Rich emoji render correctly
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

app = typer.Typer(
    name="testpilot",
    help="AI TestPilot X — Autonomous AI-powered QA for your projects.",
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

# ── Register sub-commands ─────────────────────────────────────────────────────
from cli.cmd_init import init_cmd
from cli.cmd_run import run_cmd
from cli.cmd_analyze import analyze_cmd
from cli.cmd_bugs import bugs_cmd
from cli.cmd_report import report_cmd
from cli.cmd_dashboard import dashboard_cmd

app.command("init",      help="Initialize a testpilot.yaml config in the current project.")(init_cmd)
app.command("run",       help="Run the full AI QA pipeline — analyze, generate, execute, report.")(run_cmd)
app.command("analyze",   help="Generate test cases from a user story (no execution).")(analyze_cmd)
app.command("bugs",      help="Analyze an error log or stack trace with AI + RAG.")(bugs_cmd)
app.command("report",    help="Generate a GO/NO GO release decision from test results.")(report_cmd)
app.command("dashboard", help="Launch the Streamlit visual dashboard.")(dashboard_cmd)


def version_callback(value: bool):
    if value:
        from rich.console import Console
        Console().print("[bold cyan]AI TestPilot X[/bold cyan] [dim]v1.0.0[/dim]")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v",
        callback=version_callback, is_eager=True,
        help="Show version and exit."
    ),
):
    """[bold cyan]AI TestPilot X[/bold cyan] — Autonomous AI-powered QA platform.

    [dim]GitHub:[/dim]    https://github.com/sagar-grv/ai-testpilot-x
    [dim]Live Demo:[/dim] https://ai-testpilot-x.streamlit.app/
    """


if __name__ == "__main__":
    app()
