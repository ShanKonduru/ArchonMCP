"""Tests for archon_mcp.scaffold."""

from pathlib import Path

import pytest

from archon_mcp.constants import VALID_STACKS
from archon_mcp.scaffold import create_governance_structure


# ── expected artefact paths ───────────────────────────────────────────────────

EXPECTED_FILES = [
    Path(".github") / "copilot-instructions.md",
    Path(".github") / "archon-stack.txt",
    Path(".github") / "skills" / "security.md",
    Path(".github") / "skills" / "migration.md",
    Path(".github") / "skills" / "done.md",
    Path(".github") / "prompts" / "gap-analysis.md",
    Path(".github") / "prompts" / "harden.md",
    Path(".github") / "prompts" / "done.md",
    Path("docs") / "adr" / "README.md",
    Path("docs") / "stories" / "README.md",
    Path(".github") / "naming-bootstrap.md",
]

EXPECTED_DIRS = [
    Path(".github") / "skills",
    Path(".github") / "prompts",
    Path("docs") / "stories",
    Path("docs") / "adr",
]


@pytest.mark.parametrize("stack", VALID_STACKS)
def test_all_files_created_for_every_stack(tmp_path, stack):
    result = create_governance_structure(tmp_path, stack)
    assert result["errors"] == []
    assert result["stack"] == stack
    for rel in EXPECTED_FILES:
        assert (tmp_path / rel).exists(), f"Missing {rel} for stack={stack}"


@pytest.mark.parametrize("stack", VALID_STACKS)
def test_all_dirs_created_for_every_stack(tmp_path, stack):
    result = create_governance_structure(tmp_path, stack)
    for rel in EXPECTED_DIRS:
        assert (tmp_path / rel).is_dir(), f"Missing dir {rel} for stack={stack}"


def test_invalid_stack_falls_back_to_generic(tmp_path):
    result = create_governance_structure(tmp_path, "Unknown-Stack-XYZ")
    assert result["errors"] == []
    assert result["stack"] == "Generic"


def test_result_dict_shape(tmp_path):
    result = create_governance_structure(tmp_path, "Generic")
    assert "stack" in result
    assert "created_files" in result
    assert "created_dirs" in result
    assert "errors" in result
    assert isinstance(result["created_files"], list)
    assert isinstance(result["created_dirs"], list)


def test_files_list_matches_actual_created_count(tmp_path):
    result = create_governance_structure(tmp_path, "Generic")
    assert len(result["created_files"]) == len(EXPECTED_FILES)


def test_copilot_instructions_has_content(tmp_path):
    create_governance_structure(tmp_path, "React-FastAPI-Postgres")
    content = (tmp_path / ".github" / "copilot-instructions.md").read_text(encoding="utf-8")
    assert "React-FastAPI-Postgres" in content or "ArchonMCP" in content


def test_idempotent_second_call_does_not_error(tmp_path):
    """Running scaffold twice on the same directory should not produce errors."""
    r1 = create_governance_structure(tmp_path, "Generic")
    r2 = create_governance_structure(tmp_path, "Generic")
    assert r1["errors"] == []
    assert r2["errors"] == []


def test_scaffold_captures_write_errors(tmp_path, monkeypatch):
    """Exception during file writing is caught and reported in errors list."""
    from pathlib import Path as _Path

    def _raise_on_write(self, content, *args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(_Path, "write_text", _raise_on_write)
    result = create_governance_structure(tmp_path, "Generic")
    assert len(result["errors"]) > 0
    assert any("Error creating governance structure" in e for e in result["errors"])
