"""
Ghost Traffic - AI-Driven Autonomous Chaos QA Swarm CLI
BharatCode Build League Hackathon
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Optional

try:
    import typer
    HAS_TYPER = True
except ImportError:
    HAS_TYPER = False

try:
    from rich.console import Console
    from rich.panel import Panel
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

if HAS_RICH:
    console = Console()
else:
    console = None  # type: ignore

if HAS_TYPER:
    app = typer.Typer(
        name="ghost-traffic",
        help="👻 Ghost Traffic: AI-driven Autonomous Chaos QA Swarm CLI tool.",
        add_completion=False,
    )
else:
    app = None  # type: ignore


def print_msg(msg: str, style: str = "") -> None:
    if HAS_RICH and console:
        console.print(msg)
    else:
        # Strip simple rich tags for plain stdout
        import re
        clean = re.sub(r"\[.*?\]", "", msg)
        print(clean)


def run_version() -> None:
    """Print the Ghost Traffic CLI version."""
    from ghost import __version__
    print_msg(f"[bold cyan]Ghost Traffic CLI[/bold cyan] version [bold green]{__version__}[/bold green]")


def run_start_target(
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = True,
) -> None:
    """Start the deliberately vulnerable FastAPI target server locally."""
    import uvicorn
    target_dir = Path(__file__).parent / "target_server"
    if str(target_dir) not in sys.path:
        sys.path.insert(0, str(target_dir))

    banner = (
        f"[bold green]Starting Vulnerable Target Server[/bold green]\n"
        f"URL: [cyan]http://{host}:{port}[/cyan]\n"
        f"Checkout Endpoint: [yellow]POST http://{host}:{port}/api/v1/checkout[/yellow]\n"
        f"Interactive Docs: [cyan]http://{host}:{port}/docs[/cyan]\n"
        f"Schema: [cyan]http://{host}:{port}/schema[/cyan]"
    )
    if HAS_RICH and console:
        console.print(Panel(banner, title="🎯 Ghost Market SUT", border_style="green"))
    else:
        print_msg(banner)

    uvicorn.run("app:app", host=host, port=port, reload=reload)


def run_fuzz(
    target_url: str = "http://127.0.0.1:8000",
    endpoint: str = "/api/v1/checkout",
    schema_path: Optional[str] = "target_server/sample_schema.json",
    concurrency: int = 3,
    delay: float = 0.35,
    timeout: float = 5.0,
) -> None:
    """Run the Ghost Traffic Chaos QA Swarm against the target server."""
    from ghost.fuzzer import execute_swarm
    from ghost.llm_client import generate_chaos_payloads, analyze_crash_root_cause
    from ghost.reporter import (
        print_banner,
        print_personas_preview,
        print_swarm_results,
        print_ai_triage_cards,
        export_markdown_report,
    )

    print_banner()

    full_target_url = f"{target_url.rstrip('/')}{endpoint}"
    print_msg(f"[bold magenta]👻 Target System Under Test:[/bold magenta] [cyan]{full_target_url}[/cyan]")

    # 1. Load Schema
    schema_file = Path(schema_path) if schema_path else None
    schema_data = {}
    if schema_file and schema_file.exists():
        with open(schema_file, "r", encoding="utf-8") as f:
            schema_data = json.load(f)
        print_msg(f"[dim]Loaded API schema from {schema_file}[/dim]\n")
    else:
        print_msg(f"[yellow]Schema file {schema_path} not found. Operating with fallback schema heuristics.[/yellow]\n")

    async def _async_fuzz():
        # 2. Generate Adversarial Attacks via BharatCode LLM
        print_msg("[cyan]Contacting BharatCode AI to synthesize adversarial chaos payloads across 5 personas...[/cyan]")
        attacks = await generate_chaos_payloads(
            schema_dict=schema_data,
            target_url=full_target_url,
        )
        print_msg(f"[bold green]Synthesized {len(attacks)} chaos attack vectors.[/bold green]\n")

        # 3. Display Personas Preview Table
        print_personas_preview(attacks)

        # 4. Live Progress Callback for video-ready terminal animation
        def on_attack_progress(result: dict):
            status = result.get("status_code", 0)
            verdict = result.get("verdict", "UNKNOWN")
            persona = result.get("persona", "Attacker")
            name = result.get("attack_name", "Attack")
            latency = result.get("latency_ms", 0.0)

            if verdict == "VULNERABLE":
                tag = "[bold red]💥 CRASH (5xx)[/bold red]"
                v_str = "[bold red]VULNERABLE[/bold red]"
            elif verdict == "RESILIENT":
                tag = "[bold green]🛡️ HANDLED (4xx)[/bold green]"
                v_str = "[bold green]RESILIENT[/bold green]"
            else:
                tag = "[bold yellow]⚡ BYPASSED (2xx)[/bold yellow]"
                v_str = "[bold yellow]SUSPICIOUS[/bold yellow]"

            print_msg(f"  {tag} -> {v_str} | [cyan]{persona:<20}[/cyan] | {name:<35} ({latency:.1f}ms)")

        # 5. Execute Swarm
        print_msg("[bold cyan]🚀 Unleashing concurrent chaos assault...[/bold cyan]")
        results = await execute_swarm(
            target_url=full_target_url,
            method="POST",
            attacks=attacks,
            on_progress_callback=on_attack_progress,
            timeout=timeout,
            concurrency=concurrency,
            delay_between_requests=delay,
        )

        # 6. Enrich Crashes with Root Cause Analysis
        crashes = [r for r in results if r.get("is_crash") or r.get("verdict") == "VULNERABLE"]
        if crashes:
            print_msg("\n[cyan]Performing automated Root Cause Analysis on triggered vulnerabilities...[/cyan]")
            for c in crashes:
                rca = await analyze_crash_root_cause(
                    attack_info=c,
                    status_code=c.get("status_code", 500),
                    response_body=json.dumps(c.get("raw_response", {})),
                )
                c["root_cause_analysis"] = rca

        # 7. Print Final Telemetry Table & Triage Cards
        print_swarm_results(results)
        if crashes:
            print_ai_triage_cards(crashes)

        # 8. Export Markdown Report
        md_file = export_markdown_report(
            target_url=full_target_url,
            results=results,
            triaged_crashes=crashes,
            output_path="GHOST_REPORT.md",
        )
        print_msg(f"\n[bold green]✅ Security Audit Markdown Report saved to:[/bold green] [cyan]{md_file.resolve()}[/cyan]")

    asyncio.run(_async_fuzz())


def run_test_bugs() -> None:
    """Run in-memory test suite verifying the 5 deliberate backend bugs."""
    test_script = Path(__file__).parent / "test_bugs.py"
    if test_script.exists():
        import subprocess
        subprocess.run([sys.executable, str(test_script)], check=False)
    else:
        print_msg("[red]test_bugs.py not found[/red]")


# Typer Command Bindings
if HAS_TYPER and app is not None:
    @app.command()
    def version():
        run_version()

    @app.command()
    def start_target(
        host: str = typer.Option("127.0.0.1", "--host", "-h", help="Target server host"),
        port: int = typer.Option(8000, "--port", "-p", help="Target server port"),
        reload: bool = typer.Option(True, "--reload", help="Enable live reload"),
    ):
        run_start_target(host, port, reload)

    @app.command()
    def fuzz(
        target_url: str = typer.Option("http://127.0.0.1:8000", "--target", "-t", help="Target server base URL"),
        endpoint: str = typer.Option("/api/v1/checkout", "--endpoint", "-e", help="Target endpoint path"),
        schema_path: Optional[str] = typer.Option("target_server/sample_schema.json", "--schema", "-s", help="Path to OpenAPI/JSON schema"),
        concurrency: int = typer.Option(3, "--concurrency", "-c", help="Concurrent swarm workers"),
        delay: float = typer.Option(0.35, "--delay", "-d", help="Delay between requests for dramatic demo pacing"),
        timeout: float = typer.Option(5.0, "--timeout", help="Request timeout in seconds"),
    ):
        run_fuzz(target_url, endpoint, schema_path, concurrency, delay, timeout)

    @app.command()
    def verify():
        run_test_bugs()


if __name__ == "__main__":
    if HAS_TYPER and app is not None:
        app()
    else:
        # Fallback argument parsing if typer is not installed
        if len(sys.argv) > 1 and sys.argv[1] == "version":
            run_version()
        elif len(sys.argv) > 1 and sys.argv[1] == "start-target":
            run_start_target()
        elif len(sys.argv) > 1 and sys.argv[1] == "verify":
            run_test_bugs()
        else:
            run_fuzz()
