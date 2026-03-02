@echo off
REM Nyaya Mitra - Local Setup Script for Windows
REM This script automates the initial setup process

echo ========================================
echo   Nyaya Mitra - Initial Setup
echo ========================================
echo.
echo This script will:
echo 1. Create Python virtual environment
echo 2. Install backend dependencies
echo 3. Install frontend dependencies
echo 4. Initialize database
echo 5. Seed initial data
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul
echo.

REM Check Python
echo [1/8] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo.

REM Check Node.js
echo [2/8] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)
node --version
npm --version
echo.

REM Check PostgreSQL
echo [3/8] Checking PostgreSQL installation...
psql --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: PostgreSQL is not installed or not in PATH
    echo Please install PostgreSQL from https://www.postgresql.org/download/windows/
    pause
    exit /b 1
)
psql --version
echo.

REM Check Ollama
echo [4/8] Checking Ollama installation...
ollama --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Ollama is not installed
    echo Please install Ollama from https://ollama.com/download/windows
    pause
    exit /b 1
)
ollama --version
echo.

REM Setup Backend
echo [5/8] Setting up Backend...
cd backend

REM Create virtual environment
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate and install dependencies
echo Installing Python dependencies...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Install spaCy model
echo Installing spaCy English model...
python -m spacy download en_core_web_sm

REM Create .env if not exists
if not exist .env (
    echo Creating .env file...
    copy .env.example .env
    echo.
    echo IMPORTANT: Please edit backend\.env file with your settings:
    echo - Update DATABASE_URL with your PostgreSQL password
    echo - Generate and add JWT_SECRET
    echo - Generate and add ENCRYPTION_KEY
    echo.
    echo Run these commands to generate keys:
    echo python -c "import secrets; print(secrets.token_urlsafe(32))"
    echo python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    echo.
    pause
)

cd ..
echo Backend setup complete ✓
echo.

REM Setup Frontend
echo [6/8] Setting up Frontend...
cd frontend
echo Installing Node.js dependencies...
call npm install
cd ..
echo Frontend setup complete ✓
echo.

REM Download Ollama model
echo [7/8] Downloading Ollama model...
echo This will download ~4GB. It may take several minutes...
ollama pull mistral:7b
echo Ollama model downloaded ✓
echo.

REM Initialize Database
echo [8/8] Initializing Database...
echo.
echo Please ensure:
echo 1. PostgreSQL is running
echo 2. You have created the 'nyaya_mitra' database
echo 3. You have updated the .env file with correct credentials
echo.
echo To create database, run:
echo psql -U postgres -c "CREATE DATABASE nyaya_mitra;"
echo.
set /p continue="Continue with database initialization? (y/n): "
if /i not "%continue%"=="y" (
    echo Skipping database initialization.
    echo Run manually: python -c "from database import init_db; init_db()"
    goto :skip_db
)

cd backend
call .venv\Scripts\activate.bat
echo Initializing database tables...
python -c "from database import init_db; init_db()"
echo.
echo Seeding emergency contacts...
python seed_emergency_contacts.py
echo.
echo Seeding legal aid providers...
python seed_legal_aid_providers.py
cd ..
echo Database initialized ✓

:skip_db
echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit backend\.env with your settings (if not done)
echo 2. Ensure PostgreSQL is running
echo 3. Ensure Ollama is running
echo 4. Run: start-local.bat
echo.
echo Or start manually:
echo   Backend:  cd backend ^&^& .venv\Scripts\activate ^&^& uvicorn main:app --reload
echo   Frontend: cd frontend ^&^& npm run dev
echo.
pause
