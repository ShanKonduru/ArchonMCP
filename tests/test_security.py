"""Security tests: path containment and safe-write behavior."""

from pathlib import Path

import pytest

from archon_mcp.pathsafe import PathContainmentError, resolve_within
from archon_mcp.scaffold import create_governance_structure

# ── path containment (E9.F1.S2 / E10.F5) ─────────────────────────────────────

def test_resolve_within_allows_child(tmp_path):
    target = resolve_within(tmp_path, Path(".github/copilot-instructions.md"))
    assert str(target).startswith(str(tmp_path.resolve()))


def test_resolve_within_rejects_parent_traversal(tmp_path):
    with pytest.raises(PathContainmentError):
        resolve_within(tmp_path, Path("../escape.txt"))


def test_resolve_within_rejects_absolute_outside(tmp_path, tmp_path_factory):
    outside = tmp_path_factory.mktemp("outside") / "evil.txt"
    with pytest.raises(PathContainmentError):
        resolve_within(tmp_path, outside)


def test_resolve_within_rejects_symlink_escape(tmp_path, tmp_path_factory):
    outside = tmp_path_factory.mktemp("outside")
    link = tmp_path / "link"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks not supported in this environment")
    with pytest.raises(PathContainmentError):
        resolve_within(tmp_path, Path("link/evil.txt"))


def test_scaffold_never_writes_outside_root(tmp_path):
    """Every created path must live inside the project root."""
    root = tmp_path.resolve()
    result = create_governance_structure(root, "Generic")
    for p in result["created_files"] + result["created_dirs"]:
        rp = Path(p).resolve()
        assert rp == root or root in rp.parents, f"{rp} escaped {root}"


# ── safe writes: no silent overwrite (E9.F1.S1) ───────────────────────────────

def test_existing_file_preserved_by_default(tmp_path):
    existing = tmp_path / ".github" / "copilot-instructions.md"
    existing.parent.mkdir(parents=True, exist_ok=True)
    existing.write_text("MY HAND-WRITTEN RULES", encoding="utf-8")

    result = create_governance_structure(tmp_path, "Generic")

    assert str(existing.resolve()) in result["skipped"]
    assert existing.read_text(encoding="utf-8") == "MY HAND-WRITTEN RULES"


def test_force_overwrites_existing_file(tmp_path):
    existing = tmp_path / ".github" / "copilot-instructions.md"
    existing.parent.mkdir(parents=True, exist_ok=True)
    existing.write_text("MY HAND-WRITTEN RULES", encoding="utf-8")

    result = create_governance_structure(tmp_path, "Generic", force=True)

    assert result["skipped"] == []
    assert existing.read_text(encoding="utf-8") != "MY HAND-WRITTEN RULES"


# ── dry-run writes nothing (E10.F4.S2) ────────────────────────────────────────

def test_dry_run_writes_no_files(tmp_path):
    result = create_governance_structure(tmp_path, "Generic", dry_run=True)

    assert result["dry_run"] is True
    assert result["created_files"], "dry-run should still report a plan"
    # Nothing should actually exist on disk.
    assert not (tmp_path / ".github").exists()
    assert not (tmp_path / "docs").exists()


def test_dry_run_does_not_overwrite(tmp_path):
    existing = tmp_path / ".github" / "copilot-instructions.md"
    existing.parent.mkdir(parents=True, exist_ok=True)
    existing.write_text("KEEP ME", encoding="utf-8")

    create_governance_structure(tmp_path, "Generic", dry_run=True, force=True)

    assert existing.read_text(encoding="utf-8") == "KEEP ME"
