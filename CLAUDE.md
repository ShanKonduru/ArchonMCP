# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

ArchonMCP is a Python package that deploys a **governance framework** (rules, runbooks, slash-command prompts, ADR/story scaffolding) into any target project. It ships as both a Click CLI (`archon-mcp`) and an MCP server over stdio. The value is entirely in the generated Markdown — the code is a small detection + templating + file-writing pipeline around a large template dictionary.

## Common commands

```bash
# Install editable with dev tools
pip install -e ".[dev]"

# Tests
./run_tests.sh                              # all tests
./run_tests.sh coverage                     # + HTML coverage in htmlcov/
python -m pytest tests/test_detector.py     # single file
python -m pytest tests/test_detector.py::test_generic_empty_dir   # single test

# Lint / format / type-check (config in pyproject.toml; line-length 100)
ruff check archon_mcp tests
black archon_mcp tests
mypy archon_mcp

# Dependency security audit (needs project-local .venv with audit tools)
./project_venv.sh setup     # create .venv + install pip-audit tooling
./run_audit.sh              # pip-audit -> project-audit.json + security_project.html

# Exercise the tool itself
archon-mcp detect [--root DIR]
archon-mcp init [--root DIR] [--stack STACK] [--verbose]
archon-mcp server           # run as MCP server over stdio
```

`pytest` runs in `asyncio_mode = "auto"` with `--strict-markers` (see `[tool.pytest.ini_options]`). On Windows, the `.sh` scripts have `.bat` equivalents (`run_tests.bat`, `run_audit.bat`, `project_venv.bat`, `deploy.bat`).

## Architecture

The request flow is identical for both entry points — CLI and MCP server are thin adapters over the same three modules:

```
cli.py / server.py   →   detector.detect_tech_stack()   →   scaffold.create_governance_structure()   →   templates.GOVERNANCE_TEMPLATES
   (adapters)              (pick a stack profile)             (make dirs, write files, collect results)      (the actual content)
```

- **`constants.py`** — `VALID_STACKS`, the single source of truth for supported stack profiles (`React-FastAPI-Postgres`, `Next.js-Django-Postgres`, `Vue-Express-MongoDB`, `Angular-SpringBoot-MySQL`, `React-Node-MongoDB`, `Generic`). Every other module keys off this list.
- **`detector.py`** — `detect_tech_stack(root)` returns one `VALID_STACKS` value. It **first** checks for Archon's own markers (`.github/archon-stack.txt`, then stack names inside `.github/copilot-instructions.md`) so a re-run on an already-initialized project recovers the original stack; only then does it sniff signal files (package.json, tsconfig, next.config.*, angular.json, manage.py, pom.xml, etc.). Order of the sniffing checks matters — more specific stacks are tested before more generic ones. Falls back to `Generic` and never raises (swallows `PermissionError`/`OSError`).
- **`scaffold.py`** — `create_governance_structure(root, stack)` creates the directory tree and writes every file, returning a result dict `{stack, created_files, created_dirs, errors}`. It writes `.github/archon-stack.txt` as the marker the detector reads back. Template lookups fall back to the `"Generic"` entry when a stack has no specific content: `GOVERNANCE_TEMPLATES[key].get(stack, GOVERNANCE_TEMPLATES[key]["Generic"])`.
- **`templates.py`** — `GOVERNANCE_TEMPLATES`, a nested dict `{template_key: {stack: markdown_string}}`. ~53KB and by far the largest file. This is where governance content lives; editing what a governed project receives means editing here, not the pipeline.
- **`server.py`** — registers the `init_governance` MCP tool and `list_tools`, runs over stdio. Returns `CallToolResult` with `isError` set; errors are returned as content, not raised.
- **`cli.py`** — `init` / `detect` / `server` sub-commands with colorized output.
- **`__init__.py`** re-exports the public API; **`__main__.py`** enables `python -m archon_mcp`.

## Working in this repo

- **Adding a stack profile:** add it to `VALID_STACKS`, add detection logic in `detector.py` (place the check before broader profiles), and add template entries under each key in `templates.py` (or rely on the `Generic` fallback). Add detector tests mirroring the pattern in `tests/test_detector.py` (the `_touch` helper + `tmp_path`).
- **Changing generated governance content:** edit `templates.py` only. The set of files written and their locations is fixed in `scaffold.py` (`.github/copilot-instructions.md`, `.github/skills/{security,migration,done}.md`, `.github/prompts/{gap-analysis,harden,done}.md`, `.github/naming-bootstrap.md`, plus `docs/adr/README.md` and `docs/stories/README.md`).
- The scaffolder generates `.github/archon-stack.txt`; that path is gitignored so the marker doesn't leak into this repo when self-testing.
- `deploy.sh` / `deploy.bat` are interactive build/publish menus (build, TestPyPI, PyPI) — not needed for normal development.

## Known inconsistencies to be aware of

- `cli.py` hard-codes `version="0.1.0"` in `@click.version_option`, while `pyproject.toml` is at `0.1.5` — the CLI `--version` output is stale.
- Docstrings in `server.py` still describe only `React-FastAPI-Postgres`/`Generic`, predating the expanded `VALID_STACKS`. Trust `constants.py`.
