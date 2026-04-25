# Role: ArchonMCP Lead Developer
Build a Python-based MCP server using the `fastmcp` library named "ArchonMCP".

## Core Functionality:
Implement a tool named `init_governance` that:
1. **Detects Environment:** Scans the current working directory for existing files to guess the tech stack.
2. **Deploys Framework:** Writes the following to the project root:
    - `.github/copilot-instructions.md` (High-governance rules).
    - `.github/skills/` (Security, Migration, and Done runbooks).
    - `.github/prompts/` (Gap-analysis, Harden, and Done slash commands).
    - `/docs/stories/` and `/docs/adr/` (Folder structures).
3. **Stack Support:** Must support 'React-FastAPI-Postgres' as the primary profile, but allow for 'Generic' as a fallback.

## Technical Specifications:
- Use `pathlib` for all file operations to ensure cross-IDE/OS compatibility.
- Use a dictionary-based "template engine" inside the code to store the Markdown content for each file.
- The server must run over `stdio` to be compatible with all MCP-enabled IDEs (Cursor, VS Code, Claude).

## Output:
Provide the `archon_mcp.py` file and the `pyproject.toml` required to run it.