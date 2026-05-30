"""testpilot report — Generate a GO/NO GO release decision from test results."""

from __future__ import annotations
import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

EXIT_GO = 0
EXIT_GO_WITH_RISK = 1
EXIT_NO_GO = 2


def report_cmd(
    results: Path = typer.Argument(
        ..., help="Path to execution results JSON (ExecutionSchema format)."
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Save release report JSON to this file."
    ),
    config: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Path to testpilot.yaml."
    ),
    session: Optional[str] = typer.Option(None, "--session", help="Session ID."),
):
    """Generate a GO/NO GO release decision from existing test results.

    Reads an ExecutionSchema JSON file, runs BugAgent + ReportAgent,
    and prints the release decision.

    Useful in CI after running your own test suite — just serialize the
    results to JSON and pipe through testpilot report.

    [dim]Exit codes:[/dim]
      [green]0[/green] = GO
      [yellow]1[/yellow] = GO WITH RISK
      [red]2[/red] = NO GO
    """
    try:
        from config import load_yaml_config, reload_settings

        load_yaml_config(config)
        reload_settings()
    except Exception:
        pass

    if not results.exists():
        console.print(f"[red]Error:[/red] File not found: {results}")
        raise typer.Exit(1)

    try:
        data = json.loads(results.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        console.print(f"[red]Error:[/red] Invalid JSON: {e}")
        raise typer.Exit(1)

    console.print()
    console.print(
        Panel.fit(
            "[bold cyan]AI TestPilot X[/bold cyan]  ·  Release Report",
            border_style="cyan",
        )
    )
    console.print()

    sid = session or "cli-report"

    with Progress(
        SpinnerColumn(spinner_name="dots", style="cyan"),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as prog:
        t = prog.add_task("Running bug analysis...", total=None)
        from agents.bug_agent import BugAgent
        from schemas.execution_schema import ExecutionSchema

        try:
            exec_schema = ExecutionSchema(**data)
        except Exception as e:
            prog.stop()
            console.print(f"[red]Error parsing results:[/red] {e}")
            raise typer.Exit(1)

        bugs, clusters = BugAgent().run(exec_schema, session_id=sid)

        prog.update(t, description="Generating release decision...")
        from agents.report_agent import ReportAgent

        report = ReportAgent().run(exec_schema, bugs, clusters, session_id=sid)

    decision = report.decision
    risk_score = report.risk_score

    BANNERS = {
        "GO": ("green", "✅", "GO", "Release approved."),
        "GO_WITH_RISK": (
            "yellow",
            "⚠️ ",
            "GO WITH RISK",
            "High severity issues. Proceed with caution.",
        ),
        "NO_GO": ("red", "🚫", "NO GO", "Critical bugs detected. Release blocked."),
    }
    color, icon, label, subtitle = BANNERS.get(decision, BANNERS["NO_GO"])

    console.print(
        Panel(
            f"{icon}  [bold {color}]{label}[/bold {color}]\n\n"
            f"[dim]Risk Score[/dim]   [bold]{risk_score:.0f} / 100[/bold]\n"
            f"[dim]Tests[/dim]        [green]{report.passed}[/green] / {report.total_tests} passed\n"
            f"[dim]Bugs[/dim]         "
            f"[red]{report.critical_bugs} critical[/red]  "
            f"[yellow]{report.high_bugs} high[/yellow]  "
            f"[dim]{report.medium_bugs} medium  {report.low_bugs} low[/dim]\n\n"
            + (
                f"[italic dim]{report.recommendation_text}[/italic dim]"
                if report.recommendation_text
                else ""
            ),
            title="[bold]Release Decision[/bold]",
            border_style=color,
            expand=False,
        )
    )

    if output:
        output.write_text(json.dumps(report.model_dump(), indent=2), encoding="utf-8")
        console.print()
        console.print(f"[dim]Saved → [cyan]{output}[/cyan][/dim]")

    console.print()

    exit_map = {"GO": EXIT_GO, "GO_WITH_RISK": EXIT_GO_WITH_RISK, "NO_GO": EXIT_NO_GO}
    raise typer.Exit(exit_map.get(decision, EXIT_NO_GO))
