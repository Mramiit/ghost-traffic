"""
Ghost Traffic - 1-Click Autonomous Chaos QA Swarm Demo
BharatCode Build League Hackathon (https://bharatcode.ai/hackathon)

Boots the vulnerable target server in the background, executes the
AI Chaos QA Swarm, displays real-time Rich triage cards, and saves
the vulnerability report.
"""

import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

# Ensure UTF-8 output on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def run_demo() -> None:
    base_dir = Path(__file__).parent.resolve()
    target_dir = base_dir / "target_server"

    print("=" * 75)
    print(" 👻 GHOST TRAFFIC: AUTONOMOUS CHAOS QA SWARM (1-CLICK DEMO)")
    print("    BharatCode Build League Hackathon | https://bharatcode.ai")
    print("=" * 75)
    print("[1/3] Starting deliberately vulnerable target server in background...")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(base_dir)
    env["PYTHONUTF8"] = "1"

    server_proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
            "--log-level",
            "warning",
        ],
        cwd=str(target_dir),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        started = False
        for _ in range(40):
            try:
                with urllib.request.urlopen("http://127.0.0.1:8000/docs", timeout=0.5):
                    started = True
                    break
            except Exception:
                time.sleep(0.1)

        if not started:
            print("[NOTE] Direct socket loopback connection was restricted in this environment.")
            print("[INFO] Running in-memory verification suite instead...\n")
            verify_script = base_dir / "test_bugs.py"
            subprocess.run([sys.executable, str(verify_script)], cwd=str(base_dir), env=env)
            return

        print("[OK] Target server active at http://127.0.0.1:8000 (docs at /docs)")
        print("[2/3] Unleashing Ghost Traffic Chaos Swarm across 5 AI personas...\n")

        main_script = base_dir / "main.py"
        schema_path = target_dir / "sample_schema.json"
        report_path = base_dir / "reports" / "GHOST_REPORT.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        subprocess.run(
            [
                sys.executable,
                str(main_script),
                "fuzz",
                "--target",
                "http://127.0.0.1:8000/api/v1/checkout",
                "--schema",
                str(schema_path),
                "--output",
                str(report_path),
            ],
            cwd=str(base_dir),
            env=env,
        )

    finally:
        print("\n[3/3] Shutting down background target server...")
        server_proc.terminate()
        try:
            server_proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            server_proc.kill()
        print("[OK] Demo execution finished.\n")


if __name__ == "__main__":
    run_demo()
