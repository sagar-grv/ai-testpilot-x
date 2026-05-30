"""testpilot bugs — Analyze a stack trace or error log with AI + RAG."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

SEV_COLORS = {"Critical": "red", "High": "yellow", "Medium": "cyan", "Low": "green"}
SEV_ICONS  = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}


def bugs_cmd(
    log: Optional[str] = typer.Option(None, "--log", "-l",
        help="Error log text or path to a .log/.txt file."),
    output: Optional[Path] = typer.Option(None, "--output", "-o",
        help="Save bug report JSON to this file."),
    config: Optional[Path] = typer.Option(None, "--config", "-c",
        help="Path to testpilot.yaml."),
    session: Optional[str] = typer.Option(None, "--session",
        help="Session ID for RAG correlation."),
):
    """Analyze an error log or stack trace with AI + RAG.

    Pass inline text with --log, or a file path.

    Examples:

        testpilot bugs --log "NoSuchElementException: #login-btn"

        testpilot bugs --log ./error.log
    """
    try:
        from config import load_yaml_config, reload_settings
        load_yaml_config(config)
        reload_settings()
    except Exception:
        pass

    # ── Resolve log text ──────────────────────────────────────────────────────
    log_text = ""
    if log:
        p = Path(log)
        if p.exists():
            log_text = p.read_text(encoding="utf-8", errors="ignore")
            console.print(f"[dim]Reading log from: {p}[/dim]")
        else:
            log_text = log
    else:
        # Read from stdin if piped
        import sys
        if not sys.stdin.isatty():
            log_text = sys.stdin.read()
        else:
            console.print("[red]Error:[/red] Provide --log TEXT or --log FILE, or pipe stdin.")
            raise typer.Exit(1)

    if not log_text.strip():
        console.print("[red]Error:[/red] Empty log text.")
        raise typer.Exit(1)

    console.print()
    console.print(Panel.fit(
        "[bold cyan]AI TestPilot X[/bold cyan]  ·  Bug Analysis",
        border_style="cyan"
    ))
    console.print()

    sid = session or "cli-bugs"

    with Progress(
        SpinnerColumn(spinner_name="dots", style="cyan"),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as prog:
        t = prog.add_task("Analyzing with AI + RAG correlation...", total=None)
        from agents.bug_agent import BugAgent
        bug = BugAgent().analyze_single(log_text, session_id=sid)

    sev = bug.severity
    sc  = SEV_COLORS.get(sev, "white")
    si  = SEV_ICONS.get(sev, "⚪")

    # ── Bug report panel ──────────────────────────────────────────────────────
    console.print(Panel(
        f"{si}  [bold {sc}]{sev} Severity[/bold {sc}]  ·  {bug.priority}\n\n"
        f"[dim]ID[/dim]               {bug.id}\n"
        f"[dim]Title[/dim]            {bug.title}\n"
        f"[dim]Signature[/dim]        [yellow]{bug.failure_signature}[/yellow]\n\n"
        f"[bold]Root Cause[/bold]  [dim]({bug.root_cause_confidence:.0%} confidence)[/dim]\n"
        f"  {bug.root_cause}\n\n"
        f"[bold]Fix Suggestion[/bold]  [dim]({bug.fix_confidence:.0%} confidence)[/dim]\n"
        f"  {bug.fix_suggestion}",
        title="[bold]Bug Report[/bold]",
        border_style=sc,
        expand=False,
    ))

    # ── RAG matches ───────────────────────────────────────────────────────────
    if bug.rag_matches:
        console.print()
        console.print(f"[bold]Similar past bugs (RAG):[/bold]  {len(bug.rag_matches)} matches")
        for m in bug.rag_matches[:3]:
            sim = max(0.0, 1.0 - float(m.get("distance", 0.5)))
            console.print(
                f"  [dim]·[/dim] [cyan]{m.get('id','?')}[/cyan]  "
                f"[dim]{sim:.0%} similar[/dim]  —  {m.get('text','')[:80]}..."
            )

    # ── Save output ───────────────────────────────────────────────────────────
    if output:
        output.write_text(json.dumps(bug.model_dump(), indent=2), encoding="utf-8")
        console.print()
        console.print(f"[dim]Saved → [cyan]{output}[/cyan][/dim]")

    console.print()
