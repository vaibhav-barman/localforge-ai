# LocalForge-AI

**Autonomous, fully offline multi-agent software development and QA engine.**
Built with **LangGraph**, driven entirely by local open-weight models through **Ollama**.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Orchestration](https://img.shields.io/badge/orchestration-LangGraph-orange)
![Inference](https://img.shields.io/badge/inference-Ollama%20(local)-black)
![Tests](https://img.shields.io/badge/tests-pytest-green)
![Network](https://img.shields.io/badge/network-offline%20at%20runtime-success)

---

## Table of Contents

1. [Overview](#1-overview)
2. [Core Multi-Agent Loop Architecture](#2-core-multi-agent-loop-architecture)
3. [Key Engineering Integrations](#3-key-engineering-integrations)
4. [Comprehensive Testing Suite](#4-comprehensive-testing-suite)
5. [Setup & Installation](#5-setup--installation)
6. [Repository Structure](#6-repository-structure)

---

## 1. Overview

LocalForge-AI simulates a complete enterprise **SDLC** (requirements, implementation, verification, remediation) on a single local machine. A task prompt goes in; a spec, working source code, and a QA validation report come out. Nothing leaves the host.

### Design Principles

- [x] **100% offline at runtime.** No API keys, no cloud inference, no telemetry. After the one-time model pull, the engine runs with the network disabled.
- [x] **Local compute, resource-efficient.** Three small-to-mid open-weight models (3B to 8B class) are sequenced rather than run concurrently, which keeps memory pressure low on consumer hardware.
- [x] **Self-correcting execution.** Generated code is executed, linted, and semantically checked. Failures are routed back to the Software Engineer Agent with structured feedback.
- [x] **Deterministic verification over model opinion.** Pass/fail decisions are grounded in exit codes, linter output, and stdout inspection, not in an LLM's self-assessment alone.
- [x] **Auditable artifacts.** Every run produces versioned build folders with specs and QA reports.

---

## 2. Core Multi-Agent Loop Architecture

The pipeline is a **LangGraph state machine**. Three role-specialized agents share a typed execution state (`state.py`). A conditional router decides whether a build ships or loops back for repair.

```
                ┌──────────────────────┐
   User Task ──▶│  Product Manager     │  llama3.1:latest
                │  (spec compilation)  │
                └──────────┬───────────┘
                           │ functional spec
                           ▼
                ┌──────────────────────┐
         ┌─────▶│  Software Engineer   │  qwen2.5-coder:7b
         │      │  (code drafting)     │
         │      └──────────┬───────────┘
         │                 │ source code
         │                 ▼
         │      ┌──────────────────────┐
         │      │  Sandbox + Pyflakes  │  tools.py (subprocess)
         │      │  (execute + lint)    │
         │      └──────────┬───────────┘
         │                 │ telemetry: exit code, stdout, stderr, lint
         │                 ▼
         │      ┌──────────────────────┐
         │      │  QA Tester           │  llama3.2:3b
         │      │  (parse + audit)     │
         │      └──────────┬───────────┘
         │                 │
         │          ┌──────┴───────┐
         │          │ router       │
         │          └──────┬───────┘
         │   FAIL: feedback │        │ PASS
         └──────────────────┘        ▼
                              Package solution_N/
```

### Agent Responsibilities

| Stage | Agent | Model | Responsibility |
|:-----:|-------|-------|----------------|
| 1 | **Product Manager** | `llama3.1:latest` | **Context analysis and functional spec compilation.** Converts the raw task into a structured specification (requirements, expected behavior, acceptance criteria) consumed by downstream agents. |
| 2 | **Software Engineer** | `qwen2.5-coder:7b` | **Target source code syntax drafting.** Generates the implementation from the spec. On repair iterations, it receives the QA diagnostics and revises the previous draft. |
| 3 | **QA Tester** | `llama3.2:3b` | **Telemetry parsing, linter auditing, and self-correction routing.** Interprets execution results and Pyflakes findings, classifies failures, and emits the feedback that drives the retry loop. |

### State and Routing

- **Shared state (`state.py`)** is a `TypedDict` holding the spec, current code, execution telemetry, lint results, QA verdict, and iteration counter. Agents read from and write to this single object, so no hidden side channels exist.
- **Router condition (`graph.py`)** inspects the QA verdict. A passing verdict terminates the graph and triggers packaging. A failing verdict routes control back to the Software Engineer node with the failure context attached.
- **Bounded retries.** The loop is intended to terminate on success or on a retry ceiling so a persistently failing task cannot spin indefinitely.

---

## 3. Key Engineering Integrations

### 3.1 Isolated Subprocess Sandboxing

Generated code is untrusted. `tools.py` never uses `exec()` or `eval()` in the host interpreter; scripts run in a **separate child process**.

- [x] **Subprocess isolation.** Each candidate script executes as its own process; a crash or runaway loop cannot take down the orchestrator.
- [x] **Strict timeout cutoffs.** Execution is killed when the time budget is exceeded, which catches infinite loops and blocking calls and reports them to QA as a distinct failure class.
- [x] **Environment copies.** The child receives a **copy** of the environment with overrides applied, so the parent process environment is never mutated.
- [x] **Headless graphics flags.** Variables that force non-interactive rendering (for example `MPLBACKEND=Agg`, `SDL_VIDEODRIVER=dummy`, `QT_QPA_PLATFORM=offscreen`) prevent generated GUI or plotting code from opening windows and **freezing the pipeline**.
- [x] **Captured telemetry.** Exit code, stdout, and stderr are collected and passed into shared state.

```python
# Conceptual shape of the sandbox call
result = subprocess.run(
    [sys.executable, script_path],
    capture_output=True,
    text=True,
    timeout=TIMEOUT_SECONDS,
    env=sandbox_env,          # copy of os.environ + headless overrides
)
```

### 3.2 Static Code Quality Linting

Passing at runtime is not the same as being clean. **Pyflakes** runs against every draft.

- [x] Detects **unused imports** and **unaccessed local variables**
- [x] Flags **undefined names** and other statically detectable defects
- [x] Findings are fed to the QA agent as structured input, so **dead code is treated as a defect**, not a warning to ignore

### 3.3 Semantic Logic Output Verification

A script can exit with code `0` and still do nothing useful. The QA stage includes an explicit **semantic check**:

- [x] Scripts that compile and exit cleanly but emit **zero lines of stdout** are flagged as failures
- [x] The failure reason is returned to the Software Engineer Agent as actionable feedback (for example, "the program produced no observable output")
- [x] Closes the gap between "syntactically valid" and "behaviorally meaningful"

### 3.4 Dynamic Sequential Build Separation

Each successful run is packaged into its own incrementally numbered directory under `workspace/`, so previous builds are never overwritten.

```
workspace/
├── solution_1/
│   ├── <generated source>
│   ├── product_spec.md        # PM Agent specification
│   └── qa_report.md           # QA validation report
├── solution_2/
│   └── ...
└── solution_N/
```

- [x] **Auto-incrementing indices** computed from existing folders
- [x] **Product specification** and **Markdown QA validation report** bundled with every build
- [x] `workspace/` is **git-ignored** and treated as disposable runtime output

---

## 4. Comprehensive Testing Suite

The `tests/` directory contains a **Pytest** suite that verifies the infrastructure the agents depend on, independent of any LLM output. This keeps the harness deterministic and CI-friendly.

| Area | What is verified |
|------|------------------|
| **Linter exceptions** | Pyflakes integration surfaces unused imports and undefined names, and handles malformed source without crashing the pipeline |
| **Input stream simulations** | Scripts that read from `stdin` are exercised with simulated input so interactive programs do not hang the sandbox |
| **Directory index increments** | `solution_N` numbering advances correctly across consecutive builds and does not overwrite existing folders |

```bash
pytest -v
```

- [x] No Ollama or model access is required to run the suite
- [x] Tests target `src/tools.py`, the execution and file-system layer

---

## 5. Setup & Installation

### Prerequisites

- Python **3.10+**
- [Ollama](https://ollama.com/download) installed and running locally
- Disk space and RAM sufficient for the three models listed below

### Step 1: Clone the repository

```bash
git clone https://github.com/<your-username>/localforge-ai.git
cd localforge-ai
```

### Step 2: Pull the local models

Requires a network connection **once**. Afterwards the engine runs offline.

```bash
ollama pull llama3.1:latest
ollama pull qwen2.5-coder:7b
ollama pull llama3.2:3b
```

Verify:

```bash
ollama list
```

### Step 3: Create and activate a virtual environment

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

### Step 4: Install dependencies

```bash
pip install -r requirements.txt
```

Runtime dependencies: `langgraph`, `langchain-ollama`, `pyflakes`, `pytest`.

### Step 5: Run the engine

Make sure the Ollama service is running, then:

```bash
python main.py
```

Terminal output includes real-time timestamped stage transitions rendered by `ui.py`.

### Step 6: View run metrics

```bash
python resume.py
```

Renders a CLI execution matrix summarizing run results.

### Step 7: Run the test suite

```bash
pytest -v
```

### Troubleshooting

| Symptom | Check |
|---------|-------|
| Connection refused to Ollama | Confirm the service is running (`ollama serve`) |
| Model not found | Re-run the matching `ollama pull` command |
| Slow generation | Close other memory-heavy applications; models are loaded sequentially |

---

## 6. Repository Structure

```
localforge-ai/
├── src/
│   ├── __init__.py          # (Package initialization)
│   ├── agents.py            # (LLM prompt logic for PM, Coder, and QA Analyzer)
│   ├── graph.py             # (LangGraph state machine loop and router condition)
│   ├── state.py             # (TypedDict shared application execution state memory)
│   ├── tools.py             # (Subprocess script sandboxing and pyflakes engine context)
│   └── ui.py                # (Terminal visualization engine with real-time timestamps)
├── tests/
│   ├── __init__.py          # (Package initialization)
│   └── test_tools.py        # (Pytest infrastructure verification suite)
├── workspace/               # (Git-ignored sandbox directory tracking dynamic builds)
├── .gitignore               # (Excludes runtime build logs, virtual environments, and caches)
├── main.py                  # (Application interface entry point)
├── requirements.txt         # (Project runtime dependencies: langgraph, langchain-ollama, pyflakes, pytest)
└── resume.py                # (CLI execution matrix rendering resume metrics)
```

### Module Map

| Module | Role |
|--------|------|
| `src/agents.py` | Prompt construction and LLM invocation for the PM, Coder, and QA roles |
| `src/graph.py` | Node wiring, edges, and the conditional router that implements the repair loop |
| `src/state.py` | Single typed state contract shared across all nodes |
| `src/tools.py` | Sandboxed execution, Pyflakes linting, stdout verification, and build packaging |
| `src/ui.py` | Timestamped terminal output for pipeline observability |
| `main.py` | CLI entry point |
| `resume.py` | Execution matrix and metrics renderer |

---

## Security Notes

- Generated code runs in a **child process with a timeout**, but a subprocess is **not a full security boundary**. For hostile or high-risk workloads, run LocalForge-AI inside a container or VM.
- `workspace/` contains model-generated code. **Review before executing outside the sandbox.**

---

## License

Add your license of choice here (for example, MIT).
