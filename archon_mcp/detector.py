"""Tech-stack auto-detection logic."""

from pathlib import Path

from archon_mcp.constants import VALID_STACKS


def detect_tech_stack(root_path: Path) -> str:
    """
    Detect the tech stack from files in the root directory.

    Returns one of the VALID_STACKS identifiers, falling back to 'Generic'.
    """
    files_and_dirs: set[str] = set()
    suffixes: set[str] = set()
    try:
        for item in root_path.iterdir():
            files_and_dirs.add(item.name)
            if item.is_file():
                suffixes.add(item.suffix)
    except (PermissionError, OSError):
        pass

    # Presence signals
    has_package_json = "package.json" in files_and_dirs
    has_tsconfig = "tsconfig.json" in files_and_dirs
    has_next_config = any(
        f in files_and_dirs
        for f in ("next.config.js", "next.config.ts", "next.config.mjs")
    )
    has_angular_json = "angular.json" in files_and_dirs
    has_vite_config = any(
        f in files_and_dirs for f in ("vite.config.ts", "vite.config.js")
    )
    has_vue_config = "vue.config.js" in files_and_dirs
    has_py_files = ".py" in suffixes
    has_requirements = "requirements.txt" in files_and_dirs
    has_pyproject = "pyproject.toml" in files_and_dirs
    has_fastapi = "main.py" in files_and_dirs or "app.py" in files_and_dirs
    has_django = "manage.py" in files_and_dirs
    has_pom = "pom.xml" in files_and_dirs
    has_gradle = (
        "build.gradle" in files_and_dirs or "build.gradle.kts" in files_and_dirs
    )
    has_tsx_jsx = ".tsx" in suffixes or ".jsx" in suffixes

    # Angular + Spring Boot + MySQL
    if has_angular_json and (has_pom or has_gradle):
        return "Angular-SpringBoot-MySQL"

    # Next.js + Django + Postgres
    if has_next_config and has_django:
        return "Next.js-Django-Postgres"

    # Vue + Express + MongoDB (Vite present, no Python backend)
    if has_package_json and (has_vite_config or has_vue_config) and not has_py_files:
        return "Vue-Express-MongoDB"

    # React + FastAPI + Postgres (Python backend detected)
    if has_package_json and has_fastapi and not has_django:
        react_signals = sum([has_tsconfig, has_tsx_jsx])
        if react_signals >= 1:
            return "React-FastAPI-Postgres"

    # React + Node + MongoDB (MERN: JS-only, no Python, no Angular, no Next)
    if (
        has_package_json
        and not has_py_files
        and not has_django
        and not has_angular_json
        and not has_next_config
        and (has_tsconfig or has_tsx_jsx)
    ):
        return "React-Node-MongoDB"

    return "Generic"


