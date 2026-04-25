#!/usr/bin/env bash
set -e

# Run ArchonMCP test suite with optional coverage report.
#
# Usage:
#   ./run_tests.sh              -- run all tests
#   ./run_tests.sh coverage     -- run tests + generate HTML coverage report
#   ./run_tests.sh help         -- show this help

action="${1:-run}"

run_tests() {
  echo "============================================================"
  echo " ArchonMCP Test Suite"
  echo "============================================================"
  python3 -m pytest tests/ -v --tb=short
  echo ""
  echo "All tests passed."
}

run_coverage() {
  echo "============================================================"
  echo " ArchonMCP Test Suite with Coverage"
  echo "============================================================"
  python3 -m pytest tests/ -v --tb=short \
    --cov=archon_mcp \
    --cov-report=term-missing \
    --cov-report=html:htmlcov
  echo ""
  echo "Coverage report written to: htmlcov/index.html"
}

help_cmd() {
  echo "Usage: ./run_tests.sh [run|coverage|help]"
  echo ""
  echo "  run       Run all tests (default)"
  echo "  coverage  Run tests and generate HTML coverage report in htmlcov/"
  echo "  help      Show this message"
}

case "$action" in
  run)      run_tests ;;
  coverage) run_coverage ;;
  help)     help_cmd ;;
  *)
    echo "Unknown action: $action"
    help_cmd
    exit 1
    ;;
esac
