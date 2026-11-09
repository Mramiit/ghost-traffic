"""
Ghost Traffic - Chaos Reporter & Vulnerability Triage Engine
Generates cyber-security styled terminal UI with Rich and exports
publication-ready GitHub-flavored Markdown vulnerability audit reports.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Optional import of rich with terminal fallback
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.syntax import Syntax
    from rich.text import Text
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

console = Console() if HAS_RICH else None


def _get_val(obj: Any, key: str, default: Any = None) -> Any:
    """Safely retrieves value from dict or object attribute."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def print_banner() -> None:
    """
    Renders a bold ASCII art header for 'GHOST TRAFFIC // Autonomous Chaos QA Swarm'
    inside a rich.panel.Panel with cyber-security styling (cyan/magenta/red accents).
    """
    ascii_art = """
 ██████╗ ██╗  ██╗ ██████╗ ███████╗████████╗    ████████╗██████╗  █████╗ ███████╗███████╗██╗ ██████╗
██╔════╝ ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝    ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██╔════╝██║██╔════╝
██║  ███╗███████║██║   ██║███████╗   ██║          ██║   ██████╔╝███████║█████╗  █████╗  ██║██║     
██║   ██║██╔══██║██║   ██║╚════██║   ██║          ██║   ██╔══██╗██╔══██║██╔══╝  ██╔══╝  ██║██║     
╚██████╔╝██║  ██║╚██████╔╝███████║   ██║          ██║   ██║  ██║██║  ██║██║     ██║     ██║╚██████╗
 ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝          ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝     ╚═╝ ╚═════╝"""

    subtitle = (
        "[bold cyan]AUTONOMOUS CHAOS QA SWARM[/bold cyan] [bold bright_black]•[/bold bright_black] "
        "[bold bright_magenta]BHARATCODE BUILD LEAGUE[/bold bright_magenta] [bold bright_black]•[/bold bright_black] "
        "[bold bright_red]VULNERABILITY FUZZER[/bold bright_red]"
    )

    if HAS_RICH and console:
        panel_content = f"[bold bright_cyan]{ascii_art}[/bold bright_cyan]\n\n{subtitle}"
        banner_panel = Panel(
            panel_content,
            border_style="bright_magenta",
            title="[bold bright_red]👻 GHOST TRAFFIC v0.1.0[/bold bright_red]",
            subtitle="[bold dim cyan]AI-Powered Dynamic API Security Fuzzing[/bold dim cyan]",
            padding=(1, 2),
        )
        console.print(banner_panel)
    else:
        print("=" * 80)
        print(" GHOST TRAFFIC // Autonomous Chaos QA Swarm (v0.1.0)")
        print(" BharatCode Build League Hackathon")
        print("=" * 80)


def print_personas_preview(attacks: list[dict[str, Any]]) -> None:
    """
    Displays a compact rich.table.Table showing the AI-generated Chaos Personas,
    their Attack Names, and their Hypotheses before firing the swarm.
    """
    if HAS_RICH and console:
        table = Table(
            title="🎯 Armed Chaos Swarm Personas & Target Attack Vectors",
            header_style="bold bright_cyan",
            border_style="dim magenta",
            show_lines=True,
        )
        table.add_column("#", style="dim", justify="center", width=4)
        table.add_column("Chaos Persona", style="bold magenta", width=24)
        table.add_column("Attack Vector", style="bold white", width=34)
        table.add_column("Target Hypothesis", style="yellow")

        for idx, atk in enumerate(attacks, 1):
            persona = _get_val(atk, "persona", "Adversarial Fuzzer")
            attack_name = _get_val(atk, "attack_name", "Boundary Probe")
            hypothesis = _get_val(atk, "hypothesis", "None provided")

            # Style persona badge
            p_style = "bold cyan"
            if "SQL" in persona:
                p_style = "bold red"
            elif "Unicode" in persona or "Gremlin" in persona:
                p_style = "bold magenta"
            elif "Boundary" in persona:
                p_style = "bold yellow"
            elif "Type" in persona:
                p_style = "bold blue"
            elif "JSON" in persona or "Hoarder" in persona:
                p_style = "bold green"

            table.add_row(
                str(idx),
                f"[{p_style}]{persona}[/{p_style}]",
                attack_name,
                hypothesis,
            )

        console.print(table)
        console.print()
    else:
        print("\nArmed Chaos Personas Preview:")
        for idx, atk in enumerate(attacks, 1):
            p = _get_val(atk, "persona", "Fuzzer")
            n = _get_val(atk, "attack_name", "Probe")
            h = _get_val(atk, "hypothesis", "")
            print(f"  [{idx}] {p:<22} | {n:<32} -> {h}")
        print()


