@echo off
setlocal

REM Project-local virtualenv workflow for ArchonMCP
REM Usage:
REM   project_venv.bat setup
REM   project_venv.bat audit
REM   project_venv.bat help

set "ACTION=%~1"
if "%ACTION%"=="" set "ACTION=help"

if /I "%ACTION%"=="setup" goto setup
if /I "%ACTION%"=="audit" goto audit
if /I "%ACTION%"=="help" goto help

echo Unknown action: %ACTION%
goto help

:setup
echo [1/4] Creating .venv...
python -m venv .venv
if errorlevel 1 exit /b 1

echo [2/4] Installing into .venv using host pip...
python -m pip --python .venv install --upgrade pip
if errorlevel 1 exit /b 1

echo [3/4] Installing project (editable)...
python -m pip --python .venv install -e .
if errorlevel 1 exit /b 1

echo [4/4] Installing audit tools in venv...
python -m pip --python .venv install pip-audit "pip-audit-html[mcp]"
if errorlevel 1 exit /b 1

echo.
echo Setup complete.
echo Activate with: .\.venv\Scripts\activate
exit /b 0

:audit
if not exist .venv\Scripts\python.exe (
  echo .venv not found. Run: project_venv.bat setup
  exit /b 1
)

echo Running project-scoped audit from .venv...
.\.venv\Scripts\python -m pip_audit . -f json -o project-audit.json
if errorlevel 1 (
  echo pip-audit reported vulnerabilities or errors.
)

echo Rendering HTML report...
.\.venv\Scripts\python -m pip_audit_html project-audit.json -o security.html --title "ArchonMCP Project Dependency Security"
if errorlevel 1 exit /b 1

echo Done. Generated: project-audit.json and security.html
exit /b 0

:help
echo Usage: project_venv.bat [setup^|audit^|help]
exit /b 0
