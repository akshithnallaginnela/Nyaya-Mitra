@echo off
REM Nyaya Mitra - Local Startup Script for Windows
REM This script starts both backend and frontend servers

echo ========================================
echo   Nyaya Mitra - Starting Application
echo ========================================
echo.

REM Check if PostgreSQL is running
echo [1/5] Checking PostgreSQL...
sc query postgresql-x64-18 | find "RUNNING" >nul
if errorlevel 1 (
    echo PostgreSQL is not running. Please start PostgreSQL service.
    echo Run: net start postgresql-x64-18
    pause
    exit /b 1
)
echo PostgreSQL is running ✓
echo.

REM Check AI provider
set AI_PROVIDER=ollama
if exist backend\.env (
    for /f "tokens=2 delims==" %%a in ('findstr /i "AI_PROVIDER=" backend\.env') do set AI_PROVIDER=%%a
)
set AI_PROVIDER=%AI_PROVIDER: =%

if /i "%AI_PROVIDER%"=="bedrock" (
    echo [2/5] Using AI Provider: Amazon Bedrock (skipping Ollama check)
) else (
    REM Check if Ollama is running
    echo [2/5] Checking Ollama...
    curl -s http://localhost:11434/api/tags >nul 2>&1
    if errorlevel 1 (
        echo Ollama is not running. Please start Ollama from Start menu.
        pause
        exit /b 1
    )
    echo Ollama is running ✓
)
echo.

REM Start Backend
echo [3/5] Starting Backend Server...
start "Nyaya Mitra Backend" cmd /k "cd backend && .venv\Scripts\activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo Backend starting on http://localhost:8000
timeout /t 5 /nobreak >nul
echo.

REM Start Frontend
echo [4/5] Starting Frontend Server...
start "Nyaya Mitra Frontend" cmd /k "cd frontend && npm run dev"
echo Frontend starting on http://localhost:5173
timeout /t 5 /nobreak >nul
echo.

echo [5/5] Opening Application...
timeout /t 10 /nobreak >nul
start http://localhost:5173
echo.

echo ========================================
echo   Application Started Successfully!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to stop all servers...
pause >nul

REM Stop servers
echo.
echo Stopping servers...
taskkill /FI "WindowTitle eq Nyaya Mitra Backend*" /T /F >nul 2>&1
taskkill /FI "WindowTitle eq Nyaya Mitra Frontend*" /T /F >nul 2>&1
echo Servers stopped.
echo.
pause
