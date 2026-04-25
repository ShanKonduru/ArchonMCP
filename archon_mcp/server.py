"""MCP server: tool registration and stdio transport."""

from pathlib import Path
from typing import Optional

import mcp.server.stdio
from mcp.server import Server
from mcp.types import CallToolResult, Tool, TextContent

from archon_mcp.constants import VALID_STACKS
from archon_mcp.detector import detect_tech_stack
from archon_mcp.scaffold import create_governance_structure


server = Server("archon-mcp")


@server.call_tool()
async def init_governance(
    root_directory: Optional[str] = None,
    stack: Optional[str] = None,
) -> CallToolResult:
    """
    Initialize governance framework for a project.
    
    This tool:
    1. Detects or validates the tech stack
    2. Creates governance directory structure
    3. Deploys governance templates
    
    Args:
        root_directory: Project root directory (defaults to current directory)
        stack: Tech stack to use ('React-FastAPI-Postgres' or 'Generic', auto-detected if not specified)
        
    Returns:
        CallToolResult with creation status and details
    """
    try:
        # Determine root directory
        if root_directory:
            root_path = Path(root_directory).resolve()
        else:
            root_path = Path.cwd()
        
        # Validate root directory exists
        if not root_path.is_dir():
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Error: Root directory does not exist: {root_path}",
                    )
                ],
                isError=True,
            )
        
        # Detect or validate stack
        if stack is None:
            detected_stack = detect_tech_stack(root_path)
            stack = detected_stack
        elif stack not in VALID_STACKS:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Invalid stack specified: '{stack}'. "
                        f"Valid options: {', '.join(VALID_STACKS)}",
                    )
                ],
                isError=True,
            )
        
        # Create governance structure
        results = create_governance_structure(root_path, stack)
        
        # Format output
        if results["errors"]:
            error_text = "\n".join(results["errors"])
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Governance initialization completed with errors:\n\n{error_text}",
                    )
                ],
                isError=True,
            )
        
        # Success message
        output = f"""✓ Governance framework initialized successfully!

Stack Detected: {results['stack']}
Project Root: {root_path}

Created Directories:
{chr(10).join(f"  • {d}" for d in results['created_dirs'])}

Created Files:
{chr(10).join(f"  • {f}" for f in results['created_files'])}

Next Steps:
1. Review the governance files in .github/
2. Customize templates for your project
3. Add ADRs to docs/adr/ as decisions are made
4. Document features in docs/stories/
5. Reference these governance standards in code reviews
"""
        
        return CallToolResult(
            content=[TextContent(type="text", text=output)],
            isError=False,
        )
        
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")],
            isError=True,
        )


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="init_governance",
            description="Initialize governance framework for a project. Detects tech stack and deploys governance templates including rules, skills, and prompts.",
            inputSchema={
                "type": "object",
                "properties": {
                    "root_directory": {
                        "type": "string",
                        "description": "Project root directory (defaults to current working directory). Use absolute paths for best compatibility.",
                    },
                    "stack": {
                        "type": "string",
                        "enum": VALID_STACKS,
                        "description": (
                            "Technology stack to use. Auto-detected if not specified. "
                            f"Options: {', '.join(VALID_STACKS)}"
                        ),
                    },
                },
            },
        )
    ]


async def run_mcp_server():  # pragma: no cover
    """Run the MCP server over stdio."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            mcp.server.stdio.ServerParameters(),
        )


