# 👻 Ghost Traffic

> **Autonomous AI-Driven Chaos QA Swarm & Self-Healing Root Cause Triage Engine**  
> *Built for the BharatCode Build League Hackathon (Track: AI Developer Tools / Autonomous Agents)*

[![BharatCode](https://img.shields.io/badge/Powered%20by-BharatCode%20AI%20(qwen--3.8--27b)-orange.svg)](https://bharatcode.ai)
[![Hackathon](https://img.shields.io/badge/Hackathon-BharatCode%20Build%20League-blueviolet.svg)](https://bharatcode.ai/hackathon)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Target-FastAPI%20SUT-009688.svg)](https://fastapi.tiangolo.com)
[![Async HTTPX](https://img.shields.io/badge/Engine-HTTPX%20Swarm-1085c5.svg)](https://www.python-httpx.org/)
[![Terminal UI](https://img.shields.io/badge/UI-Rich%20Terminal-magenta.svg)](https://github.com/Textualize/rich)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

---

## ⚡ The Pitch

Traditional API fuzzers mindlessly spew random byte mutations that get rejected by basic regex filters before ever reaching application code. 

**Ghost Traffic** turns the tables by deploying an autonomous swarm of **AI Chaos Personas** powered by the **BharatCode API (`qwen-3.8-27b`)**. The swarm inspects API schemas, hypothesizes subtle business logic flaws, synthesizes adversarial edge-case payloads, and attacks endpoints concurrently. When a crash (HTTP 500) is triggered, Ghost Traffic captures the leaked traceback, performs automated **Root Cause Analysis (RCA)**, and generates copy-pasteable Python code patches—all rendered in a cyber-security styled terminal UI and exported as publication-ready GitHub Markdown audit reports.

---

## 🔑 Where to Add Your BharatCode API Key

Ghost Traffic is built to work out of the box with **BharatCode's Model API**:

1. **Get your key**: Sign in at [bharatcode.ai](https://bharatcode.ai) and copy your API key (starts with `bc_live_...`).
2. **Open the `.env` file** in the project root (a pre-configured template `.env` has been created for you, or copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```
3. **Paste your key** into `.env`:
   ```ini
   # BharatCode Model API Configuration
   BHARATCODE_API_KEY=bc_live_your_actual_api_key_here
   BHARATCODE_BASE_URL=https://bharatcode.ai/api/model/v1
   BHARATCODE_MODEL=qwen-3.8-27b
   # Alternative supported model: deepseek-v4.1-flash
   ```

> 🛡️ **Zero-Setup Offline Fallback Mode**: Even if you do not have an API key right now or if network access is restricted, Ghost Traffic includes a **bulletproof deterministic fallback engine**. It comes pre-loaded with 8 realistic adversarial attack vectors across all 5 personas and heuristic AST traceback triage so judges can test the full end-to-end workflow immediately!

---

## ⏱️ 1-Click Quickstart (Judge & Demo Friendly)

### Option A: 1-Click Autonomous Demo
Boots the included vulnerable target server, unleashes the AI Chaos Swarm, renders real-time Rich triage cards, and saves the Markdown report in one command:
```bash
python run_demo.py
# Or: python main.py demo
```

### Option B: Step-by-Step Manual Run

**1. Install Dependencies**
```bash
git clone https://github.com/<your-username>/ghost-traffic.git
cd ghost-traffic
pip install -r requirements.txt
```

**2. Start Vulnerable Target Server (Terminal 1)**
```bash
python main.py start-target
```
*The deliberately vulnerable checkout target boots at `http://127.0.0.1:8000` with 5 real backend bugs.*

**3. Unleash Ghost Traffic Swarm (Terminal 2)**
```bash
python main.py fuzz
```

**4. Run In-Memory Verification Test Suite**
```bash
python test_bugs.py
```
*Verifies all 5 deliberate backend crash bugs in-memory without network sockets.*

---

## 🏗️ Architecture

```
 ┌────────────────────────┐
 │   OpenAPI 3.0 / JSON   │
 │   Target Schema File   │
 └───────────┬────────────┘
             │
             ▼
 ┌────────────────────────────────────────────────────────┐
 │ Stage 1: BharatCode AI Engine (qwen-3.8-27b)           │
 │  • Reads schema definitions and field boundaries       │
 │  • Deploys 5 Specialized "Chaos Personas"              │
 └───────────┬────────────────────────────────────────────┘
             │
             ▼ [8 Structured Adversarial Payloads + Hypotheses]
 ┌────────────────────────────────────────────────────────┐
 │ Async HTTPX Chaos Swarm (Controlled Concurrency)       │
 │  • Rate-limited execution via asyncio.Semaphore(3)     │
 │  • Real-time Rich progress bar & latency telemetry     │
 └───────────┬────────────────────────────────────────────┘
             │
             ▼ [HTTP 500 Crash Stack Traces Intercepted]
 ┌────────────────────────────────────────────────────────┐
 │ Stage 2: BharatCode AI Root-Cause Triage (qwen-3.8-27b)│
 │  • Deep Stack-Trace Analysis & CWE Taxonomy Mapping    │
 │  • Automated Generation of 2-4 Line Python Fix Diff    │
 └───────────┬────────────────────────────────────────────┘
             │
             ▼
 ┌────────────────────────────────────────────────────────┐
 │ Developer Output Artifacts                             │
 │  • Rich Monokai Syntax Triage Cards in Terminal        │
 │  • GHOST_REPORT.md (GitHub Issue / PR Ready Audit)     │
 └────────────────────────────────────────────────────────┘
```

---

## 🎭 The 5 Chaos Personas

| Persona | Attack Strategy | Target Vulnerabilities |
| :--- | :--- | :--- |
| 💉 **The SQL Injector** | Crafts unparameterized SQL syntax, stacked queries, and comment bypasses in text fields. | SQL Injection (`CWE-89`), `OperationalError` |
| 👾 **The Unicode Destroyer** | Injects 4-byte UTF-8 emojis (`🚀`), Zero-Width Joiners (`\u200d`), and legacy charset breaks. | Encoding mismatches (`CWE-176`), latin-1 DB crashes |
| 💥 **The Boundary Pusher** | Tests `0`, `-1`, negative inventory reserves, and integer boundaries. | Divide by Zero (`CWE-369`), Numeric Underflows |
| 🔀 **The Type Anarchist** | Injects integers, arrays, or booleans into fields expecting strings. | Type Confusion (`CWE-843`), Unhandled `AttributeError` |
| 📦 **The Nesting Fiend** | Delivers deeply nested JSON objects (> 5 levels) and recursive payloads. | Recursion limits (`CWE-674`), Stack Exhaustion |

---

## 📊 Sample Output & Audit Report

Ghost Traffic automatically writes a publication-ready GitHub-flavored Markdown audit report on every run:
* 📄 **[View Sample Audit Report](reports/SAMPLE_GHOST_REPORT.md)**

```text
 👻 GHOST TRAFFIC v0.1.0 // AUTONOMOUS CHAOS QA SWARM
 BharatCode Build League Hackathon

════════ Finding #1: Integer Coupon Code Type Confusion ════════
  [HIGH] Unhandled Type Confusion (CWE-843)
  Attacker Persona: The Type Anarchist
  Root Cause: Endpoint directly invoked .upper() on coupon_code without verifying it is a str.

💣 Reproducing Adversarial Payload:
{
  "username": "type_confuser",
  "quantity": 1,
  "coupon_code": 99999,
  "shipping_note": "Express courier"
}

🛡️ Suggested Surgical Patch (Remediation):
1  if not isinstance(coupon_code, str):
2      raise HTTPException(status_code=400, detail='coupon_code must be a string')
```

---

## 📁 Repository Structure

```
ghost-traffic/
├── BharatCode.txt            # Mandatory BharatCode hackathon verification file
├── .env                      # Local API keys (pre-created template, git-ignored)
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules for Python, virtualenvs, reports
├── LICENSE                   # MIT License
├── README.md                 # Complete documentation and quickstart
├── run_demo.py               # 1-Click autonomous demo runner for judges
├── main.py                   # Main CLI entrypoint (Typer & Rich)
├── requirements.txt          # Python project dependencies
├── test_bugs.py              # In-memory test suite for bug verification
├── ghost/                    # Core chaos swarm engine
│   ├── __init__.py           # Package version (0.1.0)
│   ├── fuzzer.py             # Asynchronous swarm execution engine
│   ├── llm_client.py         # BharatCode AI API client & persona generator
│   └── reporter.py           # Rich terminal UI & Markdown report generator
├── target_server/            # Deliberately vulnerable mock server
│   ├── app.py                # FastAPI checkout service with 5 deliberate bugs
│   └── sample_schema.json    # JSON schema definition for SUT
└── reports/                  # Generated audit reports
    └── SAMPLE_GHOST_REPORT.md# Sample publication report for judges
```

---

## 🏆 Hackathon Compliance Details

* **Hackathon**: [BharatCode Build League 2026](https://bharatcode.ai/hackathon)
* **Track**: AI Developer Utilities & Autonomous Agents
* **Mandatory File**: `BharatCode.txt` included at repository root.
* **Model Endpoint**: `https://bharatcode.ai/api/model/v1` (`qwen-3.8-27b`)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
