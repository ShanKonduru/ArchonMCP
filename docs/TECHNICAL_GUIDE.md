# ArchonMCP — Technical Guide

> **Version:** 0.1.5  
> **Repository:** https://github.com/ShanKonduru/ArchonMCP  
> **Protocol:** Model Context Protocol (MCP) over stdio  
> **License:** MIT

---

## Table of Contents

1. [What is ArchonMCP?](#1-what-is-archonmcp)
2. [How It Works](#2-how-it-works)
3. [Capabilities](#3-capabilities)
4. [Features](#4-features)
5. [Supported Tech Stacks](#5-supported-tech-stacks)
6. [Governance Artifacts Deployed](#6-governance-artifacts-deployed)
7. [Benefits](#7-benefits)
8. [Use Cases](#8-use-cases)
9. [Local Installation and CLI Usage](#9-local-installation-and-cli-usage)
10. [MCP Server Usage in VS Code](#10-mcp-server-usage-in-vs-code)
11. [MCP Server Usage in Cursor](#11-mcp-server-usage-in-cursor)
12. [MCP Server Usage in Other AI IDEs](#12-mcp-server-usage-in-other-ai-ides)
13. [Architecture Deep Dive](#13-architecture-deep-dive)
14. [Project Structure](#14-project-structure)
15. [Troubleshooting](#15-troubleshooting)

---

## 1. What is ArchonMCP?

**ArchonMCP** is a Python-based governance framework server that automatically deploys structured governance artifacts into any software project. It speaks the **Model Context Protocol (MCP)**, which means it can be wired directly into AI-assisted development tools like VS Code (with GitHub Copilot or Cline), Cursor, Claude Desktop, and any other MCP-compatible IDE.

The core idea is simple: when you start a new project (or adopt governance on an existing one), you should not be writing rulebooks, security runbooks, definition-of-done checklists, and AI instruction files by hand. ArchonMCP detects your tech stack and deploys all of that in a single command.

### The Problem It Solves

| Without ArchonMCP | With ArchonMCP |
|---|---|
| Every team writes governance files from scratch | One command deploys a complete, stack-aware framework |
| AI assistants lack project-specific rules | `copilot-instructions.md` guides every AI interaction |
| Security runbooks exist in wikis or are forgotten | Security skill lives in the repo, versioned alongside code |
| ADRs and stories have no home | Structured `docs/` layout is created automatically |
| Stack detection is manual or tribal knowledge | Automatic detection scans project files |

---

## 2. How It Works

```
┌──────────────────────────────────────────────────┐
│                  Your Project Folder              │
│                                                   │
│   (empty or partial)                              │
└──────────────┬───────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────┐
│               ArchonMCP                           │
│                                                   │
│  1. detect_tech_stack()                           │
│     Scans files → identifies stack                │
│                                                   │
│  2. create_governance_structure()                 │
│     Writes templates tailored to detected stack   │
└──────────────┬───────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────┐
│             Deployed Governance                   │
│                                                   │
│   .github/copilot-instructions.md                 │
│   .github/skills/security.md                      │
│   .github/skills/migration.md                     │
│   .github/skills/done.md                          │
│   .github/prompts/gap-analysis.md                 │
│   .github/prompts/harden.md                       │
│   .github/prompts/done.md                         │
│   .github/naming-bootstrap.md                     │
│   docs/adr/README.md                              │
│   docs/stories/README.md                          │
└──────────────────────────────────────────────────┘
```

ArchonMCP operates in two modes:

- **CLI mode** — a local command-line tool (`archon-mcp init`, `archon-mcp detect`)
- **MCP Server mode** — a stdio-based server that AI IDEs connect to as a tool

---

## 3. Capabilities

### Stack Detection

ArchonMCP scans a project directory and classifies it into one of six stack profiles based on the presence of specific files and file types:

| Signal File / Extension | Detected Role |
|---|---|
| `package.json` + `tsconfig.json` or `.tsx/.jsx` | React / TypeScript frontend |
| `next.config.js`, `next.config.ts`, `next.config.mjs` | Next.js frontend |
| `angular.json` | Angular frontend |
| `vite.config.ts`, `vite.config.js`, `vue.config.js` | Vue 3 frontend |
| `main.py`, `app.py` (+ no `manage.py`) | FastAPI backend |
| `manage.py` | Django backend |
| `pom.xml`, `build.gradle`, `build.gradle.kts` | Spring Boot backend |
| `.tsx`, `.jsx` extensions in directory | React component files |

When no signals match, the stack falls back to **Generic**.

When governance files from a previous `archon-mcp init` are present, the stack is also recovered from:
1. `.github/archon-stack.txt` — exact persisted stack name (highest priority)
2. `.github/copilot-instructions.md` — stack name embedded in content (fallback)

### Governance Scaffolding

For every supported stack, ArchonMCP deploys a set of fully-rendered Markdown governance documents tailored to that stack's languages, frameworks, and conventions.

### MCP Tool Exposure

Over MCP, ArchonMCP exposes the `init_governance` tool with two optional parameters:

| Parameter | Type | Description |
|---|---|---|
| `root_directory` | string | Absolute path to the project root (defaults to CWD) |
| `stack` | enum | One of the supported stack names (auto-detected if omitted) |

---

## 4. Features

### One-Command Governance Setup
A single command — CLI or MCP tool call — deploys 11 governance files and 4 directories, correctly tailored for your stack.

### Intelligent Stack Auto-Detection
No configuration needed. ArchonMCP inspects your project and determines the correct stack profile. If it already initialized a project, it reads its own metadata to remain consistent across runs.

### Stack-Aware Templates
Each of the 6 supported stacks gets its own version of every governance file. A React-FastAPI-Postgres project receives FastAPI-specific security patterns; an Angular-SpringBoot-MySQL project receives Flyway migration guidance and Spring Security patterns.

### Persistent Stack Metadata
After `init`, the chosen stack is written to `.github/archon-stack.txt`, so subsequent `detect` runs always return the correct stack — even in a project that contains only governance files.

### Idempotent Execution
Running `archon-mcp init` on an already-initialized project is safe. All file writes use `exist_ok=True` on directories and overwrite files in place; no errors are raised.

### Dual-Mode Operation
The same Python package runs either as a local CLI tool or as a persistent stdio MCP server consumed by AI IDEs.

### Cross-Platform Compatibility
All file operations use Python's `pathlib`, ensuring correct path separators and behavior on Windows, macOS, and Linux.

### Verbose Output
Pass `--verbose` to `archon-mcp init` to see every directory and file that was created.

### Structured Error Reporting
Errors during scaffold creation are caught and returned in a structured list rather than crashing the process, allowing partial-success scenarios to be handled gracefully.

---

## 5. Supported Tech Stacks

| Stack Profile | Frontend | Backend | Database |
|---|---|---|---|
| `React-FastAPI-Postgres` | React + TypeScript | FastAPI (Python) | PostgreSQL |
| `Next.js-Django-Postgres` | Next.js (App Router) | Django REST Framework | PostgreSQL |
| `Vue-Express-MongoDB` | Vue 3 (Composition API) | Express / Node.js | MongoDB |
| `Angular-SpringBoot-MySQL` | Angular (Standalone) | Spring Boot | MySQL |
| `React-Node-MongoDB` | React + TypeScript | Express / Node.js | MongoDB |
| `Generic` | Any | Any | Any |

---

## 6. Governance Artifacts Deployed

### `.github/copilot-instructions.md`
High-level governance rules injected into every AI assistant session. Contains:
- Project context (stack, purpose)
- AI assistant expectations (ADR references, PR workflow)
- Code quality standards per language/framework
- Review checklist

### `.github/skills/security.md`
A structured security runbook that walks through:
- Pre-implementation security checklist
- Frontend, backend, and database security measures specific to the stack
- Post-implementation verification steps

### `.github/skills/migration.md`
A data migration runbook covering:
- Pre-migration planning and backup procedures
- Schema preparation patterns (reversible migrations)
- Transaction management during data moves
- Post-migration validation steps

### `.github/skills/done.md`
A Definition of Done checklist covering:
- Code quality gates (tests, linting, coverage thresholds)
- Documentation requirements
- Testing requirements (unit, integration, E2E)
- Deployment readiness criteria

### `.github/prompts/gap-analysis.md`
A slash-command prompt (`/gap-analysis`) that instructs the AI to analyze the codebase for missing governance, untested paths, and architecture gaps.

### `.github/prompts/harden.md`
A slash-command prompt (`/harden`) that instructs the AI to perform a full security review and recommend hardening steps.

### `.github/prompts/done.md`
A slash-command prompt (`/done`) that validates a feature against the Definition of Done checklist.

### `.github/naming-bootstrap.md`
Naming conventions for files, components, functions, routes, and database objects — tailored per stack.

### `docs/adr/README.md`
Seed file for Architecture Decision Records. Teams add individual ADR files here as decisions are made.

### `docs/stories/README.md`
Seed file for feature stories and acceptance criteria documentation.

---

## 7. Benefits

### For Individual Developers
- Start a new project with production-quality governance in seconds
- AI assistants immediately understand project conventions through `copilot-instructions.md`
- Security runbooks prevent common mistakes specific to the chosen stack

### For Teams
- Shared governance baseline reduces on-boarding time
- All team members and AI tools operate from the same rulebook
- ADR and story directories create a culture of documented decision-making

### For Tech Leads / Architects
- Enforce code quality standards through AI-readable instructions rather than verbal reminders
- Custom prompts (`/gap-analysis`, `/harden`) give structured ways to audit the codebase
- Stack-specific migration runbooks reduce the risk of data loss during schema changes

### For AI-Assisted Development Workflows
- MCP server mode allows AI tools to invoke governance setup as a first-class operation
- `copilot-instructions.md` is the first file AI IDEs load; ArchonMCP ensures it has meaningful, stack-specific content
- All governance files are Markdown, so AI models read them natively with no extra parsing

---

## 8. Use Cases

### Starting a New Full-Stack Project
```bash
mkdir my-app
cd my-app
archon-mcp init --stack React-FastAPI-Postgres
```
Governance is in place before the first line of application code is written.

### Adopting Governance on an Existing Project
```bash
cd /path/to/existing-project
archon-mcp detect        # Confirm stack is identified correctly
archon-mcp init          # Deploy governance based on detected stack
```

### CI/CD Integration
Add to a GitHub Actions workflow to ensure governance files are always present:
```yaml
- name: Ensure governance framework
  run: archon-mcp init --stack ${{ env.STACK_PROFILE }}
```

### MCP-Driven Governance from AI Chat
In Cursor or VS Code with Copilot Agent mode:
```
User: Set up governance for this project
AI: [calls init_governance via MCP → deploys all files → confirms success]
```

### Security Audit Kick-Off
```
User: /harden
AI: [reads .github/skills/security.md → performs structured security review]
```

### Feature Completion Check
```
User: /done
AI: [reads .github/skills/done.md → validates feature against checklist]
```

### Architecture Gap Review
```
User: /gap-analysis
AI: [reads .github/prompts/gap-analysis.md → analyzes codebase for missing pieces]
```

---

## 9. Local Installation and CLI Usage

### Prerequisites

- Python 3.10 or higher
- pip

### Install from PyPI (when published)

```bash
pip install archon-mcp
```

### Install from Source (Development)

```bash
# Clone the repository
git clone https://github.com/ShanKonduru/ArchonMCP.git
cd ArchonMCP

# Create and activate a virtual environment (recommended)
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# Install the package in editable mode with dev dependencies
pip install -e ".[dev]"
```

### Verify Installation

```bash
archon-mcp --version
# ArchonMCP, version 0.1.5

archon-mcp --help
```

### CLI Commands

#### `archon-mcp detect`

Scans the current directory and reports the detected tech stack. Does not create any files.

```bash
# Detect stack in current directory
archon-mcp detect

# Detect stack in a specific directory
archon-mcp detect --root /path/to/project
archon-mcp detect -r /path/to/project
```

**Example output:**
```
Detecting technology stack...

Project Root: C:\MyProjects\my-app
Detected Stack: React-FastAPI-Postgres

Indicators found:
  ✓ React/TypeScript frontend (package.json + .tsx files)
  ✓ FastAPI backend (main.py / app.py)
  ✓ PostgreSQL database

To initialize: archon-mcp init --stack "React-FastAPI-Postgres"
```

---

#### `archon-mcp init`

Deploys the full governance structure into the target directory.

```bash
# Auto-detect stack, initialize in current directory
archon-mcp init

# Specify stack explicitly
archon-mcp init --stack React-FastAPI-Postgres
archon-mcp init --stack Generic
archon-mcp init --stack Next.js-Django-Postgres
archon-mcp init --stack Vue-Express-MongoDB
archon-mcp init --stack Angular-SpringBoot-MySQL
archon-mcp init --stack React-Node-MongoDB

# Initialize in a specific directory
archon-mcp init --root /path/to/project
archon-mcp init -r /path/to/project

# Verbose output (lists every file and directory created)
archon-mcp init --verbose
archon-mcp init -v

# Combined
archon-mcp init --root /path/to/project --stack Generic --verbose
```

**Example output (verbose):**
```
==================================================
ArchonMCP Governance Initialization
==================================================

ℹ Using specified stack: React-FastAPI-Postgres
ℹ Creating governance structure...
✓ Governance framework initialized successfully!

--------------------------------------------------
Stack:        React-FastAPI-Postgres
Project Root: C:\MyProjects\my-app
--------------------------------------------------

Created Directories:
  📁 C:\MyProjects\my-app\.github\skills
  📁 C:\MyProjects\my-app\.github\prompts
  📁 C:\MyProjects\my-app\docs\stories
  📁 C:\MyProjects\my-app\docs\adr

Created Files:
  📄 C:\MyProjects\my-app\.github\copilot-instructions.md
  📄 C:\MyProjects\my-app\.github\archon-stack.txt
  📄 C:\MyProjects\my-app\.github\skills\security.md
  ...

Next Steps:
  1. Review the governance files in .github/
  2. Customize templates for your project
  3. Add ADRs to docs/adr/ as decisions are made
  4. Document features in docs/stories/
  5. Reference these governance standards in code reviews
```

---

#### `archon-mcp server`

Starts ArchonMCP as an MCP server over stdio. Used internally when an IDE launches the server process. You can also start it manually to test the connection.

```bash
archon-mcp server
```

---

### Running Tests

```bash
# All tests
.\run_tests.bat        # Windows
./run_tests.sh         # macOS / Linux

# With HTML coverage report
.\run_tests.bat coverage
./run_tests.sh coverage
```

---

## 10. MCP Server Usage in VS Code

### With GitHub Copilot (Agent Mode)

**Requirements:** VS Code 1.99+, GitHub Copilot extension

**Step 1 — Add MCP server configuration**

Open (or create) `.vscode/mcp.json` in your workspace:

```json
{
  "servers": {
    "archon-mcp": {
      "type": "stdio",
      "command": "archon-mcp",
      "args": ["server"]
    }
  }
}
```

If `archon-mcp` is not on your PATH (e.g., installed in a venv), use the full path:

```json
{
  "servers": {
    "archon-mcp": {
      "type": "stdio",
      "command": "C:/MyProjects/ArchonMCP/.venv/Scripts/archon-mcp.exe",
      "args": ["server"]
    }
  }
}
```

**Step 2 — Enable the server**

Open the Copilot Chat panel and switch to **Agent mode** (`@workspace`). The MCP tools panel shows available servers. Click **Start** next to `archon-mcp`.

**Step 3 — Use the tool**

In Copilot Chat (Agent mode):
```
Set up governance for this React + FastAPI project
```
Copilot will call `init_governance` with the detected or specified stack and confirm the files created.

---

### With Cline Extension

**Requirements:** VS Code, Cline extension installed

**Step 1 — Open Cline MCP settings**

Click the Cline icon in the sidebar → click **MCP Servers** → click **Edit MCP Settings**.

**Step 2 — Add server entry**

```json
{
  "mcpServers": {
    "archon-mcp": {
      "command": "archon-mcp",
      "args": ["server"],
      "disabled": false,
      "autoApprove": ["init_governance"]
    }
  }
}
```

**Step 3 — Use in Cline chat**

```
Initialize governance for my project at C:\MyProjects\my-app using the React-FastAPI-Postgres stack
```

---

## 11. MCP Server Usage in Cursor

**Requirements:** Cursor 0.40+ (MCP support is built-in)

**Step 1 — Open MCP configuration**

`Cursor Settings` → `Features` → `MCP` → click **Add New MCP Server**.

Or edit `~/.cursor/mcp.json` (user-level) or `.cursor/mcp.json` (project-level) directly:

```json
{
  "mcpServers": {
    "archon-mcp": {
      "command": "archon-mcp",
      "args": ["server"]
    }
  }
}
```

If using a virtual environment, provide the absolute executable path:

```json
{
  "mcpServers": {
    "archon-mcp": {
      "command": "/home/user/.venv/bin/archon-mcp",
      "args": ["server"]
    }
  }
}
```

**Step 2 — Restart Cursor**

Cursor starts the MCP server process automatically when it launches.

**Step 3 — Use in Composer or Chat**

Open Cursor Composer (`Ctrl+I` / `Cmd+I`) or Chat and ask:
```
Use archon-mcp to initialize governance for this project
```

Cursor will display the tool call, the parameters sent, and the result. The governance files will appear in the file tree immediately.

**Step 4 — Verify**

```
Use archon-mcp to detect the tech stack of my project
```

---

## 12. MCP Server Usage in Other AI IDEs

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "archon-mcp": {
      "command": "archon-mcp",
      "args": ["server"]
    }
  }
}
```

Restart Claude Desktop. The `init_governance` tool appears in the tools panel. Ask Claude:
```
Please initialize governance for my project at /path/to/project
```

---

### Windsurf (Codeium)

Edit `.windsurf/mcp.json` in your project (or the user-level config):

```json
{
  "mcpServers": {
    "archon-mcp": {
      "command": "archon-mcp",
      "args": ["server"],
      "transport": "stdio"
    }
  }
}
```

---

### Continue.dev

In `.continue/config.json`:

```json
{
  "experimental": {
    "modelContextProtocolServers": [
      {
        "transport": {
          "type": "stdio",
          "command": "archon-mcp",
          "args": ["server"]
        }
      }
    ]
  }
}
```

---

### Any MCP-Compatible Client (Generic Config)

ArchonMCP uses the standard stdio MCP transport. Any client that supports `stdio` MCP servers can connect using:

| Property | Value |
|---|---|
| Transport | `stdio` |
| Command | `archon-mcp` (or full path to executable) |
| Args | `["server"]` |
| Tool name | `init_governance` |

---

## 13. Architecture Deep Dive

### Module Overview

```
archon_mcp/
├── __init__.py        Package metadata
├── __main__.py        Entry point (python -m archon_mcp)
├── cli.py             Click-based CLI commands: init, detect, server
├── constants.py       VALID_STACKS list
├── detector.py        Stack detection logic
├── scaffold.py        File/directory creation logic
├── server.py          MCP server: tool registration and stdio transport
└── templates.py       All governance Markdown templates, keyed by stack
```

### Detection Pipeline (`detector.py`)

```
detect_tech_stack(root_path)
  │
  ├─ 1. Check .github/archon-stack.txt  (persisted marker)
  │       → return exact stack if valid
  │
  ├─ 2. Check .github/copilot-instructions.md
  │       → scan content for stack name strings
  │       → return matching stack if found
  │
  └─ 3. Scan root_path for framework files/extensions
          → apply heuristic rules (see constants below)
          → return matched stack or "Generic"
```

Detection heuristic priority order:
1. `Angular-SpringBoot-MySQL` — `angular.json` + `pom.xml`/`build.gradle`
2. `Next.js-Django-Postgres` — `next.config.*` + `manage.py`
3. `Vue-Express-MongoDB` — `package.json` + Vite/Vue config, no Python files
4. `React-FastAPI-Postgres` — `package.json` + `main.py`/`app.py` + React signals
5. `React-Node-MongoDB` — `package.json` + TS/JSX, no Python
6. `Generic` — fallback

### Template Engine (`templates.py`)

All governance content lives in `GOVERNANCE_TEMPLATES`, a nested dictionary:

```python
GOVERNANCE_TEMPLATES = {
    "copilot_instructions": {
        "React-FastAPI-Postgres": "...",
        "Next.js-Django-Postgres": "...",
        ...
        "Generic": "..."
    },
    "security_skill": { ... },
    "migration_skill": { ... },
    "done_skill": { ... },
    "gap_analysis_prompt": { ... },
    "harden_prompt": { ... },
    "done_prompt": { ... },
    "naming_bootstrap": { ... },
}
```

If a stack has no specific entry, the `Generic` template is used as a fallback.

### Scaffold Logic (`scaffold.py`)

`create_governance_structure(root_path, stack)` performs these operations in order:
1. Validate and normalise stack; fall back to Generic if unknown
2. Create four directories with `mkdir(parents=True, exist_ok=True)`
3. Write `copilot-instructions.md`
4. Write three skill files
5. Write three prompt files
6. Write `docs/adr/README.md` and `docs/stories/README.md`
7. Write `naming-bootstrap.md`
8. Write `.github/archon-stack.txt` (stack persistence marker)
9. Return result dict `{stack, created_files, created_dirs, errors}`

All exceptions are caught and appended to `errors`; the function never raises.

### MCP Server (`server.py`)

Built on the `mcp` library (stdio transport). Exposes:

- `list_tools()` — advertises `init_governance` with full JSON Schema for its inputs
- `call_tool()` / `init_governance()` — resolves path, detects/validates stack, calls scaffold, returns structured text result

The server runs as an async event loop via `asyncio.run(run_mcp_server())`, started by `archon-mcp server`.

---

## 14. Project Structure

```
ArchonMCP/
├── archon_mcp/             Source package
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── constants.py
│   ├── detector.py
│   ├── scaffold.py
│   ├── server.py
│   └── templates.py
├── tests/                  Test suite (pytest)
│   ├── test_archon_mcp.py
│   ├── test_cli.py
│   ├── test_constants.py
│   ├── test_detector.py
│   ├── test_scaffold.py
│   ├── test_server.py
│   └── test_templates.py
├── docs/
│   ├── adr/                Architecture Decision Records
│   ├── stories/            Feature stories
│   └── TECHNICAL_GUIDE.md  This document
├── .github/
│   ├── copilot-instructions.md
│   ├── skills/
│   └── prompts/
├── pyproject.toml          Package metadata and build config
├── run_tests.bat / .sh     Test runner scripts
├── run_audit.bat / .sh     Security audit scripts
├── deploy.bat / .sh        Deployment helpers
└── README.md               Project overview
```

---

## 15. Troubleshooting

### `archon-mcp: command not found`

The package is not on your PATH. Either:
- Activate the virtual environment where it is installed: `.venv\Scripts\activate`
- Use the full path in your MCP config: `C:/path/to/.venv/Scripts/archon-mcp.exe`

### `detect` returns `Generic` after `init`

This was a bug fixed in v0.1.5. After `init`, the stack is persisted to `.github/archon-stack.txt`. If you ran `init` on an older version:
```bash
archon-mcp init --stack <YourStack>   # re-run to write the marker
archon-mcp detect                     # should now return the correct stack
```

### MCP server not appearing in IDE

1. Confirm `archon-mcp server` starts without error from a terminal
2. Check the IDE MCP log for connection errors
3. Use the absolute path to the executable in your MCP config
4. On Windows, use forward slashes or escaped backslashes in JSON paths

### Permission errors on Linux / macOS

Ensure the executable bit is set:
```bash
chmod +x $(which archon-mcp)
```

### Tests fail with `No module named pytest`

Install dev dependencies:
```bash
pip install -e ".[dev]"
```

---

*Generated by ArchonMCP project documentation tooling — v0.1.5*
