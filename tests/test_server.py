"""Tests for archon_mcp.server (MCP tool handlers)."""

import asyncio
from unittest.mock import patch

import pytest

from archon_mcp.constants import VALID_STACKS
from archon_mcp.server import init_governance, list_tools


# ── list_tools ────────────────────────────────────────────────────────────────

def test_list_tools_returns_one_tool():
    tools = asyncio.run(list_tools())
    assert len(tools) == 1


def test_list_tools_tool_name():
    tools = asyncio.run(list_tools())
    assert tools[0].name == "init_governance"


def test_list_tools_stack_enum_matches_valid_stacks():
    tools = asyncio.run(list_tools())
    schema = tools[0].inputSchema
    assert schema["properties"]["stack"]["enum"] == VALID_STACKS


def test_list_tools_has_root_directory_property():
    tools = asyncio.run(list_tools())
    assert "root_directory" in tools[0].inputSchema["properties"]


# ── init_governance error cases ───────────────────────────────────────────────

def test_missing_root_returns_error():
    result = asyncio.run(init_governance(root_directory="Z:/definitely-does-not-exist-12345"))
    assert result.isError is True


def test_missing_root_error_message_mentions_path():
    result = asyncio.run(init_governance(root_directory="Z:/definitely-does-not-exist-12345"))
    combined = " ".join(c.text for c in result.content)
    assert "does not exist" in combined


def test_invalid_stack_returns_error(tmp_path):
    result = asyncio.run(
        init_governance(root_directory=str(tmp_path), stack="FakeStack-X")
    )
    assert result.isError is True
    combined = " ".join(c.text for c in result.content)
    assert "Invalid stack" in combined or "FakeStack-X" in combined


# ── init_governance success cases ─────────────────────────────────────────────

def test_success_with_valid_stack(tmp_path):
    result = asyncio.run(
        init_governance(root_directory=str(tmp_path), stack="Generic")
    )
    assert result.isError is False


def test_success_output_mentions_stack(tmp_path):
    result = asyncio.run(
        init_governance(root_directory=str(tmp_path), stack="Generic")
    )
    combined = " ".join(c.text for c in result.content)
    assert "Generic" in combined


def test_success_auto_detect_stack(tmp_path):
    """No stack argument → auto-detection → no error."""
    result = asyncio.run(init_governance(root_directory=str(tmp_path)))
    assert result.isError is False


@pytest.mark.parametrize("stack", VALID_STACKS)
def test_all_stacks_initialise_without_error(tmp_path, stack):
    result = asyncio.run(
        init_governance(root_directory=str(tmp_path), stack=stack)
    )
    assert result.isError is False, f"Unexpected error for stack={stack}"


# ── no root_directory (else branch → Path.cwd()) ──────────────────────────────

def test_no_root_directory_defaults_to_cwd():
    """Passing root_directory=None hits the else branch using Path.cwd()."""
    result = asyncio.run(init_governance(root_directory=None, stack="Generic"))
    assert result.isError is False


# ── scaffold errors propagated ────────────────────────────────────────────────

def test_init_governance_propagates_scaffold_errors(tmp_path):
    """When create_governance_structure returns errors, isError is True."""
    error_result = {
        "stack": "Generic",
        "created_files": [],
        "created_dirs": [],
        "errors": ["disk full"],
    }
    with patch("archon_mcp.server.create_governance_structure", return_value=error_result):
        result = asyncio.run(
            init_governance(root_directory=str(tmp_path), stack="Generic")
        )
    assert result.isError is True
    combined = " ".join(c.text for c in result.content)
    assert "disk full" in combined


# ── unexpected exception ──────────────────────────────────────────────────────

def test_init_governance_handles_unexpected_exception(tmp_path):
    """Unhandled exception inside init_governance is caught and returned as error."""
    with patch(
        "archon_mcp.server.create_governance_structure",
        side_effect=RuntimeError("unexpected boom"),
    ):
        result = asyncio.run(
            init_governance(root_directory=str(tmp_path), stack="Generic")
        )
    assert result.isError is True
    combined = " ".join(c.text for c in result.content)
    assert "unexpected boom" in combined
