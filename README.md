# 👻 Ghost Traffic

> **Autonomous AI-Driven Chaos QA Swarm & Self-Healing Root Cause Triage Engine**  
> *Built for the BharatCode Build League Hackathon (Track: Coding & Developer Tools / Work & Automation)*

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![BharatCode](https://img.shields.io/badge/Powered%20by-BharatCode%20AI%20(qwen--3.8--27b)-orange.svg)](https://bharatcode.ai)
[![FastAPI](https://img.shields.io/badge/Target-FastAPI%20SUT-009688.svg)](https://fastapi.tiangolo.com)
[![Async HTTPX](https://img.shields.io/badge/Engine-HTTPX%20Swarm-1085c5.svg)](https://www.python-httpx.org/)
[![Terminal UI](https://img.shields.io/badge/UI-Rich%20Terminal-magenta.svg)](https://github.com/Textualize/rich)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

---

## ⚡ The Pitch

Traditional API fuzzers mindlessly spew random byte mutations that get rejected by basic regex filters before ever reaching application code. **Ghost Traffic** deploys an autonomous swarm of **AI Chaos Personas** that reason about API schemas and business logic constraints to trigger real unhandled backend crashes—then automatically analyzes the leaked stack traces to produce surgical, copy-pasteable Python code patches.

---

## 🏗️ Architecture

Ghost Traffic operates a dual-stage agentic loop orchestrated with the **BharatCode API (`qwen-3.8-27b`)**:

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
| 💉 **The SQL Injector** | Crafts unparameterized SQL syntax, stacked queries, and comment bypasses in text fields. | SQL Injection (CWE-89), OperationalErrors |
| 👾 **The Unicode Gremlin** | Injects 4-byte UTF-8 emojis, Zero-Width Joiners (`\u200d`), and RTL overrides. | Encoding mismatches (CWE-172), latin-1 DB crashes |
| 💥 **The Boundary Breaker** | Tests `0`, `-1`, negative reserves, and integer boundaries. | Divide by Zero (CWE-369), Numeric Underflows |
| 🔀 **The Type-Switcher** | Injects integers, arrays, or booleans into fields expecting strings. | Type Confusion (CWE-843), Unhandled `AttributeError` |
| 📦 **The JSON Hoarder** | Delivers deeply nested objects ($> 5$ levels) and recursive payloads. | Recursion limits (CWE-674), Stack Exhaustion |

---

## ⏱️ 60-Second Quickstart

### Step 1: Install Dependencies
```bash
git clone https://github.com/<your-username>/ghost-traffic.git
cd ghost-traffic
pip install -r requirements.txt
```

### Step 2: Configure Environment (Optional)
```bash
cp .env.example .env
```
*(Ghost Traffic includes a deterministic fallback chaos suite and heuristic triage engine, so it runs out-of-the-box even without an API key!)*

### Step 3: Start the Vulnerable Server (Terminal 1)
```bash
uvicorn target_server.app:app --port 8000
```
*The deliberately vulnerable checkout target boots at `http://127.0.0.1:8000` with 5 unhandled backend bugs.*

### Step 4: Unleash Ghost Traffic (Terminal 2)
```bash
python main.py
```
*Ghost Traffic summons the personas, fires the swarm against `POST /api/v1/checkout`, triages all crashes with AI, and saves `GHOST_REPORT.md`!*

---

## 🖥️ Sample Terminal Output

```text
 👻 GHOST TRAFFIC v0.1.0 // AUTONOMOUS CHAOS QA SWARM
 BharatCode Build League Hackathon

🎯 Armed Chaos Swarm Personas & Target Attack Vectors:
┏━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ # ┃ Chaos Persona        ┃ Attack Vector                      ┃ Target Hypothesis                       ┃
┡━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 1 │ The SQL Injector     │ Coupon Code SQLi Operator Bypass   │ Raw query string triggers SQL error     │
│ 2 │ The Unicode Gremlin  │ 4-Byte Emoji UTF-8 Driver Crash    │ 4-byte emojis crash legacy latin-1 DB   │
│ 3 │ The Boundary Breaker │ Zero Quantity Division Underflow   │ Quantity 0 triggers ZeroDivisionError   │
│ 4 │ The Boundary Breaker │ Negative Inventory Reserve         │ Negative quantity triggers underflow    │
│ 5 │ The Type-Switcher    │ Integer Coupon Code Type Confusion │ Int coupon causes AttributeError .upper │
│ 6 │ The JSON Hoarder     │ Deeply Nested Recursive Explosion  │ Nesting > 5 triggers RecursionError     │
└───┴──────────────────────┴────────────────────────────────────┴─────────────────────────────────────────┘

Unleashing Ghost Traffic Swarm... [━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━] 100% • 00:03

⚡ Chaos Swarm Telemetry & Security Assessment:
┏━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ # ┃ Persona              ┃ Attack Vector                      ┃ HTTP Status┃ Latency  ┃ Verdict    ┃
┡━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 1 │ The SQL Injector     │ Coupon Code SQLi Operator Bypass   │    500     │ 14.2ms   │ VULNERABLE │
│ 2 │ The Unicode Gremlin  │ 4-Byte Emoji UTF-8 Driver Crash    │    500     │ 12.1ms   │ VULNERABLE │
│ 3 │ The Boundary Breaker │ Zero Quantity Division Underflow   │    500     │ 11.5ms   │ VULNERABLE │
│ 4 │ The Boundary Breaker │ Negative Inventory Reserve         │    500     │ 10.8ms   │ VULNERABLE │
│ 5 │ The Type-Switcher    │ Integer Coupon Code Type Confusion │    500     │ 13.0ms   │ VULNERABLE │
│ 6 │ The JSON Hoarder     │ Deeply Nested Recursive Explosion  │    500     │ 18.4ms   │ VULNERABLE │
└───┴──────────────────────┴────────────────────────────────────┴━━━━━━━━━━━━┴━━━━━━━━━━┴━━━━━━━━━━━━┘

════════ Finding #1: Integer Coupon Code Type Confusion ════════
  [HIGH] Unhandled Type Confusion (CWE-843)
  Attacker Persona: The Type-Switcher
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
3  coupon_clean = coupon_code.upper()

✔ Security Audit Report successfully compiled!
File Location: c:\Users\itzmr\Hackathon\BharatCode\ghost-traffic\GHOST_REPORT.md
```

---

## 📄 Sample Generated `GHOST_REPORT.md`

```markdown
# 👻 GHOST TRAFFIC — Autonomous Chaos QA Audit Report
> Generated by Ghost Traffic • AI-Driven Autonomous Chaos QA Swarm for BharatCode Build League

## 1. Executive Summary
| Metric | Value |
| :--- | :--- |
| **Target Endpoint** | `http://127.0.0.1:8000/api/v1/checkout` |
| **Total Swarm Attacks** | `8` |
| **Vulnerabilities Triggered (HTTP 500)** | `6` |
| **Failure / Crash Rate** | **`75.0%`** |
| **Average Round-Trip Latency** | `13.3 ms` |

---

## 2. Vulnerability Root Cause Analysis (RCA) & Remediation

### Finding #1: Coupon Code Raw Query SQL Injection Bypass
- **Severity:** `CRITICAL`
- **Vulnerability Classification:** `Improper Neutralization of Special Elements in SQL Command (CWE-89)`
- **Attacker Persona:** `The SQL Injector`
- **Target Response:** HTTP `500`

#### 💣 Reproducing Payload
```json
{
  "username": "shopper_sqli",
  "quantity": 1,
  "coupon_code": "' OR 1=1 --"
}
```

#### 🔍 Root Cause Analysis
> Unsanitized user-controlled coupon_code is concatenated directly into raw SQL string without parameterized query bindings.

#### 🛡️ Suggested Surgical Patch
```python
# Use parameterized SQL queries instead of raw string concatenation:
cursor.execute('SELECT * FROM coupons WHERE code = ?', (coupon_code,))
```
```

---

## 🛠️ CLI Reference

```bash
# Run swarm against custom target and schema
python main.py --target http://127.0.0.1:8000/api/v1/checkout --schema target_server/sample_schema.json --output GHOST_REPORT.md

# Shorthand options
python main.py fuzz -t http://127.0.0.1:8000/api/v1/checkout -o GHOST_REPORT.md

# Run target server
python main.py start-target --port 8000

# Verify in-memory bug suite without network dependencies
python main.py verify
```

---

## 👥 Hackathon Team & Acknowledgements

Developed for the **BharatCode Build League Hackathon**.  
Powered by the **BharatCode API (`qwen-3.8-27b`)**.

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
