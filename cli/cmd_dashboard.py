"""testpilot dashboard — Launch the Streamlit visual dashboard."""
from __future__ import annotations
import typer
from rich.console import Console

console = Console()


def dashboard_cmd(
    port: int = typer.Option(8501, "--port", "-p", help="Port to run on."),
    no_browser: bool = typer.Option(False, "--no-browser",
        help="Don't open browser automatically."),
):
    """Launch the AI TestPilot X visual dashboard.

    Requires the [ui] extra: [cyan]pip install ai-testpilot-x[ui][/cyan]
    """
    try:
        import importlib.util
        if importlib.util.find_spec("streamlit") is None:
            raise ImportError("streamlit not found")
    except ImportError:
        console.print(
            "[red]Streamlit is not installed.[/red]\n\n"
            "Install the UI extras:\n"
            "  [cyan]pip install ai-testpilot-x[ui][/cyan]"
        )
        raise typer.Exit(1)

    import subprocess
    import sys
    from pathlib import Path

    # Find app.py — try cwd first, then package directory
    app_path = Path.cwd() / "app.py"
    if not app_path.exists():
        app_path = Path(__file__).parent.parent / "app.py"
    if not app_path.exists():
        console.print(
            "[red]Error:[/red] Could not find app.py.\n"
            "Make sure you're running from the ai-testpilot-x project directory."
        )
        raise typer.Exit(1)

    console.print()
    console.print(
        f"[bold cyan]AI TestPilot X[/bold cyan] Dashboard starting on "
        f"[cyan]http://localhost:{port}[/cyan]"
    )
    console.print("[dim]Press Ctrl+C to stop.[/dim]")
    console.print()

    cmd = [
        sys.executable, "-m", "streamlit", "run", str(app_path),
        "--server.port", str(port),
        "--server.headless", "false",
    ]
    if no_browser:
        cmd += ["--server.headless", "true"]

    try:
        subprocess.run(cmd, check=False)
    except KeyboardInterrupt:
        console.print("\n[dim]Dashboard stopped.[/dim]")
