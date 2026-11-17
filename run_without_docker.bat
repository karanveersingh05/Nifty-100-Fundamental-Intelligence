@echo off
setlocal enabledelayedexpansion
title B100 Intelligence Suite - Local (No Docker)

echo ===================================================================
echo   B100 INTELLIGENCE SUITE - Standalone Local Runner (No Docker)
echo ===================================================================
echo.

:: 1. Navigate to project root directory
cd /d "%~dp0"

:: 2. Find Python interpreter (prefer virtualenv)
if exist "venv\Scripts\python.exe" (
    set "PYTHON_EXE=venv\Scripts\python.exe"
    echo [+] Using virtual environment Python: !PYTHON_EXE!
) else (
    where python >nul 2>&1
    if !errorlevel! equ 0 (
        set "PYTHON_EXE=python"
        echo [+] Using system Python: python
    ) else (
        echo [!] ERROR: Python is not found on your system.
        echo [!] Please install Python 3.10+ or create the venv folder.
        pause
        exit /b 1
    )
)

:: 3. Set environment for SQLite + local cache mode
set USE_SQLITE=1
set PYTHONPATH=%cd%

echo.
:: 4. Check if SQLite database already exists
if not exist "data\b100_local.sqlite3" (
    echo [*] First-time setup detected. Initializing SQLite Data Warehouse...
    echo [*] Running database migrations...
    !PYTHON_EXE! webapp\manage.py migrate
    if !errorlevel! neq 0 (
        echo [!] Migration failed.
        pause
        exit /b 1
    )

    echo.
    echo [*] Running ETL pipeline: Excel to Clean to SQLite Warehouse...
    !PYTHON_EXE! etl\01_extract_from_mysql.py
    !PYTHON_EXE! etl\02_clean_and_transform.py
    !PYTHON_EXE! etl\03_load_to_warehouse.py

    echo.
    echo [*] Running ML Scoring Engine...
    !PYTHON_EXE! analytics\scoring_engine.py
    echo [+] First-time initialization complete!
) else (
    echo [+] SQLite database found: data\b100_local.sqlite3
    echo [*] Applying any pending migrations...
    !PYTHON_EXE! webapp\manage.py migrate >nul 2>&1
)

echo.
echo ===================================================================
echo   [+] B100 Intelligence is ready!
echo   [*] Web Dashboard : http://127.0.0.1:8000
echo   [*] Press Ctrl+C in this window to stop the server.
echo ===================================================================
echo.

:: 5. Automatically open browser after 2 seconds in background
start "" /b cmd /c "ping -n 3 127.0.0.1 >nul & start http://127.0.0.1:8000"

:: 6. Start Django development server
!PYTHON_EXE! webapp\manage.py runserver 127.0.0.1:8000

pause
