@echo off
REM Pre-Deployment Check Script for Nyaya Mitra
REM Run this before deploying to AWS to ensure everything is ready

echo ========================================
echo Nyaya Mitra Pre-Deployment Check
echo ========================================
echo.

REM Check if AWS CLI is installed
echo [1/8] Checking AWS CLI...
aws --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [FAIL] AWS CLI not found. Install from: https://aws.amazon.com/cli/
    goto :error
) else (
    echo [PASS] AWS CLI installed
)
echo.

REM Check if Node.js is installed
echo [2/8] Checking Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [FAIL] Node.js not found. Install from: https://nodejs.org/
    goto :error
) else (
    echo [PASS] Node.js installed
    node --version
)
echo.

REM Check if Python is installed
echo [3/8] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [FAIL] Python not found. Install Python 3.11+
    goto :error
) else (
    echo [PASS] Python installed
    python --version
)
echo.

REM Check if Git is installed
echo [4/8] Checking Git...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [FAIL] Git not found. Install from: https://git-scm.com/
    goto :error
) else (
    echo [PASS] Git installed
)
echo.

REM Check if backend .env.example exists
echo [5/8] Checking backend configuration...
if not exist "backend\.env.example" (
    echo [WARN] backend\.env.example not found
) else (
    echo [PASS] Backend configuration template found
)
echo.

REM Check if frontend package.json exists
echo [6/8] Checking frontend configuration...
if not exist "frontend\package.json" (
    echo [FAIL] frontend\package.json not found
    goto :error
) else (
    echo [PASS] Frontend configuration found
)
echo.

REM Check if backend requirements.txt exists
echo [7/8] Checking backend dependencies...
if not exist "backend\requirements.txt" (
    echo [FAIL] backend\requirements.txt not found
    goto :error
) else (
    echo [PASS] Backend dependencies file found
)
echo.

REM Check AWS credentials
echo [8/8] Checking AWS credentials...
aws sts get-caller-identity >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARN] AWS credentials not configured or invalid
    echo Run: aws configure
) else (
    echo [PASS] AWS credentials configured
    aws sts get-caller-identity
)
echo.

echo ========================================
echo Pre-Deployment Check Complete!
echo ========================================
echo.
echo Next Steps:
echo 1. Review AWS_BEDROCK_DEPLOYMENT_GUIDE.md
echo 2. Open DEPLOYMENT_CHECKLIST.md to track progress
echo 3. Ensure you have:
echo    - AWS account with $200 credits
echo    - Strong passwords prepared
echo    - SSH key pair ready
echo.
echo Ready to deploy? Follow the deployment guide!
echo.
pause
exit /b 0

:error
echo.
echo ========================================
echo Pre-Deployment Check FAILED
echo ========================================
echo Please fix the issues above before deploying.
echo.
pause
exit /b 1
