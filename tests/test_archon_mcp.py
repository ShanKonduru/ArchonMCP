import asyncio
from pathlib import Path

import archon_mcp


def _touch(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_detect_stack_nextjs_django_postgres(tmp_path: Path) -> None:
    _touch(tmp_path / "next.config.js", "module.exports = {}")
    _touch(tmp_path / "manage.py", "#!/usr/bin/env python")

    detected = archon_mcp.detect_tech_stack(tmp_path)

    assert detected == "Next.js-Django-Postgres"


def test_detect_stack_angular_springboot_mysql(tmp_path: Path) -> None:
    _touch(tmp_path / "angular.json", "{}")
    _touch(tmp_path / "pom.xml", "<project></project>")

    detected = archon_mcp.detect_tech_stack(tmp_path)

    assert detected == "Angular-SpringBoot-MySQL"


def test_detect_stack_react_fastapi_postgres(tmp_path: Path) -> None:
    _touch(tmp_path / "package.json", "{}")
    _touch(tmp_path / "main.py", "from fastapi import FastAPI")
    _touch(tmp_path / "App.tsx", "export const App = () => null")

    detected = archon_mcp.detect_tech_stack(tmp_path)

    assert detected == "React-FastAPI-Postgres"


def test_detect_stack_generic_when_no_signals(tmp_path: Path) -> None:
    _touch(tmp_path / "README.md", "hello")

    detected = archon_mcp.detect_tech_stack(tmp_path)

    assert detected == "Generic"


def test_create_governance_structure_creates_expected_files(tmp_path: Path) -> None:
    result = archon_mcp.create_governance_structure(tmp_path, "React-Node-MongoDB")

    assert result["errors"] == []
    assert result["stack"] == "React-Node-MongoDB"

    required_paths = [
        tmp_path / ".github" / "copilot-instructions.md",
        tmp_path / ".github" / "skills" / "security.md",
        tmp_path / ".github" / "skills" / "migration.md",
        tmp_path / ".github" / "skills" / "done.md",
        tmp_path / ".github" / "prompts" / "gap-analysis.md",
        tmp_path / ".github" / "prompts" / "harden.md",
        tmp_path / ".github" / "prompts" / "done.md",
        tmp_path / "docs" / "adr" / "README.md",
        tmp_path / "docs" / "stories" / "README.md",
        tmp_path / ".github" / "naming-bootstrap.md",
    ]

    for path in required_paths:
        assert path.exists(), f"Missing expected file: {path}"


def test_create_governance_structure_invalid_stack_falls_back_to_generic(tmp_path: Path) -> None:
    result = archon_mcp.create_governance_structure(tmp_path, "Unknown-Stack")

    assert result["errors"] == []
    assert result["stack"] == "Generic"


def test_init_governance_returns_error_for_missing_root() -> None:
    result = asyncio.run(archon_mcp.init_governance(root_directory="Z:/definitely-missing"))

    assert result.isError is True
    assert any("does not exist" in content.text for content in result.content)


def test_list_tools_exposes_supported_stacks_enum() -> None:
    tools = asyncio.run(archon_mcp.list_tools())

    assert len(tools) == 1
    tool = tools[0]
    assert tool.name == "init_governance"
    assert tool.inputSchema["properties"]["stack"]["enum"] == archon_mcp.VALID_STACKS
