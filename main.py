"""
Ghost Traffic - AI-Driven Autonomous Chaos QA Swarm CLI
BharatCode Build League Hackathon

Orchestrates automated adversarial fuzzing, live terminal progress,
AI root-cause crash triage, and vulnerability report compilation.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Optional

try:
    import typer
    HAS_TYPER = True
except ImportError:
    HAS_TYPER = False

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import (
        Progress,
        SpinnerColumn,
        BarColumn,
        TextColumn,
        TimeElapsedColumn,
        TaskProgressColumn,
    )
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

from ghost.fuzzer import execute_swarm
from ghost.llm_client import generate_chaos_payloads, analyze_crash_root_cause
from ghost.reporter import (
    print_banner,
    print_personas_preview,
    print_swarm_results,
    print_ai_triage_cards,
    export_markdown_report,
)

console = Console() if HAS_RICH else None


def print_msg(msg: str) -> None:
    """Safe printer compatible with or without rich."""
    if HAS_RICH and console:
        console.print(msg)
    else:
        import re
        clean = re.sub(r"\[.*?\]", "", msg)
        print(clean)


async def run_fuzz_workflow(
    target: str,
    schema: str,
    method: str,
    output: str,
) -> None:
    """
    Executes the 7-step Autonomous Chaos QA Swarm pipeline:
      1. Print banner & target configuration.
      2. Load schema & synthesize 8 chaos payloads with BharatCode AI.
      3. Render personas preview table.
      4. Unleash swarm with live Rich progress bar animation.
      5. Print telemetry table & summary metrics.
      6. Perform automated Root Cause Analysis on crashes & render triage panels.
      7. Export GHOST_REPORT.md and display completion badge.
    """
    # -------------------------------------------------------------------------
    # Step 1: Banner & Target Configuration
    # -------------------------------------------------------------------------
    print_banner()

    if HAS_RICH and console:
        config_panel = Panel(
            f"[bold cyan]Target URL:[/bold cyan] [bold white]{target}[/bold white]\n"
            f"[bold cyan]HTTP Method:[/bold cyan] [bold yellow]{method.upper()}[/bold yellow]\n"
            f"[bold cyan]Schema Path:[/bold cyan] [bold dim]{schema}[/bold dim]\n"
            f"[bold cyan]Report Output:[/bold cyan] [bold green]{output}[/bold green]",
            title="[bold bright_magenta]🎯 Swarm Mission Configuration[/bold bright_magenta]",
            border_style="bright_blue",
            padding=(0, 2),
        )
        console.print(config_panel)
        console.print()
    else:
        print(f"Target URL:    {target}")
        print(f"HTTP Method:   {method.upper()}")
        print(f"Schema Path:   {schema}")
        print(f"Report Output: {output}\n")

    # -------------------------------------------------------------------------
    # Step 2: Load Schema & Summon Personas with Spinner
    # -------------------------------------------------------------------------
    schema_path = Path(schema)
    schema_dict: dict[str, Any] = {}
    if schema_path.exists():
        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                schema_dict = json.load(f)
        except Exception as e:
            print_msg(f"[bold yellow]⚠️ Warning: Failed to parse schema ({e}). Using fallback heuristics.[/bold yellow]")
    else:
        print_msg(f"[bold yellow]⚠️ Notice: Schema file '{schema}' not found. Using fallback heuristics.[/bold yellow]")

    attacks: list[dict[str, Any]] = []
    if HAS_RICH and console:
        with console.status(
            "[bold bright_magenta]Summoning Chaos Personas via BharatCode AI...[/bold bright_magenta]",
            spinner="dots",
        ):
            attacks = await generate_chaos_payloads(
                schema_dict=schema_dict,
                target_url=target,
            )
        console.print(
            f"[bold green]✔ Successfully materialized {len(attacks)} distinct attack vectors across 5 Chaos Personas.[/bold green]\n"
        )
    else:
        print("Summoning Chaos Personas via BharatCode AI...")
        attacks = await generate_chaos_payloads(
            schema_dict=schema_dict,
            target_url=target,
        )
        print(f"Generated {len(attacks)} attack vectors.")

    # -------------------------------------------------------------------------
    # Step 3: Print Generated Chaos Personas Preview Table
    # -------------------------------------------------------------------------
    print_personas_preview(attacks)

    # -------------------------------------------------------------------------
    # Step 4: Live Progress Bar & Swarm Attack Execution
    # -------------------------------------------------------------------------
    results: list[dict[str, Any]] = []

    if HAS_RICH and console:
        with Progress(
            SpinnerColumn("dots", style="bright_red"),
            TextColumn("[bold bright_red]{task.description}[/bold bright_red]"),
            BarColumn(bar_width=40, style="dim magenta", complete_style="bold bright_magenta"),
            TaskProgressColumn(),
            TextColumn("•"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task_id = progress.add_task(
                "Unleashing Ghost Traffic Swarm...",
                total=len(attacks),
            )

            def on_attack_completed(res: dict[str, Any]) -> None:
                progress.advance(task_id, 1)

            results = await execute_swarm(
                target_url=target,
                method=method.upper(),
                attacks=attacks,
                on_progress_callback=on_attack_completed,
                timeout=5.0,
                concurrency=3,
                delay_between_requests=0.35,
            )
        console.print()
    else:
        print("Unleashing Ghost Traffic Swarm...")

        def on_attack_completed(res: dict[str, Any]) -> None:
            code = res.get("status_code", 0)
            name = res.get("attack_name", "")
            print(f"  -> Finished: {name} (HTTP {code})")

        results = await execute_swarm(
            target_url=target,
            method=method.upper(),
            attacks=attacks,
            on_progress_callback=on_attack_completed,
            timeout=5.0,
            concurrency=3,
            delay_between_requests=0.35,
        )

    # -------------------------------------------------------------------------
    # Step 5: Swarm Results Table & Summary Telemetry
    # -------------------------------------------------------------------------
    print_swarm_results(results)

    total_fired = len(results)
    crashes = [
        r for r in results
        if r.get("is_crash") or r.get("status_code", 0) >= 500 or r.get("verdict") == "VULNERABLE"
    ]
    crashes_5xx = len(crashes)
    handled_4xx = sum(1 for r in results if 400 <= r.get("status_code", 0) < 500)
    bypassed_2xx = sum(1 for r in results if 200 <= r.get("status_code", 0) < 300)
    crash_rate_str = f"{(crashes_5xx / max(1, total_fired)) * 100:.1f}%"

    if HAS_RICH and console:
        summary_table = Table(
            title="📊 Swarm Execution Telemetry Summary",
            border_style="bright_blue",
            show_header=True,
            header_style="bold cyan",
        )
        summary_table.add_column("Total Fired", justify="center", style="bold white", width=14)
        summary_table.add_column("5xx Crashes Triggered", justify="center", style="bold red", width=22)
        summary_table.add_column("4xx Safely Rejected", justify="center", style="bold green", width=20)
        summary_table.add_column("2xx Bypassed", justify="center", style="bold yellow", width=16)
        summary_table.add_column("Crash Rate", justify="center", style="bold red", width=14)

        summary_table.add_row(
            str(total_fired),
            str(crashes_5xx),
            str(handled_4xx),
            str(bypassed_2xx),
            crash_rate_str,
        )
        console.print(summary_table)
        console.print()
    else:
        print("\nTelemetry Summary:")
        print(f"Total Fired: {total_fired} | 5xx Crashes: {crashes_5xx} | 4xx Handled: {handled_4xx} | 2xx Bypassed: {bypassed_2xx} | Crash Rate: {crash_rate_str}\n")

    # -------------------------------------------------------------------------
    # Step 6: Filter 5xx Crashes, Run Root Cause Triage & Display Cards
    # -------------------------------------------------------------------------
    if crashes:
        if HAS_RICH and console:
            with console.status(
                "[bold bright_red]Performing Root-Cause Triage with BharatCode AI...[/bold bright_red]",
                spinner="bouncingBar",
            ):
                for c in crashes:
                    status_code = c.get("status_code", 500)
                    resp_body = (
                        json.dumps(c.get("raw_response", {}))
                        if isinstance(c.get("raw_response"), (dict, list))
                        else str(c.get("raw_response") or c.get("response_preview") or "")
                    )
                    rca = await analyze_crash_root_cause(
                        attack_info=c,
                        status_code=status_code,
                        response_body=resp_body,
                    )
                    c["root_cause_analysis"] = rca

            print_ai_triage_cards(crashes)
        else:
            print("Performing Root-Cause Triage with BharatCode AI...")
            for c in crashes:
                status_code = c.get("status_code", 500)
                resp_body = json.dumps(c.get("raw_response", {}))
                rca = await analyze_crash_root_cause(
                    attack_info=c,
                    status_code=status_code,
                    response_body=resp_body,
                )
                c["root_cause_analysis"] = rca
            print_ai_triage_cards(crashes)
    else:
        if HAS_RICH and console:
            console.print(
                Panel(
                    "[bold green]🛡️ Target API demonstrated 100% resilience! Zero unhandled crashes triggered.[/bold green]",
                    title="[bold green]STATUS HEALTHY[/bold green]",
                    border_style="green",
                )
            )
        else:
            print("Target API demonstrated 100% resilience. Zero crashes triggered.")

    # -------------------------------------------------------------------------
    # Step 7: Export Markdown Report & Final Badge
    # -------------------------------------------------------------------------
    out_file = export_markdown_report(
        target_url=target,
        results=results,
        triaged_crashes=crashes,
        output_path=output,
    )

    if HAS_RICH and console:
        success_panel = Panel(
            f"[bold green]✔ Security Audit Report successfully compiled![/bold green]\n\n"
            f"[bold white]File Location:[/bold white] [bold cyan]{out_file.resolve()}[/bold cyan]\n"
            f"[bold dim]Attach this report to your GitHub Issue, Pull Request, or BharatCode Hackathon Submission.[/bold dim]",
            title="[bold bright_green]🏆 MISSION COMPLETE[/bold bright_green]",
            border_style="bright_green",
            padding=(1, 2),
        )
        console.print(success_panel)
    else:
        print(f"\n[OK] Report saved to {out_file.resolve()}")


# -----------------------------------------------------------------------------
# Typer CLI Definition
# -----------------------------------------------------------------------------
if HAS_TYPER:
    app = typer.Typer(
        name="ghost-traffic",
        help="👻 Ghost Traffic: AI-driven Autonomous Chaos QA Swarm CLI tool.",
        add_completion=False,
    )

    @app.callback(invoke_without_command=True)
    def main_callback(
        ctx: typer.Context,
        target: str = typer.Option(
            "http://127.0.0.1:8000/api/v1/checkout",
            "--target",
            "-t",
            help="Target API URL",
        ),
        schema: str = typer.Option(
            "target_server/sample_schema.json",
            "--schema",
            "-s",
            help="Path to sample JSON schema file",
        ),
        method: str = typer.Option(
            "POST",
            "--method",
            "-m",
            help="HTTP method",
        ),
        output: str = typer.Option(
            "GHOST_REPORT.md",
            "--output",
            "-o",
            help="Path to save Markdown report",
        ),
    ):
        """Ghost Traffic CLI default entry point."""
        if ctx.invoked_subcommand is None:
            asyncio.run(run_fuzz_workflow(target, schema, method, output))

    @app.command(name="fuzz")
    def fuzz_command(
        target: str = typer.Option(
            "http://127.0.0.1:8000/api/v1/checkout",
            "--target",
            "-t",
            help="Target API URL",
        ),
        schema: str = typer.Option(
            "target_server/sample_schema.json",
            "--schema",
            "-s",
            help="Path to sample JSON schema file",
        ),
        method: str = typer.Option(
            "POST",
            "--method",
            "-m",
            help="HTTP method",
        ),
        output: str = typer.Option(
            "GHOST_REPORT.md",
            "--output",
            "-o",
            help="Path to save Markdown report",
        ),
    ):
        """Run the Ghost Traffic Chaos QA Swarm against the target server."""
        asyncio.run(run_fuzz_workflow(target, schema, method, output))

    @app.command(name="start-target")
    def start_target_command(
        host: str = typer.Option("127.0.0.1", "--host", "-h", help="Target server host"),
        port: int = typer.Option(8000, "--port", "-p", help="Target server port"),
        reload: bool = typer.Option(True, "--reload", help="Enable live reload"),
    ):
        """Start the deliberately vulnerable FastAPI target server locally."""
        import uvicorn
        target_dir = Path(__file__).parent / "target_server"
        if str(target_dir) not in sys.path:
            sys.path.insert(0, str(target_dir))

        if HAS_RICH and console:
            console.print(
                Panel(
                    f"[bold green]Starting Vulnerable Target Server[/bold green]\n"
                    f"URL: [cyan]http://{host}:{port}[/cyan]\n"
                    f"Checkout Endpoint: [yellow]POST http://{host}:{port}/api/v1/checkout[/yellow]\n"
                    f"Interactive Docs: [cyan]http://{host}:{port}/docs[/cyan]\n"
                    f"Schema: [cyan]http://{host}:{port}/schema[/cyan]",
                    title="🎯 Ghost Market SUT",
                    border_style="green",
                )
            )
        else:
            print(f"Starting Target Server on http://{host}:{port}")

        uvicorn.run("app:app", host=host, port=port, reload=reload)

    @app.command(name="verify")
    def verify_command():
        """Run in-memory test suite verifying the 5 deliberate backend bugs."""
        test_script = Path(__file__).parent / "test_bugs.py"
        if test_script.exists():
            import subprocess
            subprocess.run([sys.executable, str(test_script)], check=False)
        else:
            print_msg("[red]test_bugs.py not found[/red]")

    @app.command(name="version")
    def version_command():
        """Print the Ghost Traffic CLI version."""
        from ghost import __version__
        print_msg(f"[bold cyan]Ghost Traffic CLI[/bold cyan] version [bold green]{__version__}[/bold green]")

else:
    # Standard library fallback if typer is not installed
    def run_cli_fallback():
        if len(sys.argv) > 1 and sys.argv[1] == "start-target":
            # Delegate to start-target
            import uvicorn
            target_dir = Path(__file__).parent / "target_server"
            if str(target_dir) not in sys.path:
                sys.path.insert(0, str(target_dir))
            print("Starting Target Server on http://127.0.0.1:8000")
            uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
            return
        elif len(sys.argv) > 1 and sys.argv[1] == "verify":
            test_script = Path(__file__).parent / "test_bugs.py"
            if test_script.exists():
                import subprocess
                subprocess.run([sys.executable, str(test_script)], check=False)
            return
        elif len(sys.argv) > 1 and sys.argv[1] == "version":
            from ghost import __version__
            print(f"Ghost Traffic CLI version {__version__}")
            return

        import argparse
        parser = argparse.ArgumentParser(description="Ghost Traffic - Chaos QA Swarm CLI")
        parser.add_argument("-t", "--target", default="http://127.0.0.1:8000/api/v1/checkout", help="Target API URL")
        parser.add_argument("-s", "--schema", default="target_server/sample_schema.json", help="Schema path")
        parser.add_argument("-m", "--method", default="POST", help="HTTP method")
        parser.add_argument("-o", "--output", default="GHOST_REPORT.md", help="Output report path")
        args, _ = parser.parse_known_args()
        asyncio.run(run_fuzz_workflow(args.target, args.schema, args.method, args.output))


if __name__ == "__main__":
    if HAS_TYPER and app is not None:
        app()
    else:
        run_cli_fallback()