def print_swarm_results(results: list[dict[str, Any]]) -> None:
    """
    Displays a color-coded results table with columns:
    `#`, `Persona`, `Attack Vector`, `HTTP Status`, `Latency`, and `Verdict`
    (Red bold for VULNERABLE/500, Yellow for SUSPICIOUS/200 on attack, Green for RESILIENT/400-422).
    """
    if HAS_RICH and console:
        table = Table(
            title="⚡ Chaos Swarm Telemetry & Security Assessment",
            header_style="bold bright_cyan",
            border_style="bright_blue",
            show_lines=False,
        )
        table.add_column("#", justify="center", width=4, style="dim")
        table.add_column("Persona", style="cyan", width=22)
        table.add_column("Attack Vector", style="bold white", width=34)
        table.add_column("HTTP Status", justify="center", width=12)
        table.add_column("Latency", justify="right", width=12)
        table.add_column("Verdict", justify="center", width=14)

        for idx, r in enumerate(results, 1):
            status = _get_val(r, "status_code", 0)
            verdict = _get_val(r, "verdict", "UNKNOWN")
            latency = float(_get_val(r, "latency_ms", 0.0))
            persona = _get_val(r, "persona", "Attacker")
            attack_name = _get_val(r, "attack_name", "Attack")

            # Determine color-coded styling
            if status >= 500 or verdict == "VULNERABLE":
                status_styled = f"[bold red]{status}[/bold red]"
                verdict_styled = "[bold red]VULNERABLE[/bold red]"
            elif verdict == "RESILIENT" or 400 <= status < 500:
                status_styled = f"[bold green]{status}[/bold green]"
                verdict_styled = "[bold green]RESILIENT[/bold green]"
            elif verdict == "SUSPICIOUS" or 200 <= status < 300:
                status_styled = f"[bold yellow]{status}[/bold yellow]"
                verdict_styled = "[bold yellow]SUSPICIOUS[/bold yellow]"
            else:
                status_styled = f"[cyan]{status}[/cyan]"
                verdict_styled = f"[dim]{verdict}[/dim]"

            table.add_row(
                str(idx),
                str(persona),
                str(attack_name)[:33],
                status_styled,
                f"{latency:.1f}ms",
                verdict_styled,
            )

        console.print(table)
        console.print()
    else:
        print("\nSwarm Execution Results:")
        print(f"{'#':<4} {'Persona':<22} {'Attack Vector':<32} {'Status':<10} {'Latency':<10} {'Verdict'}")
        print("-" * 90)
        for idx, r in enumerate(results, 1):
            p = _get_val(r, "persona", "")
            n = _get_val(r, "attack_name", "")
            s = _get_val(r, "status_code", 0)
            l = float(_get_val(r, "latency_ms", 0.0))
            v = _get_val(r, "verdict", "")
            print(f"{idx:<4} {p:<22} {n[:30]:<32} {s:<10} {l:.1f}ms    {v}")
        print("-" * 90)


