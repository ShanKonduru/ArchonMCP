"""ArchonMCP package – re-exports for backward compatibility."""

from archon_mcp.constants import VALID_STACKS
from archon_mcp.templates import GOVERNANCE_TEMPLATES
from archon_mcp.detector import detect_tech_stack
from archon_mcp.scaffold import create_governance_structure
from archon_mcp.server import init_governance, list_tools, run_mcp_server
from archon_mcp.cli import cli

__all__ = [
    "VALID_STACKS",
    "GOVERNANCE_TEMPLATES",
    "detect_tech_stack",
    "create_governance_structure",
    "init_governance",
    "list_tools",
    "run_mcp_server",
    "cli",
]
