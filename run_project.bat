@echo off
setlocal
echo ===================================================================
echo   B100 INTELLIGENCE SUITE - Deployment Launcher
echo ===================================================================
echo.
echo [*] Checking for Docker installation...
docker --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Docker is not installed.
    echo [*] Automatically switching to Local Mode (No Docker required)...
    echo.
    call "%~dp0run_without_docker.bat"
    exit /b %errorlevel%
)

:: Check if Docker engine is running
docker info > nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Docker is installed but Docker Desktop is NOT running.
    echo [*] Automatically switching to Local Mode (No Docker required)...
    echo.
    call "%~dp0run_without_docker.bat"
    exit /b %errorlevel%
)

echo [+] Docker is running.
echo.
echo Select launch mode:
echo   [1] Docker Containers (PostgreSQL, Redis, Celery, Django)
echo   [2] Standalone Local Mode (SQLite, Instant start, No Docker overhead)
echo.
set /p choice="Enter choice [1 or 2, default is 1]: "

if "%choice%"=="2" (
    call "%~dp0run_without_docker.bat"
    exit /b %errorlevel%
)

echo.
echo [*] Starting containers (PostgreSQL, Redis, Django, Celery)...
docker-compose up -d --build

if %errorlevel% neq 0 (
    echo [!] ERROR: Failed to start Docker containers.
    echo [*] Would you like to fall back to Local Mode (No Docker)? [Y/N]
    set /p fallback="Choice: "
    if /i "%fallback%"=="Y" (
        call "%~dp0run_without_docker.bat"
        exit /b %errorlevel%
    )
    pause
    exit /b 1
)

echo [*] Waiting for database to initialize (10 seconds)...
timeout /t 10 /nobreak > nul

echo [*] Running ETL Pipeline to populate Data Warehouse...
docker-compose exec web python etl/01_extract_from_mysql.py
docker-compose exec web python etl/02_clean_and_transform.py
docker-compose exec web python etl/03_load_to_warehouse.py

echo [*] Running ML Scoring Engine...
docker-compose exec web python analytics/scoring_engine.py

echo.
echo [+] Deployment and ETL Data Load successful!
echo [+] Web Application running at: http://localhost:8000
echo.
echo Press any key to view logs...
pause > nul
docker-compose logs -f
