"""Tests for archon_mcp.detector."""

from pathlib import Path

import pytest

from archon_mcp.detector import detect_tech_stack


def _touch(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ── concrete stacks ─────────────────────────────────────────────────────────

def test_react_fastapi_postgres_tsconfig(tmp_path):
    _touch(tmp_path / "package.json")
    _touch(tmp_path / "tsconfig.json")
    _touch(tmp_path / "main.py")
    assert detect_tech_stack(tmp_path) == "React-FastAPI-Postgres"


def test_react_fastapi_postgres_tsx(tmp_path):
    _touch(tmp_path / "package.json")
    _touch(tmp_path / "App.tsx")
    _touch(tmp_path / "app.py")
    assert detect_tech_stack(tmp_path) == "React-FastAPI-Postgres"


def test_nextjs_django_postgres(tmp_path):
    _touch(tmp_path / "next.config.js")
    _touch(tmp_path / "manage.py")
    assert detect_tech_stack(tmp_path) == "Next.js-Django-Postgres"


def test_nextjs_django_postgres_mjs(tmp_path):
    _touch(tmp_path / "next.config.mjs")
    _touch(tmp_path / "manage.py")
    assert detect_tech_stack(tmp_path) == "Next.js-Django-Postgres"


def test_vue_express_mongodb_vite(tmp_path):
    _touch(tmp_path / "package.json")
    _touch(tmp_path / "vite.config.ts")
    assert detect_tech_stack(tmp_path) == "Vue-Express-MongoDB"


def test_vue_express_mongodb_vue_config(tmp_path):
    _touch(tmp_path / "package.json")
    _touch(tmp_path / "vue.config.js")
    assert detect_tech_stack(tmp_path) == "Vue-Express-MongoDB"


def test_angular_springboot_mysql_pom(tmp_path):
    _touch(tmp_path / "angular.json")
    _touch(tmp_path / "pom.xml")
    assert detect_tech_stack(tmp_path) == "Angular-SpringBoot-MySQL"


def test_angular_springboot_mysql_gradle(tmp_path):
    _touch(tmp_path / "angular.json")
    _touch(tmp_path / "build.gradle")
    assert detect_tech_stack(tmp_path) == "Angular-SpringBoot-MySQL"


def test_react_node_mongodb_tsconfig(tmp_path):
    _touch(tmp_path / "package.json")
    _touch(tmp_path / "tsconfig.json")
    assert detect_tech_stack(tmp_path) == "React-Node-MongoDB"


def test_react_node_mongodb_jsx(tmp_path):
    _touch(tmp_path / "package.json")
    _touch(tmp_path / "App.jsx")
    assert detect_tech_stack(tmp_path) == "React-Node-MongoDB"


# ── generic fallback ─────────────────────────────────────────────────────────

def test_generic_empty_dir(tmp_path):
    assert detect_tech_stack(tmp_path) == "Generic"


def test_generic_only_readme(tmp_path):
    _touch(tmp_path / "README.md")
    assert detect_tech_stack(tmp_path) == "Generic"


def test_generic_python_only_no_framework(tmp_path):
    _touch(tmp_path / "script.py")
    assert detect_tech_stack(tmp_path) == "Generic"


# ── permission-error resilience ──────────────────────────────────────────────

def test_returns_generic_for_unreadable_dir(tmp_path, monkeypatch):
    """detect_tech_stack should not raise on PermissionError."""
    from pathlib import Path as _Path

    def _bad_iterdir(self):
        raise PermissionError("no permission")

    monkeypatch.setattr(_Path, "iterdir", _bad_iterdir)
    result = detect_tech_stack(tmp_path)
    assert result == "Generic"