def print_ai_triage_cards(triaged_crashes: list[dict[str, Any]]) -> None:
    """
    For every 500 crash analyzed by the BharatCode LLM, render a rich.panel.Panel showing:
      - Severity Badge & Vulnerability Type
      - The exact JSON payload that broke the server (formatted with rich.syntax.Syntax)
      - Root Cause Analysis
      - Suggested Surgical Code Fix (formatted with rich.syntax.Syntax in Python)
    """
    if not triaged_crashes:
        return

    if HAS_RICH and console:
        console.print("\n[bold bright_red]💥 AUTOMATED ROOT CAUSE ANALYSIS & REMEDIATION CARDS[/bold bright_red]\n")

        for idx, c in enumerate(triaged_crashes, 1):
            rca = _get_val(c, "root_cause_analysis") or {}
            attack_name = _get_val(c, "attack_name", "Crash Vector")
            persona = _get_val(c, "persona", "Chaos Attacker")
            payload = _get_val(c, "payload", {})

            # Extract RCA details or fall back to response data
            severity = rca.get("severity", "CRITICAL")
            vuln_type = rca.get("vulnerability_type", _get_val(c, "error_class", "Internal Server Crash"))
            root_cause = rca.get("root_cause", _get_val(c, "error_detail", "Unhandled backend exception."))
            fix_code = rca.get("fix_diff", "# Implement defensive input validation")

            # Style severity badge
            if severity == "CRITICAL":
                sev_badge = "[bold white on red] CRITICAL [/bold white on red]"
                border = "bright_red"
            elif severity == "HIGH":
                sev_badge = "[bold black on yellow] HIGH [/bold black on yellow]"
                border = "yellow"
            else:
                sev_badge = "[bold white on blue] MEDIUM [/bold white on blue]"
                border = "blue"

            console.print(f"[bold red]════════ Finding #{idx}: {attack_name} ════════[/bold red]")
            console.print(f"  {sev_badge} [bold white]{vuln_type}[/bold white]")
            console.print(f"  [dim cyan]Attacker Persona:[/dim cyan] {persona}")
            console.print(f"  [dim cyan]Root Cause:[/dim cyan] {root_cause}\n")

            # Syntax highlighted payload
            payload_json = json.dumps(payload, indent=2)
            payload_syntax = Syntax(payload_json, "json", theme="monokai", line_numbers=False)
            payload_panel = Panel(
                payload_syntax,
                title="[bold bright_yellow]💣 Reproducing Adversarial Payload[/bold bright_yellow]",
                border_style="bright_black",
                padding=(0, 1),
            )
            console.print(payload_panel)

            # Syntax highlighted Python code fix
            fix_syntax = Syntax(fix_code, "python", theme="monokai", line_numbers=True)
            fix_panel = Panel(
                fix_syntax,
                title="[bold bright_green]🛡️ Suggested Surgical Patch (Remediation)[/bold bright_green]",
                border_style="green",
                padding=(0, 1),
            )
            console.print(fix_panel)
            console.print()
    else:
        print("\n" + "=" * 80)
        print(" VULNERABILITY ROOT CAUSE ANALYSIS & REMEDIATIONS")
        print("=" * 80)
        for idx, c in enumerate(triaged_crashes, 1):
            rca = _get_val(c, "root_cause_analysis") or {}
            n = _get_val(c, "attack_name", "")
            p = _get_val(c, "persona", "")
            sev = rca.get("severity", "HIGH")
            vt = rca.get("vulnerability_type", "")
            rc = rca.get("root_cause", "")
            fix = rca.get("fix_diff", "")
            print(f"\n[Finding #{idx}] [{sev}] {n} ({p})")
            print(f"  Vulnerability: {vt}")
            print(f"  Root Cause: {rc}")
            print("  Suggested Fix:")
            for line in fix.splitlines():
                print(f"    {line}")
        print("=" * 80)


