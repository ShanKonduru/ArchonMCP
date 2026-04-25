#!/usr/bin/env bash
set -e

# Project-local virtualenv workflow for ArchonMCP
# Usage:
#   ./project_venv.sh setup
#   ./project_venv.sh audit
#   ./project_venv.sh help

action="${1:-help}"

setup() {
  echo "[1/4] Creating .venv..."
  python3 -m venv .venv

  echo "[2/4] Installing into .venv using host pip..."
  python3 -m pip --python .venv install --upgrade pip

  echo "[3/4] Installing project (editable)..."
  python3 -m pip --python .venv install -e .

  echo "[4/4] Installing audit tools in venv..."
  python3 -m pip --python .venv install pip-audit "pip-audit-html[mcp]"

  echo ""
  echo "Setup complete."
  echo "Activate with: source .venv/bin/activate"
}

audit() {
  if [ ! -x ".venv/bin/python" ]; then
    echo ".venv not found. Run: ./project_venv.sh setup"
    exit 1
  fi

  echo "Running project-scoped audit from .venv..."
  set +e
  .venv/bin/python -m pip_audit . -f json -o project-audit.json
  audit_exit=$?
  set -e

  if [ "$audit_exit" -ne 0 ]; then
    echo "pip-audit reported vulnerabilities or errors."
  fi

  echo "Rendering HTML report..."
  .venv/bin/pip-audit-html project-audit.json -o security.html --title "ArchonMCP Project Dependency Security"

  echo "Done. Generated: project-audit.json and security.html"
  return "$audit_exit"
}

help_cmd() {
  echo "Usage: ./project_venv.sh [setup|audit|help]"
}

case "$action" in
  setup) setup ;;
  audit) audit ;;
  help) help_cmd ;;
  *)
    echo "Unknown action: $action"
    help_cmd
    exit 1
    ;;
esac
