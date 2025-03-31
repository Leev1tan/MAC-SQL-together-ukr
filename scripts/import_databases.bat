@echo off
echo === BIRD-UKR Benchmark Database Import Tool ===
echo.

REM Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found. Please install Python before running this script.
    exit /b 1
)

REM Check Python version (need 3.6+)
for /f "tokens=2" %%V in ('python --version 2^>^&1') do (
    echo Found Python version: %%V
    set PYVER=%%V
)

REM Check if psycopg2 is installed
python -c "import psycopg2" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: psycopg2 module not found. Attempting to install...
    pip install -r %~dp0\requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to install required packages. Please run manually:
        echo pip install -r %~dp0\requirements.txt
        exit /b 1
    )
    echo Successfully installed required packages.
)

REM Check if PostgreSQL is installed
where psql >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: PostgreSQL not found. Please install PostgreSQL and make sure psql is in your PATH.
    exit /b 1
)

REM Run the import script
echo.
echo Running database import script...
echo.
cd %~dp0\..
python %~dp0\import_databases.py

echo.
if %ERRORLEVEL% NEQ 0 (
    echo Import process completed with errors. See above for details.
) else (
    echo Import process completed successfully!
)

pause 