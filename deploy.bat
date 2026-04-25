@echo off
REM ArchonMCP - Build and Deploy Script for Windows
REM Supports both CLI and MCP Server modes
REM
REM After deployment, use:
REM   archon-mcp init            - Initialize governance (CLI mode)
REM   archon-mcp detect          - Detect tech stack (CLI mode)  
REM   archon-mcp server          - Run as MCP server (IDE integration)
REM   archon-mcp --help          - Show all available commands

setlocal enabledelayedexpansion

echo.
echo ========================================
echo ArchonMCP Build and Deploy Tool
echo ========================================
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

REM Check for required tools
pip show build >nul 2>&1
if errorlevel 1 (
    echo Installing build tools...
    pip install build twine
) else (
    echo Build tools already installed
)

REM Menu
echo.
echo Select an action:
echo 1. Build only
echo 2. Test locally with pip
echo 3. Upload to TestPyPI
echo 4. Upload to PyPI (production)
echo 5. Full cycle (build + TestPyPI + PyPI)
echo 6. Clean build artifacts
echo.

set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto build
if "%choice%"=="2" goto test_local
if "%choice%"=="3" goto testpypi
if "%choice%"=="4" goto pypi
if "%choice%"=="5" goto full_cycle
if "%choice%"=="6" goto clean
echo Invalid choice
exit /b 1

:build
echo.
echo Building package...
python -m build
if errorlevel 1 (
    echo Error: Build failed
    exit /b 1
)
echo Build completed successfully!
echo Artifacts in: dist/
goto end

:test_local
echo.
echo Building package...
python -m build
if errorlevel 1 (
    echo Error: Build failed
    exit /b 1
)
echo.
echo Testing with pip...
pip install -e .
echo.
echo Testing installation...
python -c "import archon_mcp; print('ArchonMCP installed successfully')"
if errorlevel 1 (
    echo Error: Installation or import failed
    exit /b 1
)
echo Local test completed successfully!
goto end

:testpypi
echo.
echo Building package...
python -m build
if errorlevel 1 (
    echo Error: Build failed
    exit /b 1
)
echo.
echo Uploading to TestPyPI...
echo Note: You will need TestPyPI credentials
echo.
python -m twine upload --repository testpypi dist/*
if errorlevel 1 (
    echo Error: TestPyPI upload failed
    exit /b 1
)
echo.
echo Successfully uploaded to TestPyPI!
echo To test the package, run:
echo   pip install --index-url https://test.pypi.org/simple/ archon-mcp
goto end

:pypi
echo.
echo WARNING: This will upload to production PyPI
echo Ensure version is incremented in pyproject.toml
echo.
set /p confirm="Continue? (yes/no): "
if /i not "%confirm%"=="yes" (
    echo Upload cancelled
    exit /b 0
)
echo.
echo Building package...
python -m build
if errorlevel 1 (
    echo Error: Build failed
    exit /b 1
)
echo.
echo Uploading to PyPI...
python -m twine upload dist/*
if errorlevel 1 (
    echo Error: PyPI upload failed
    exit /b 1
)
echo.
echo Successfully uploaded to PyPI!
goto end

:full_cycle
echo.
echo Full deployment cycle: Clean ^> Build ^> TestPyPI ^> PyPI
echo.
echo Cleaning old artifacts...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist *.egg-info rmdir /s /q *.egg-info
echo.
echo Building package...
python -m build
if errorlevel 1 (
    echo Error: Build failed
    exit /b 1
)
echo.
echo Uploading to TestPyPI...
python -m twine upload --repository testpypi dist/*
if errorlevel 1 (
    echo Error: TestPyPI upload failed
    exit /b 1
)
echo.
echo TestPyPI upload successful. Testing installation...
pause
pip install --index-url https://test.pypi.org/simple/ --no-deps archon-mcp
echo.
echo WARNING: This will upload to production PyPI
echo Ensure version is incremented in pyproject.toml
echo.
set /p confirm="Continue to PyPI? (yes/no): "
if /i not "%confirm%"=="yes" (
    echo PyPI upload cancelled
    exit /b 0
)
echo.
echo Uploading to PyPI...
python -m twine upload dist/*
if errorlevel 1 (
    echo Error: PyPI upload failed
    exit /b 1
)
echo.
echo Full deployment cycle completed successfully!
goto end

:clean
echo.
echo Cleaning build artifacts...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
for /d %%x in (*.egg-info) do rmdir /s /q "%%x"
echo Clean completed!
goto end

:end
echo.
echo ========================================
echo Operation completed
echo ========================================
echo.
endlocal
exit /b 0
