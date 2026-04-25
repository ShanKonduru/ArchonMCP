"""Tests for archon_mcp.cli (Click commands)."""

from pathlib import Path
from unittest.mock import patch, AsyncMock

import pytest
from click.testing import CliRunner

from archon_mcp.cli import cli
from archon_mcp.constants import VALID_STACKS


@pytest.fixture()
def runner():
    return CliRunner()


# ── archon-mcp detect ────────────────────────────────────────────────────────

def test_detect_shows_stack(runner, tmp_path):
    result = runner.invoke(cli, ["detect", "--root", str(tmp_path)])
    assert result.exit_code == 0
    assert "Generic" in result.output or any(s in result.output for s in VALID_STACKS)


def test_detect_nextjs_project(runner, tmp_path):
    (tmp_path / "next.config.js").write_text("module.exports = {}", encoding="utf-8")
    (tmp_path / "manage.py").write_text("", encoding="utf-8")
    result = runner.invoke(cli, ["detect", "--root", str(tmp_path)])
    assert result.exit_code == 0
    assert "Next.js-Django-Postgres" in result.output


# ── archon-mcp init ──────────────────────────────────────────────────────────

def test_init_default_stack_auto_detect(runner, tmp_path):
    result = runner.invoke(cli, ["init", "--root", str(tmp_path)])
    assert result.exit_code == 0
    assert "successfully" in result.output.lower() or "initialized" in result.output.lower()


def test_init_explicit_stack(runner, tmp_path):
    result = runner.invoke(cli, ["init", "--root", str(tmp_path), "--stack", "Generic"])
    assert result.exit_code == 0


def test_init_verbose_lists_files(runner, tmp_path):
    result = runner.invoke(
        cli, ["init", "--root", str(tmp_path), "--stack", "Generic", "--verbose"]
    )
    assert result.exit_code == 0
    assert "copilot-instructions.md" in result.output


def test_init_creates_github_dir(runner, tmp_path):
    runner.invoke(cli, ["init", "--root", str(tmp_path), "--stack", "Generic"])
    assert (tmp_path / ".github").is_dir()


def test_init_case_insensitive_stack(runner, tmp_path):
    result = runner.invoke(cli, ["init", "--root", str(tmp_path), "--stack", "generic"])
    assert result.exit_code == 0


# ── --version flag ────────────────────────────────────────────────────────────

def test_version_flag(runner):
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


# ── --help flag ───────────────────────────────────────────────────────────────

def test_help_lists_commands(runner):
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "init" in result.output
    assert "detect" in result.output
    assert "server" in result.output


# ── init: scaffold errors path (covers print_warning + print_error) ───────────

def test_init_shows_warning_when_scaffold_returns_errors(runner, tmp_path):
    error_result = {
        "stack": "Generic",
        "created_files": [],
        "created_dirs": [],
        "errors": ["simulated scaffold error"],
    }
    with patch("archon_mcp.cli.create_governance_structure", return_value=error_result):
        result = runner.invoke(
            cli, ["init", "--root", str(tmp_path), "--stack", "Generic"]
        )
    assert "simulated scaffold error" in result.output
    assert "Governance initialized with errors" in result.output


# ── init: unexpected exception path (covers lines 131-133) ───────────────────

def test_init_unexpected_exception_exits_nonzero(runner, tmp_path):
    with patch(
        "archon_mcp.cli.create_governance_structure",
        side_effect=RuntimeError("kaboom"),
    ):
        result = runner.invoke(
            cli, ["init", "--root", str(tmp_path), "--stack", "Generic"]
        )
    assert result.exit_code != 0
    assert "Failed to initialize governance" in result.output


# ── server command ────────────────────────────────────────────────────────────

def test_server_command_normal_exit(runner):
    """server command runs and exits cleanly when run_mcp_server completes."""
    with patch("archon_mcp.cli.run_mcp_server", new_callable=AsyncMock):
        result = runner.invoke(cli, ["server"])
    assert result.exit_code == 0
    assert "Starting ArchonMCP MCP Server" in result.output


def test_server_command_exception_exits_nonzero(runner):
    """server command handles generic exceptions and exits nonzero."""
    with patch("archon_mcp.cli.run_mcp_server", new_callable=AsyncMock) as mock_srv:
        mock_srv.side_effect = RuntimeError("server crash")
        result = runner.invoke(cli, ["server"])
    assert result.exit_code != 0
    assert "Server error" in result.output or "server crash" in result.output.lower()


def test_server_command_keyboard_interrupt_exits_zero(runner):
    """server command catches KeyboardInterrupt and exits cleanly."""
    with patch("archon_mcp.cli.run_mcp_server", new_callable=AsyncMock) as mock_srv:
        mock_srv.side_effect = KeyboardInterrupt()
        result = runner.invoke(cli, ["server"])
    assert result.exit_code == 0
    assert "Shutting down" in result.output


# ── detect: unexpected exception path (covers lines 208-210) ─────────────────

def test_detect_unexpected_exception_exits_nonzero(runner, tmp_path):
    with patch(
        "archon_mcp.cli.detect_tech_stack",
        side_effect=RuntimeError("scan failed"),
    ):
        result = runner.invoke(cli, ["detect", "--root", str(tmp_path)])
    assert result.exit_code != 0
    assert "Detection failed" in result.output


# ── __main__ entry point ──────────────────────────────────────────────────────

def test_main_module_exposes_cli():
    """Importing archon_mcp.__main__ executes cleanly and exposes the cli callable."""
    import archon_mcp.__main__ as main_mod
    assert callable(main_mod.cli)
