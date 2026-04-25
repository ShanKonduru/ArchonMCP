"""Tests for archon_mcp.templates."""

import pytest
from archon_mcp.constants import VALID_STACKS
from archon_mcp.templates import GOVERNANCE_TEMPLATES

EXPECTED_KEYS = {
    "copilot_instructions",
    "security_skill",
    "migration_skill",
    "done_skill",
    "gap_analysis_prompt",
    "harden_prompt",
    "done_prompt",
    "naming_bootstrap",
}


def test_governance_templates_has_all_keys():
    assert set(GOVERNANCE_TEMPLATES.keys()) == EXPECTED_KEYS


@pytest.mark.parametrize("artifact", EXPECTED_KEYS)
def test_each_artifact_covers_all_stacks(artifact):
    """Every template artifact must have an entry for every valid stack."""
    missing = [s for s in VALID_STACKS if s not in GOVERNANCE_TEMPLATES[artifact]]
    assert not missing, f"artifact '{artifact}' missing stacks: {missing}"


@pytest.mark.parametrize("artifact", EXPECTED_KEYS)
def test_each_artifact_content_is_non_empty_string(artifact):
    for stack in VALID_STACKS:
        content = GOVERNANCE_TEMPLATES[artifact][stack]
        assert isinstance(content, str), f"{artifact}[{stack}] is not a string"
        assert len(content.strip()) > 0, f"{artifact}[{stack}] is empty"
