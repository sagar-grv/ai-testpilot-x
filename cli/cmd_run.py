"""testpilot run — Full AI QA pipeline with Rich terminal output."""

from __future__ import annotations
import json
import time
import uuid
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

console = Console()

# Exit codes
EXIT_GO = 0
EXIT_GO_WITH_RISK = 1
EXIT_NO_GO = 2


def _load_project_config():
    """Load testpilot.yaml if it exists."""
    try:
        from config import load_yaml_config, reload_settings

        load_yaml_config()
        reload_settings()
    except Exception:
        pass


def run_cmd(
    story: str = typer.Option(
        ..., "--story", "-s", help="Plain-English user story to test."
    ),
    url: Optional[str] = typer.Option(
        None, "--url", "-u", help="Target application URL (overrides testpilot.yaml)."
    ),
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to testpilot.yaml (default: auto-detect in cwd).",
    ),
    mode: Optional[str] = typer.Option(
        None, "--mode", "-m", help="Execution mode: MOCK | LOCAL | GRID"
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Save full report JSON to this file."
    ),
    session: Optional[str] = typer.Option(
        None, "--session", help="Session ID (auto-generated if not provided)."
    ),
):
    """Run the full AI QA pipeline for a user story.

    [dim]Exit codes:[/dim]
      [green]0[/green] = GO — all tests pass
      [yellow]1[/yellow] = GO WITH RISK — high severity bugs
      [red]2[/red] = NO GO — critical bugs, release blocked
    """
    _load_project_config()

    # SECURITY: validate story length before any processing
    if len(story) > 15_000:
        console.print(
            "[red]Error:[/red] --story exceeds maximum length of 15,000 characters."
        )
        raise typer.Exit(1)

    # Apply overrides
    if mode or url:
        from config import configure

        overrides = {}
        if mode:
            overrides["execution_mode"] = mode.upper()
        if url:
            overrides["target_url"] = url
        configure(**overrides)

    from config import settings as cfg

    target_url = url or cfg.EXECUTION_MODE and getattr(cfg, "target_url", "") or ""

    session_id = session or f"run-{uuid.uuid4().hex[:8]}"

    console.print()
    console.print(
        Panel.fit(
            f"[bold cyan]AI TestPilot X[/bold cyan]  [dim]v1.0.0[/dim]  ·  Session [cyan]{session_id}[/cyan]",
            border_style="cyan",
        )
    )
    console.print()

    # ── Run pipeline with per-stage progress ──────────────────────────────────
    _stages = {
        "Analyzing requirements": None,
        "Generating test cases": None,
        "Verifying coverage": None,
        "Generating Selenium scripts": None,
        "Generating API tests": None,
        "Executing tests": None,
        "Analyzing bugs": None,
        "Generating report": None,
    }

    result = {}
    start_total = time.perf_counter()

    with Progress(
        SpinnerColumn(spinner_name="dots", style="cyan"),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    ) as progress:

        task = progress.add_task("Initializing pipeline...", total=None)

        from orchestrator import build_graph

        graph = build_graph()

        def _update(stage: str, done: bool = False, extra: str = ""):
            if done:
                progress.update(
                    task, description=f"[green]✓[/green]  {stage}  [dim]{extra}[/dim]"
                )
            else:
                progress.update(task, description=f"  {stage}...")

        try:
            # Stream-run the graph and capture intermediate state
            _update("Analyzing requirements")
            result = graph.invoke(
                {
                    "session_id": session_id,
                    "session_metadata": {
                        "user_story": story,
                        "target_url": target_url,
                    },
                },
                config={"configurable": {"thread_id": session_id}},
            )
        except Exception as e:
            progress.stop()
            console.print(f"\n[bold red]Pipeline failed:[/bold red] {e}")
            raise typer.Exit(EXIT_NO_GO)

        progress.update(task, description="[green]✓[/green]  Pipeline complete")

    elapsed = time.perf_counter() - start_total

    # ── Extract results ───────────────────────────────────────────────────────
    req = result.get("requirement_context") or {}
    tcs = result.get("generated_testcases") or []
    vrepo = result.get("verification_report") or {}
    exec_ = result.get("execution_results") or {}
    bugs = result.get("bugs") or []
    report = result.get("report") or {}

    decision = report.get("decision", "NO_GO")
    risk_score = report.get("risk_score", 0)
    total_tests = exec_.get("total", 0)
    passed = exec_.get("passed", 0)
    failed = exec_.get("failed", 0)
    critical = report.get("critical_bugs", 0)
    high = report.get("high_bugs", 0)
    medium = report.get("medium_bugs", 0)
    low = report.get("low_bugs", 0)
    rec_text = report.get("recommendation_text", "")

    console.print()

    # ── Stage summary table ───────────────────────────────────────────────────
    tbl = Table(show_header=False, box=None, padding=(0, 1))
    tbl.add_column("", style="dim", width=3)
    tbl.add_column("Stage", style="white", width=28)
    tbl.add_column("Result", style="green")

    modules = req.get("modules", [])
    tbl.add_row(
        "✓",
        "Requirements analyzed",
        f"{len(modules)} modules · [cyan]{req.get('priority','?')}[/cyan] priority",
    )
    tbl.add_row("✓", "Test cases generated", f"[cyan]{len(tcs)}[/cyan] test cases")
    cov = vrepo.get("coverage_score", 0)
    tbl.add_row(
        "✓",
        "Coverage verified",
        f"[{'green' if cov >= 0.6 else 'yellow'}]{cov:.0%}[/]"
        f"{'  ✓' if vrepo.get('passed') else '  ⚠ below threshold'}",
    )
    mode_val = exec_.get("mode", cfg.EXECUTION_MODE)
    tbl.add_row(
        "✓",
        f"Tests executed ({mode_val})",
        f"[green]{passed} passed[/green]  [red]{failed} failed[/red]",
    )
    if bugs:
        tbl.add_row(
            "✓",
            "Bugs analyzed",
            f"[red]{critical} critical[/red]  "
            f"[yellow]{high} high[/yellow]  "
            f"[dim]{medium} medium  {low} low[/dim]",
        )
    console.print(tbl)
    console.print()

    # ── Release Decision Banner ───────────────────────────────────────────────
    BANNERS = {
        "GO": ("green", "✅", "GO", "Release approved."),
        "GO_WITH_RISK": (
            "yellow",
            "⚠️ ",
            "GO WITH RISK",
            "High severity issues present.",
        ),
        "NO_GO": ("red", "🚫", "NO GO", "Critical bugs detected — release blocked."),
    }
    color, icon, label, subtitle = BANNERS.get(decision, BANNERS["NO_GO"])

    console.print(
        Panel(
            f"{icon}  [bold {color}]{label}[/bold {color}]\n\n"
            f"[dim]Risk Score[/dim]   [bold]{risk_score:.0f} / 100[/bold]\n"
            f"[dim]Tests[/dim]        [green]{passed}[/green] / {total_tests} passed\n"
            f"[dim]Bugs[/dim]         "
            f"[red]{critical} critical[/red]  [yellow]{high} high[/yellow]  "
            f"[dim]{medium} medium  {low} low[/dim]\n"
            f"[dim]Duration[/dim]     {elapsed:.1f}s\n\n"
            + (f"[italic dim]{rec_text}[/italic dim]" if rec_text else ""),
            title="[bold]Release Decision[/bold]",
            border_style=color,
            expand=False,
        )
    )
    console.print()

    # ── Save report ───────────────────────────────────────────────────────────
    report_path = output
    if not report_path:
        reports_dir = Path.cwd() / ".testpilot" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        import datetime as dt

        ts = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        report_path = reports_dir / f"run-{ts}.json"

    try:
        serializable = {k: v for k, v in result.items() if k != "_approval_fn"}
        report_path.write_text(
            json.dumps(serializable, indent=2, default=str), encoding="utf-8"
        )
        console.print(f"[dim]Report saved → [cyan]{report_path}[/cyan][/dim]")
    except Exception as e:
        console.print(f"[dim]Could not save report: {e}[/dim]")

    console.print()

    # ── Exit code ─────────────────────────────────────────────────────────────
    exit_map = {"GO": EXIT_GO, "GO_WITH_RISK": EXIT_GO_WITH_RISK, "NO_GO": EXIT_NO_GO}
    raise typer.Exit(exit_map.get(decision, EXIT_NO_GO))
