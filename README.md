# 👻 Ghost Traffic

> **Autonomous AI-Driven Chaos QA Swarm & Root Cause Triage Engine**  
> *Built for the BharatCode Build League Hackathon*

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 💡 Overview

Traditional API fuzzing relies on random bit flips or brute-force dictionary attacks that waste compute testing nonsensical inputs. **Ghost Traffic** turns the tables by deploying an **Autonomous Chaos QA Swarm** powered by LLMs.

Ghost Traffic analyzes your OpenAPI/JSON schemas and synthesizes context-aware, adversarial payloads across specialized **Chaos Personas**. When the target server crashes (HTTP 500), Ghost Traffic intercepts the stack trace, diagnoses the root cause with AI, and generates actionable triage cards and publication-ready Markdown audit reports.

---

## 🎯 Key Features

- **🧠 Autonomous Swarm Personas**:
  - **The SQL Injector**: Synthesizes injection strings that bypass naive ORM and raw query filters.
  - **The Boundary Pusher**: Explores zero-division, negative numbers, inventory underflow, and numeric limits.
  - **The Unicode Destroyer**: Crafts 4-byte UTF-8 emojis and zero-width joiners (ZWJ/ZWNJ) to break legacy codecs.
  - **The Nesting Fiend**: Injects deeply nested JSON objects designed to trigger recursion limits.
  - **The Type Anarchist**: Delivers type-confusion payloads (e.g., integers/lists where strings are expected).

- **🔍 Automatic Root Cause Analysis (RCA)**:
  - Detects HTTP 500 crashes in real-time.
  - Passes stack traces and request payloads to the AI triage engine.
  - Generates clear remediation snippets and code fixes.

- **📊 Rich Terminal UI & Markdown Audits**:
  - Live execution tables powered by `Rich`.
  - Color-coded security verdicts (`VULNERABLE`, `RESILIENT`, `SUSPICIOUS`).
  - Auto-exports timestamped reports to `reports/chaos_report_*.md`.

- **🎯 Built-in Deliberately Vulnerable Target**:
  - Includes a mock checkout server (`POST /api/v1/checkout`) with 5 deliberate backend bugs for testing and live demonstrations.

---

## 🏗️ Architecture

```
                    ┌────────────────────────┐
                    │   OpenAPI / JSON       │
                    │   Target Schema        │
                    └───────────┬────────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │  BharatCode AI Engine  │
                    │   (5 Chaos Personas)   │
                    └───────────┬────────────┘
                                │
                 ┌──────────────┴──────────────┐
                 ▼                             ▼
       [Adversarial Payloads]        [Concurrent Execution]
                 │                             │
                 └──────────────┬──────────────┘
                                ▼
                    ┌────────────────────────┐
                    │   System Under Test    │
                    │   (Target API Server)  │
                    └───────────┬────────────┘
                                │
                 ┌──────────────┴──────────────┐
                 ▼                             ▼
           [HTTP 200/400]                [HTTP 500 Crashes]
             (Handled)                   (Full Stack Trace)
                                               │
                                               ▼
                                    ┌──────────────────────┐
                                    │ AI Root Cause Triage │
                                    └──────────┬───────────┘
                                               │
                                               ▼
                                    ┌──────────────────────┐
                                    │ Rich Terminal Cards  │
                                    │  & Markdown Audits   │
                                    └──────────────────────┘
```

---

## 🚀 Quick Start

### 1. Clone & Set Up Environment

```bash
git clone https://github.com/<your-username>/ghost-traffic.git
cd ghost-traffic

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the template `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` to supply your BharatCode or OpenAI API credentials:

```ini
BHARATCODE_API_KEY=your_bharatcode_api_key_here
BHARATCODE_BASE_URL=https://api.bharatcode.ai/v1
BHARATCODE_MODEL=qwen-3.8-27b
```

> **Note**: Even without an active API key, Ghost Traffic includes built-in offline payload fallbacks and heuristic triage so you can run the full suite anytime!

### 3. Start the Vulnerable Target Server

In one terminal, start the included vulnerable target server:

```bash
python main.py target
```

The server will boot at `http://127.0.0.1:8000`. You can inspect the interactive OpenAPI documentation at `http://127.0.0.1:8000/docs`.

### 4. Run the Chaos QA Swarm

In another terminal, launch the chaos swarm:

```bash
python main.py fuzz --target-url http://127.0.0.1:8000 --concurrency 3
```

### 5. Run Verification Tests

Run the in-memory test suite to verify all 5 deliberate backend bug vectors:

```bash
python test_bugs.py
```

---

## 🛠️ CLI Reference

```
Usage: python main.py [COMMAND] [OPTIONS]

Commands:
  target    Start the deliberately vulnerable FastAPI target server locally.
  fuzz      Launch the autonomous chaos QA swarm against a target endpoint.
  version   Display current version of Ghost Traffic.
```

### `python main.py fuzz` Options

| Option | Type | Default | Description |
|---|---|---|---|
| `--target-url` | `TEXT` | `http://127.0.0.1:8000` | Target server base URL |
| `--endpoint` | `TEXT` | `/api/v1/checkout` | Target API endpoint path |
| `--schema` | `PATH` | `target_server/sample_schema.json` | Path to OpenAPI/JSON schema |
| `--concurrency` | `INT` | `3` | Concurrent worker tasks |
| `--delay` | `FLOAT` | `0.35` | Delay in seconds between requests |
| `--timeout` | `FLOAT` | `5.0` | HTTP request timeout in seconds |

---

## 📁 Repository Structure

```
ghost-traffic/
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules for Python, virtualenvs, reports
├── main.py                   # Main CLI entrypoint (Typer & Rich)
├── requirements.txt          # Python project dependencies
├── test_bugs.py              # In-memory test suite for bug verification
├── README.md                 # Project documentation and guide
├── ghost/                    # Core chaos engine package
│   ├── __init__.py           # Package version and metadata
│   ├── fuzzer.py             # Asynchronous swarm execution engine
│   ├── llm_client.py         # BharatCode / OpenAI LLM integration & personas
│   └── reporter.py           # Rich terminal UI & Markdown report generator
└── target_server/            # Deliberately vulnerable mock server
    ├── app.py                # FastAPI checkout service with 5 deliberate bugs
    └── sample_schema.json    # JSON schema definition for SUT
```

---

## 👥 Hackathon Team & Acknowledgements

Developed for the **BharatCode Build League Hackathon**.  
Special thanks to the BharatCode team for providing developer tooling and model endpoints.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
