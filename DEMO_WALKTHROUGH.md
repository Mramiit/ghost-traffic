# 🎬 Ghost Traffic — Hackathon Demo Video & Presentation Guide

> **BharatCode Build League Hackathon**  
> **Track**: Coding & Developer Tools / Work & Automation  
> **Recommended Video Duration**: 2:00 – 2:45 minutes  
> **Presenter Strategy**: Split-screen Terminal Setup (Left: Target API Server, Right: Ghost Traffic Swarm)

---

## 🖥️ Screen Layout Setup Before Recording

1. **Split your screen into two side-by-side terminal windows**:
   - **Terminal 1 (Left Window)**: Ready to launch the vulnerable FastAPI checkout target server.
   - **Terminal 2 (Right Window)**: Ready to run the `ghost-traffic` CLI.
2. Ensure terminal font size is legible (16–18pt) with a dark theme (e.g., Tokyo Night, Monokai, or Catppuccin).
3. Have your code editor (VS Code / Antigravity) open in the background with `target_server/app.py` and `sample_schema.json` open for quick B-roll.

---

## ⏱️ Video Script & Step-by-Step Flow

### 0:00 – 0:30 | The Hook: Why Traditional Fuzzing is Broken
- **What to show**: Slide or face-cam + Terminal title.
- **Presenter Script**:
  > *"Every developer knows the pain of unexpected production crashes. But why didn't QA catch them? Because traditional fuzzers are dumb—they spew random byte garbage that gets blocked by standard regex before ever reaching core application logic.*  
  > *Meet **Ghost Traffic**: an autonomous chaos QA swarm powered by the **BharatCode API (`qwen-3.8-27b`)**. Instead of random noise, Ghost Traffic understands your OpenAPI schemas and deploys 5 specialized AI Chaos Personas to break your backend on real business logic—and then writes the code patches to fix them."*

---

### 0:30 – 1:00 | Terminal 1: Launching the Target Server
- **What to show**: Switch to Terminal 1 (Left).
- **Command to run**:
  ```bash
  uvicorn target_server.app:app --port 8000
  ```
- **Presenter Script**:
  > *"Here on the left, we're booting our target e-commerce checkout service. It has 5 realistic, deliberate backend bugs: an inventory underflow zero-division error, unparameterized SQL query injection, a legacy latin-1 database driver crash on 4-byte emojis, a deep-nesting recursion memory bomb, and unhandled type confusion."*

---

### 1:00 – 1:45 | Terminal 2: Unleashing the Swarm
- **What to show**: Switch to Terminal 2 (Right).
- **Command to run**:
  ```bash
  python main.py
  ```
- **Presenter Script**:
  > *"Now watch this. With one simple command, Ghost Traffic analyzes the checkout schema and summons 5 distinct Chaos Personas:*  
  > *• **The SQL Injector** testing unescaped raw queries.*  
  > *• **The Unicode Gremlin** crafting 4-byte emojis and zero-width joiners.*  
  > *• **The Boundary Breaker** testing zero and negative inventory.*  
  > *• **The Type-Switcher** injecting integers where strings are expected.*  
  > *• **The JSON Hoarder** constructing recursive payloads.*  
  > *As the swarm fires with controlled concurrency, you see the live progress bar and instant telemetry. Look at that—6 out of 8 attacks triggered unhandled HTTP 500 crashes!"*

---

### 1:45 – 2:20 | The Climax: AI Root Cause Analysis & Instant Code Patches
- **What to show**: Scroll through the Rich Monokai Triage Cards in Terminal 2.
- **Presenter Script**:
  > *"Here is where the magic happens. Ghost Traffic intercepts the runtime stack traces, pipes them through the BharatCode API, and performs automated Root Cause Analysis in real-time:*  
  > *• It maps each crash to standardized CWE taxonomy—like CWE-843 Type Confusion and CWE-369 Divide by Zero.*  
  > *• It explains exactly why the backend crashed.*  
  > *• And look at this: it generates a surgical 2-to-4 line defensive Python patch that developers can immediately copy and paste into their route handler!"*

---

### 2:20 – 2:45 | The Deliverable & Closing: `GHOST_REPORT.md`
- **What to show**: Open `GHOST_REPORT.md` in the editor/preview.
- **Presenter Script**:
  > *"Finally, Ghost Traffic automatically compiles everything into an audit-ready Markdown report—`GHOST_REPORT.md`—ready to attach directly to a GitHub Issue or Pull Request.*  
  > *Ghost Traffic transforms security and chaos testing from a tedious manual chore into an autonomous, self-healing developer workflow. Built with pride for the BharatCode Build League. Thank you!"*

---

## 💡 Quick Tips for High Hackathon Scores

1. **Highlight BharatCode API (`qwen-3.8-27b`)**:
   - Emphasize how the model powers both **Stage 1 (Payload Synthesis)** and **Stage 2 (Stack-Trace Triage & Patching)**.
2. **Mention Offline Resilience**:
   - Note that Ghost Traffic features built-in deterministic heuristic fallbacks so live demos never fail even if Wi-Fi fluctuates on stage.
3. **Show the GitHub CI Badge**:
   - Mention that Ghost Traffic includes automated CI regression suites running across Python 3.10, 3.11, and 3.12.

