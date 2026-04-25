"""Tests for archon_mcp.constants."""

from archon_mcp.constants import VALID_STACKS


def test_valid_stacks_is_list():
    assert isinstance(VALID_STACKS, list)


def test_valid_stacks_contains_generic():
    assert "Generic" in VALID_STACKS


def test_valid_stacks_contains_all_named_stacks():
    named = {
        "React-FastAPI-Postgres",
        "Next.js-Django-Postgres",
        "Vue-Express-MongoDB",
        "Angular-SpringBoot-MySQL",
        "React-Node-MongoDB",
    }
    assert named.issubset(set(VALID_STACKS))


def test_valid_stacks_has_no_duplicates():
    assert len(VALID_STACKS) == len(set(VALID_STACKS))
