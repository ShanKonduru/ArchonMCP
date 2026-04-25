@echo off
setlocal

REM Run ArchonMCP test suite with optional coverage report.
REM
REM Usage:
REM   run_tests.bat              -- run all tests
REM   run_tests.bat coverage     -- run tests + generate HTML coverage report
REM   run_tests.bat help         -- show this help

set "ACTION=%~1"
if "%ACTION%"=="" set "ACTION=run"

if /I "%ACTION%"=="run"      goto run
if /I "%ACTION%"=="coverage" goto coverage
if /I "%ACTION%"=="help"     goto help

echo Unknown action: %ACTION%
goto help

:run
echo ============================================================
echo  ArchonMCP Test Suite
echo ============================================================
python -m pytest tests/ -v --tb=short
if errorlevel 1 (
  echo.
  echo Tests FAILED.
  exit /b 1
)
echo.
echo All tests passed.
exit /b 0

:coverage
echo ============================================================
echo  ArchonMCP Test Suite with Coverage
echo ============================================================
python -m pytest tests/ -v --tb=short ^
  --cov=archon_mcp ^
  --cov-report=term-missing ^
  --cov-report=html:htmlcov
if errorlevel 1 (
  echo.
  echo Tests FAILED.
  exit /b 1
)
echo.
echo Coverage report written to: htmlcov\index.html
exit /b 0

:help
echo Usage: run_tests.bat [run^|coverage^|help]
echo.
echo   run       Run all tests (default)
echo   coverage  Run tests and generate HTML coverage report in htmlcov\
echo   help      Show this message
exit /b 0
