"""Governance directory and file creation."""

from pathlib import Path

from archon_mcp.constants import VALID_STACKS
from archon_mcp.pathsafe import PathContainmentError, resolve_within
from archon_mcp.templates import GOVERNANCE_TEMPLATES


def create_governance_structure(
    root_path: Path,
    stack: str,
    force: bool = False,
    dry_run: bool = False,
) -> dict:
    """
    Create the governance structure with all necessary files and directories.

    Args:
        root_path: The root directory for the project.
        stack: The detected or specified stack.
        force: Overwrite existing files. When False (default), existing files
            are left untouched and reported under ``skipped`` — ArchonMCP never
            silently destroys a hand-written governance file.
        dry_run: Plan only. Compute what would be created/overwritten/skipped
            without writing anything to disk.

    Returns:
        Dictionary with creation results, including ``skipped`` (files that
        already existed and were preserved) and ``dry_run`` (echo of the flag).
    """
    results = {
        "stack": stack,
        "created_files": [],
        "created_dirs": [],
        "skipped": [],
        "errors": [],
        "dry_run": dry_run,
    }

    # Ensure stack is valid
    if stack not in VALID_STACKS:
        stack = "Generic"
        results["stack"] = stack

    root_path = Path(root_path).resolve()

    def _write(relative_path: str, content: str) -> None:
        """Write one governance file, honoring containment/force/dry-run."""
        try:
            target = resolve_within(root_path, Path(relative_path))
        except PathContainmentError as exc:
            results["errors"].append(str(exc))
            return

        if target.exists() and not force:
            results["skipped"].append(str(target))
            return

        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        results["created_files"].append(str(target))

    def _mkdir(relative_path: str) -> None:
        try:
            target = resolve_within(root_path, Path(relative_path))
        except PathContainmentError as exc:
            results["errors"].append(str(exc))
            return
        if not dry_run:
            target.mkdir(parents=True, exist_ok=True)
        results["created_dirs"].append(str(target))

    try:
        # Create directory structure
        for rel_dir in (
            ".github/skills",
            ".github/prompts",
            "docs/stories",
            "docs/adr",
        ):
            _mkdir(rel_dir)

        # copilot-instructions.md
        content = GOVERNANCE_TEMPLATES["copilot_instructions"].get(
            stack, GOVERNANCE_TEMPLATES["copilot_instructions"]["Generic"]
        )
        _write(".github/copilot-instructions.md", content)

        # Skill files
        skills = {
            "security.md": "security_skill",
            "migration.md": "migration_skill",
            "done.md": "done_skill",
        }
        for filename, template_key in skills.items():
            content = GOVERNANCE_TEMPLATES[template_key].get(
                stack, GOVERNANCE_TEMPLATES[template_key]["Generic"]
            )
            _write(f".github/skills/{filename}", content)

        # Prompt files
        prompts = {
            "gap-analysis.md": "gap_analysis_prompt",
            "harden.md": "harden_prompt",
            "done.md": "done_prompt",
        }
        for filename, template_key in prompts.items():
            content = GOVERNANCE_TEMPLATES[template_key].get(
                stack, GOVERNANCE_TEMPLATES[template_key]["Generic"]
            )
            _write(f".github/prompts/{filename}", content)

        # Placeholder ADR and stories index files
        _write(
            "docs/adr/README.md",
            "# Architecture Decision Records\n\n"
            "This directory contains all architecture decisions made for this project.\n"
            "Each decision is documented in a separate Markdown file.\n",
        )
        _write(
            "docs/stories/README.md",
            "# Feature Stories\n\n"
            "This directory contains feature stories and acceptance criteria.\n"
            "Use this to document requirements and expected behavior.\n",
        )

        # Naming bootstrap file
        bootstrap_content = GOVERNANCE_TEMPLATES["naming_bootstrap"].get(
            stack, GOVERNANCE_TEMPLATES["naming_bootstrap"]["Generic"]
        )
        _write(".github/naming-bootstrap.md", bootstrap_content)

        # Persist the selected stack so `archon-mcp detect` can recover it
        # even when the project contains only governance files. The marker is
        # always refreshed to match the current run, so it bypasses the
        # no-overwrite guard by design.
        try:
            marker = resolve_within(root_path, Path(".github/archon-stack.txt"))
            if not dry_run:
                marker.parent.mkdir(parents=True, exist_ok=True)
                marker.write_text(f"{stack}\n", encoding="utf-8")
            if str(marker) not in results["created_files"]:
                results["created_files"].append(str(marker))
        except PathContainmentError as exc:
            results["errors"].append(str(exc))

    except Exception as e:
        results["errors"].append(f"Error creating governance structure: {str(e)}")

    return results
