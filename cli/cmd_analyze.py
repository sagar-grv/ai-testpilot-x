"""testpilot analyze — Generate test cases from a user story (no execution)."""

from __future__ import annotations
import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def analyze_cmd(
    story: str = typer.Option(
        ..., "--story", "-s", help="Plain-English user story to analyze."
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Save test cases to this JSON file."
    ),
    config: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Path to testpilot.yaml."
    ),
):
    """Analyze a user story and generate test cases.

    No test execution — just AI analysis + test case generation + coverage check.
    Perfect for planning sprints or reviewing test coverage.
    """
    try:
        from config import load_yaml_config, reload_settings

        load_yaml_config(config)
        reload_settings()
    except Exception:
        pass

    console.print()
    console.print(
        Panel.fit(
            "[bold cyan]AI TestPilot X[/bold cyan]  ·  Test Case Analysis",
            border_style="cyan",
        )
    )
    console.print()

    # ── Step 1: Requirements ──────────────────────────────────────────────────
    console.print("[dim]Analyzing requirements...[/dim]")
    from agents.requirement_agent import RequirementAgent

    req = RequirementAgent().run(story)

    console.print(
        f"[green]✓[/green]  Requirements  "
        f"[cyan]{len(req.modules)} modules[/cyan]  ·  "
        f"[yellow]{req.priority}[/yellow] priority  ·  "
        f"[dim]{req.confidence_score:.0%} confidence[/dim]"
    )

    # ── Step 2: Test cases ────────────────────────────────────────────────────
    console.print("[dim]Generating test cases...[/dim]")
    from agents.testcase_agent import TestCaseAgent

    test_cases = TestCaseAgent().run(req)

    console.print(
        f"[green]✓[/green]  Test cases    [cyan]{len(test_cases)} generated[/cyan]"
    )

    # ── Step 3: Verification ──────────────────────────────────────────────────
    console.print("[dim]Verifying coverage...[/dim]")
    from agents.verification_agent import VerificationAgent

    v = VerificationAgent().run(test_cases)
    cov_color = "green" if v.coverage_score >= 0.6 else "yellow"
    console.print(
        f"[green]✓[/green]  Coverage      "
        f"[{cov_color}]{v.coverage_score:.0%}[/{cov_color}]  "
        f"{'[green]PASS[/green]' if v.passed else '[yellow]BELOW THRESHOLD[/yellow]'}  "
        f"[dim]{v.duplicate_count} duplicates[/dim]"
    )
    console.print()

    # ── Requirements summary ──────────────────────────────────────────────────
    console.print(
        "[bold]Modules identified:[/bold]  "
        + "  ".join(f"[cyan]{m}[/cyan]" for m in req.modules)
    )
    if req.risk_areas:
        console.print(
            "[bold]Risk areas:[/bold]     "
            + "  ".join(f"[red]{r}[/red]" for r in req.risk_areas)
        )
    console.print()

    # ── Test case table ───────────────────────────────────────────────────────
    TYPE_COLORS = {
        "Positive": "green",
        "Negative": "red",
        "Security": "yellow",
        "Performance": "blue",
        "Boundary": "magenta",
        "Accessibility": "cyan",
    }
    PRIO_COLORS = {
        "Critical": "red",
        "High": "yellow",
        "Medium": "cyan",
        "Low": "green",
    }

    tbl = Table(
        title=f"[bold]{len(test_cases)} Test Cases[/bold]",
        border_style="dim",
        show_lines=False,
        padding=(0, 1),
    )
    tbl.add_column("ID", style="bold cyan", width=6)
    tbl.add_column("Title", style="white")
    tbl.add_column("Type", width=13)
    tbl.add_column("Priority", width=10)
    tbl.add_column("Steps", width=6, justify="right")

    for tc in test_cases:
        tc_color = TYPE_COLORS.get(tc.type, "white")
        p_color = PRIO_COLORS.get(tc.priority, "white")
        tbl.add_row(
            tc.id,
            tc.title,
            f"[{tc_color}]{tc.type}[/{tc_color}]",
            f"[{p_color}]{tc.priority}[/{p_color}]",
            str(len(tc.steps)),
        )

    console.print(tbl)

    # ── Missing edge cases ────────────────────────────────────────────────────
    if v.missing_edge_cases:
        console.print()
        console.print("[yellow]⚠  Missing edge cases:[/yellow]")
        for ec in v.missing_edge_cases:
            console.print(f"   [dim]·[/dim] {ec}")

    # ── Save output ───────────────────────────────────────────────────────────
    if output:
        data = {
            "user_story": story,
            "requirements": req.model_dump(),
            "test_cases": [tc.model_dump() for tc in test_cases],
            "verification": v.model_dump(),
        }
        output.write_text(json.dumps(data, indent=2), encoding="utf-8")
        console.print()
        console.print(f"[dim]Saved → [cyan]{output}[/cyan][/dim]")

    console.print()
