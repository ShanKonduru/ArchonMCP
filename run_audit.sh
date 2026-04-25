#!/usr/bin/env bash
set -e

# Run pip-audit against the project and generate an HTML security report.
# Requires: .venv with pip-audit and pip-audit-html[mcp] installed.
#           Run ./project_venv.sh setup first if .venv is missing.
#
# Usage:
#   ./run_audit.sh              -- audit project deps + generate HTML report
#   ./run_audit.sh html         -- same as above (explicit)
#   ./run_audit.sh json         -- generate JSON report only (no HTML)
#   ./run_audit.sh help         -- show this help

action="${1:-html}"

_check_venv() {
  if [ ! -x ".venv/bin/python" ]; then
    echo ".venv not found. Run: ./project_venv.sh setup"
    exit 1
  fi
}

run_html() {
  _check_venv

  echo "============================================================"
  echo " ArchonMCP Security Audit"
  echo "============================================================"

  echo "[1/2] Running pip-audit (project scope)..."
  audit_exit=0
  set +e
  .venv/bin/python -m pip_audit . -f json -o project-audit.json
  audit_exit=$?
  set -e

  if [ "$audit_exit" -ne 0 ]; then
    echo "pip-audit found vulnerabilities or encountered errors."
  fi

  echo "[2/2] Generating HTML report..."
  .venv/bin/python -m pip_audit_html project-audit.json \
    -o security_project.html \
    --title "ArchonMCP Project Dependency Security"

  echo ""
  echo "Done."
  echo "  JSON : project-audit.json"
  echo "  HTML : security_project.html"

  if [ "$audit_exit" -ne 0 ]; then
    echo ""
    echo "WARNING: Vulnerabilities detected. Review security_project.html."
    exit "$audit_exit"
  fi
}

run_json() {
  _check_venv

  echo "Running pip-audit (project scope, JSON only)..."
  set +e
  .venv/bin/python -m pip_audit . -f json -o project-audit.json
  audit_exit=$?
  set -e

  if [ "$audit_exit" -ne 0 ]; then
    echo "pip-audit found vulnerabilities or encountered errors."
    echo "Review: project-audit.json"
    exit "$audit_exit"
  fi

  echo "Done. JSON report written to: project-audit.json"
}

help_cmd() {
  echo "Usage: ./run_audit.sh [html|json|help]"
  echo ""
  echo "  html   Audit project dependencies and produce HTML + JSON reports (default)"
  echo "  json   Audit project dependencies and produce JSON report only"
  echo "  help   Show this message"
  echo ""
  echo "Prerequisite: run ./project_venv.sh setup to create .venv with audit tools."
}

case "$action" in
  html) run_html ;;
  json) run_json ;;
  help) help_cmd ;;
  *)
    echo "Unknown action: $action"
    help_cmd
    exit 1
    ;;
esac
