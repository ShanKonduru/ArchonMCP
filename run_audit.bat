@echo off
setlocal

REM Run pip-audit against the project and generate an HTML security report.
REM Requires: .venv with pip-audit and pip-audit-html[mcp] installed.
REM           Run project_venv.bat setup first if .venv is missing.
REM
REM Usage:
REM   run_audit.bat              -- audit project deps + generate HTML report
REM   run_audit.bat html         -- same as above (explicit)
REM   run_audit.bat json         -- generate JSON report only (no HTML)
REM   run_audit.bat help         -- show this help

set "ACTION=%~1"
if "%ACTION%"=="" set "ACTION=html"

if /I "%ACTION%"=="html" goto html
if /I "%ACTION%"=="json" goto json
if /I "%ACTION%"=="help" goto help

echo Unknown action: %ACTION%
goto help

:html
if not exist .venv\Scripts\python.exe (
  echo .venv not found. Run: project_venv.bat setup
  exit /b 1
)

echo ============================================================
echo  ArchonMCP Security Audit
echo ============================================================

echo [1/2] Running pip-audit (project scope)...
set "AUDIT_EXIT=0"
.\.venv\Scripts\python -m pip_audit . -f json -o project-audit.json
if errorlevel 1 (
  echo pip-audit found vulnerabilities or encountered errors.
  set "AUDIT_EXIT=1"
)

echo [2/2] Generating HTML report...
.\.venv\Scripts\python -m pip_audit_html project-audit.json ^
  -o security_project.html ^
  --title "ArchonMCP Project Dependency Security"
if errorlevel 1 exit /b 1

echo.
echo Done.
echo   JSON : project-audit.json
echo   HTML : security_project.html
if "%AUDIT_EXIT%"=="1" (
  echo.
  echo WARNING: Vulnerabilities detected. Review security_project.html.
  exit /b 1
)
exit /b 0

:json
if not exist .venv\Scripts\python.exe (
  echo .venv not found. Run: project_venv.bat setup
  exit /b 1
)

echo Running pip-audit (project scope, JSON only)...
.\.venv\Scripts\python -m pip_audit . -f json -o project-audit.json
if errorlevel 1 (
  echo pip-audit found vulnerabilities or encountered errors.
  echo Review: project-audit.json
  exit /b 1
)
echo Done. JSON report written to: project-audit.json
exit /b 0

:help
echo Usage: run_audit.bat [html^|json^|help]
echo.
echo   html   Audit project dependencies and produce HTML + JSON reports (default)
echo   json   Audit project dependencies and produce JSON report only
echo   help   Show this message
echo.
echo Prerequisite: run project_venv.bat setup to create .venv with audit tools.
exit /b 0
