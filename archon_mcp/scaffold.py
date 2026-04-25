"""Governance directory and file creation."""

from pathlib import Path

from archon_mcp.constants import VALID_STACKS
from archon_mcp.templates import GOVERNANCE_TEMPLATES


def create_governance_structure(root_path: Path, stack: str) -> dict:
    """
    Create the governance structure with all necessary files and directories.
    
    Args:
        root_path: The root directory for the project
        stack: The detected or specified stack
        
    Returns:
        Dictionary with creation results
    """
    results = {
        "stack": stack,
        "created_files": [],
        "created_dirs": [],
        "errors": [],
    }
    
    # Ensure stack is valid
    if stack not in VALID_STACKS:
        stack = "Generic"
        results["stack"] = stack
    
    try:
        # Create directory structure
        dirs_to_create = [
            root_path / ".github" / "skills",
            root_path / ".github" / "prompts",
            root_path / "docs" / "stories",
            root_path / "docs" / "adr",
        ]
        
        for dir_path in dirs_to_create:
            dir_path.mkdir(parents=True, exist_ok=True)
            results["created_dirs"].append(str(dir_path))
        
        # Create copilot-instructions.md
        instructions_path = root_path / ".github" / "copilot-instructions.md"
        content = GOVERNANCE_TEMPLATES["copilot_instructions"].get(
            stack, GOVERNANCE_TEMPLATES["copilot_instructions"]["Generic"]
        )
        instructions_path.write_text(content, encoding="utf-8")
        results["created_files"].append(str(instructions_path))
        
        # Create skill files
        skills = {
            "security.md": "security_skill",
            "migration.md": "migration_skill",
            "done.md": "done_skill",
        }
        
        for filename, template_key in skills.items():
            skill_path = root_path / ".github" / "skills" / filename
            content = GOVERNANCE_TEMPLATES[template_key].get(
                stack, GOVERNANCE_TEMPLATES[template_key]["Generic"]
            )
            skill_path.write_text(content, encoding="utf-8")
            results["created_files"].append(str(skill_path))
        
        # Create prompt files
        prompts = {
            "gap-analysis.md": "gap_analysis_prompt",
            "harden.md": "harden_prompt",
            "done.md": "done_prompt",
        }
        
        for filename, template_key in prompts.items():
            prompt_path = root_path / ".github" / "prompts" / filename
            content = GOVERNANCE_TEMPLATES[template_key].get(
                stack, GOVERNANCE_TEMPLATES[template_key]["Generic"]
            )
            prompt_path.write_text(content, encoding="utf-8")
            results["created_files"].append(str(prompt_path))
        
        # Create placeholder ADR and stories files
        adr_template = """# Architecture Decision Record

## Context
Describe the context or problem that led to this decision.

## Decision
Describe the decision made.

## Consequences
Describe the consequences of this decision (positive and negative).

## Alternatives Considered
- Alternative 1: Description
- Alternative 2: Description
"""
        
        adr_index = root_path / "docs" / "adr" / "README.md"
        adr_index.write_text(
            "# Architecture Decision Records\n\n"
            "This directory contains all architecture decisions made for this project.\n"
            "Each decision is documented in a separate Markdown file.\n",
            encoding="utf-8"
        )
        results["created_files"].append(str(adr_index))
        
        stories_index = root_path / "docs" / "stories" / "README.md"
        stories_index.write_text(
            "# Feature Stories\n\n"
            "This directory contains feature stories and acceptance criteria.\n"
            "Use this to document requirements and expected behavior.\n",
            encoding="utf-8"
        )
        results["created_files"].append(str(stories_index))

        # Create naming bootstrap file
        bootstrap_path = root_path / ".github" / "naming-bootstrap.md"
        bootstrap_content = GOVERNANCE_TEMPLATES["naming_bootstrap"].get(
            stack, GOVERNANCE_TEMPLATES["naming_bootstrap"]["Generic"]
        )
        bootstrap_path.write_text(bootstrap_content, encoding="utf-8")
        results["created_files"].append(str(bootstrap_path))

    except Exception as e:
        results["errors"].append(f"Error creating governance structure: {str(e)}")
    
    return results


# Create the MCP server