def export_markdown_report(
    target_url: str,
    results: list[dict[str, Any]],
    triaged_crashes: list[dict[str, Any]],
    output_path: str = "GHOST_REPORT.md",
) -> Path:
    """
    Automatically saves a clean GitHub-flavored Markdown security audit report
    to disk so developers can attach it to a GitHub Issue or PR.
    """
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    total_attacks = len(results)
    crashes_count = len(triaged_crashes)
    crash_rate = (crashes_count / max(1, total_attacks)) * 100
    avg_latency = (
        sum(float(_get_val(r, "latency_ms", 0.0)) for r in results) / max(1, total_attacks)
    )
    resilient_count = sum(1 for r in results if 400 <= _get_val(r, "status_code", 0) < 500)
    suspicious_count = sum(1 for r in results if 200 <= _get_val(r, "status_code", 0) < 300)
    timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    md: list[str] = [
        "# 👻 GHOST TRAFFIC — Autonomous Chaos QA Audit Report",
        "",
        "> **Generated by Ghost Traffic** • *AI-Driven Autonomous Chaos QA Swarm for BharatCode Build League*",
        "",
        "## 1. Executive Summary",
        "",
        "| Metric | Value |",
        "| :--- | :--- |",
        f"| **Target Endpoint** | `{target_url}` |",
        f"| **Audit Timestamp** | `{timestamp_str}` |",
        f"| **Total Swarm Attacks** | `{total_attacks}` |",
        f"| **Vulnerabilities Triggered (HTTP 500)** | `{crashes_count}` |",
        f"| **Resilient Responses (HTTP 4xx)** | `{resilient_count}` |",
        f"| **Bypassed / Suspicious (HTTP 2xx)** | `{suspicious_count}` |",
        f"| **Failure / Crash Rate** | **`{crash_rate:.1f}%`** |",
        f"| **Average Round-Trip Latency** | `{avg_latency:.1f} ms` |",
        "",
        "---",
        "",
        "## 2. Swarm Telemetry & Attack Assessment",
        "",
        "| # | Status | Verdict | Persona | Attack Vector | Latency |",
        "| :-: | :-: | :-: | :--- | :--- | -: |",
    ]

    for idx, r in enumerate(results, 1):
        status = _get_val(r, "status_code", 0)
        verdict = _get_val(r, "verdict", "UNKNOWN")
        persona = _get_val(r, "persona", "")
        name = _get_val(r, "attack_name", "")
        lat = float(_get_val(r, "latency_ms", 0.0))

        if status >= 500 or verdict == "VULNERABLE":
            status_tag = f"`{status}` 💥"
            verdict_tag = "**VULNERABLE**"
        elif verdict == "RESILIENT":
            status_tag = f"`{status}` 🛡️"
            verdict_tag = "RESILIENT"
        else:
            status_tag = f"`{status}` ⚡"
            verdict_tag = "*SUSPICIOUS*"

        md.append(f"| {idx} | {status_tag} | {verdict_tag} | {persona} | {name} | {lat:.1f} ms |")

    md.extend([
        "",
        "---",
        "",
        "## 3. Vulnerability Root Cause Analysis (RCA) & Remediation",
        "",
    ])

    if triaged_crashes:
        for idx, c in enumerate(triaged_crashes, 1):
            rca = _get_val(c, "root_cause_analysis") or {}
            attack_name = _get_val(c, "attack_name", "Crash Vector")
            persona = _get_val(c, "persona", "Chaos Attacker")
            hypothesis = _get_val(c, "hypothesis", "")
            payload = _get_val(c, "payload", {})
            status = _get_val(c, "status_code", 500)

            severity = rca.get("severity", "CRITICAL")
            vuln_type = rca.get("vulnerability_type", _get_val(c, "error_class", "Internal Server Error"))
            root_cause = rca.get("root_cause", _get_val(c, "error_detail", "Server crashed on unhandled exception."))
            fix_code = rca.get("fix_diff", "# Implement defensive input validation")
            preview = _get_val(c, "response_preview", "")

            md.extend([
                f"### Finding #{idx}: {attack_name}",
                f"- **Severity:** `{severity}`",
                f"- **Vulnerability Classification:** `{vuln_type}`",
                f"- **Attacker Persona:** `{persona}`",
                f"- **Target Response:** HTTP `{status}`",
                f"- **Attack Hypothesis:** *\"{hypothesis}\"*",
                "",
                "#### 💣 Reproducing Payload",
                "```json",
                json.dumps(payload, indent=2),
                "```",
                "",
                f"#### 🔍 Root Cause Analysis",
                f"> {root_cause}",
                "",
                "#### 🛡️ Suggested Surgical Patch",
                "```python",
                fix_code,
                "```",
                "",
                "#### Server Traceback / Response Preview",
                "```",
                preview[:400],
                "```",
                "",
                "---",
                "",
            ])
    else:
        md.append("✅ **No vulnerabilities were triggered.** The target service proved resilient across all attack vectors.\n")

    md.extend([
        "## 4. Next Steps for Engineers",
        "1. Apply the suggested defensive patches to your route handlers.",
        "2. Add strict Pydantic schemas or schema validation middlewares to prevent type confusion.",
        "3. Replace all raw string concatenation queries with parameterized SQL queries.",
        "4. Configure database client connections with `utf8mb4` encoding to safely accept multi-byte emojis.",
        "5. Bound recursive JSON parsing with maximum recursion depth checks.",
        "",
        "---",
        "*Report automatically compiled by Ghost Traffic CLI.*",
    ])

    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    return out_file


class ChaosReporter:
    """
    Class wrapper around reporter operations for stateful reporting workflows.
    """

    def __init__(self, output_dir: str = "./reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def print_banner(self) -> None:
        print_banner()

    def print_personas_preview(self, attacks: list[dict[str, Any]]) -> None:
        print_personas_preview(attacks)

    def print_swarm_results(self, results: list[dict[str, Any]]) -> None:
        print_swarm_results(results)

    def print_ai_triage_cards(self, triaged_crashes: list[dict[str, Any]]) -> None:
        print_ai_triage_cards(triaged_crashes)

    def print_summary(self, results: list[dict[str, Any]]) -> None:
        print_swarm_results(results)
        crashes = [r for r in results if _get_val(r, "is_crash") or _get_val(r, "verdict") == "VULNERABLE"]
        if crashes:
            print_ai_triage_cards(crashes)

    def save_report(
        self,
        results: list[dict[str, Any]],
        filename_prefix: str = "GHOST_REPORT",
    ) -> tuple[Path, Path]:
        """
        Exports results to both machine-readable JSON and GitHub-flavored Markdown.
        """
        crashes = [r for r in results if _get_val(r, "is_crash") or _get_val(r, "verdict") == "VULNERABLE"]
        target_url = (
            _get_val(results[0], "target_url", "http://127.0.0.1:8000")
            if results
            else "http://127.0.0.1:8000"
        )

        md_path = self.output_dir / f"{filename_prefix}.md"
        json_path = self.output_dir / f"{filename_prefix}.json"

        # 1. Export JSON
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        # 2. Export Markdown
        export_markdown_report(
            target_url=target_url,
            results=results,
            triaged_crashes=crashes,
            output_path=str(md_path),
        )

        return json_path, md_path
