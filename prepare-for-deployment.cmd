@echo off
echo ========================================
echo   Nyaya Mitra - Deployment Preparation
echo ========================================
echo.

echo This script will verify your project is ready for AWS deployment.
echo.
pause

echo.
echo [1/5] Checking Backend...
echo ========================================
cd backend

if not exist .venv (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv .venv
    pause
    exit /b 1
)

call .venv\Scripts\activate

echo Testing backend imports...
python -c "from database import init_db; print('✓ Backend imports OK')" 2>nul
if errorlevel 1 (
    echo ERROR: Backend imports failed!
    echo Please run: pip install -r requirements.txt
    pause
    exit /b 1
)

echo ✓ Backend check passed!
echo.

echo [2/5] Checking Frontend...
echo ========================================
cd ..\frontend

if not exist node_modules (
    echo ERROR: node_modules not found!
    echo Please run: npm install
    pause
    exit /b 1
)

echo Testing frontend build...
call npm run build >nul 2>&1
if errorlevel 1 (
    echo ERROR: Frontend build failed!
    echo Please run: npm run build
    pause
    exit /b 1
)

echo ✓ Frontend check passed!
echo.

echo [3/5] Checking Required Files...
echo ========================================
cd ..

if not exist backend\.env (
    echo WARNING: backend\.env not found!
    echo You'll need to create this on AWS EC2
)

if not exist backend\requirements.txt (
    echo ERROR: backend\requirements.txt not found!
    pause
    exit /b 1
)

if not exist frontend\package.json (
    echo ERROR: frontend\package.json not found!
    pause
    exit /b 1
)

echo ✓ Required files present!
echo.

echo [4/5] Checking Deployment Guides...
echo ========================================

if not exist AWS_MVP_DEPLOYMENT_GUIDE.md (
    echo ERROR: AWS_MVP_DEPLOYMENT_GUIDE.md not found!
    pause
    exit /b 1
)

if not exist AWS_DEPLOYMENT_CHECKLIST.md (
    echo ERROR: AWS_DEPLOYMENT_CHECKLIST.md not found!
    pause
    exit /b 1
)

echo ✓ Deployment guides present!
echo.

echo [5/5] Creating Deployment Package...
echo ========================================

echo Creating deployment-info.txt template...
(
echo === AWS DEPLOYMENT INFO ===
echo.
echo AWS Account ID: __________________
echo AWS Region: us-east-1
echo.
echo === DATABASE ===
echo RDS Endpoint: ____________________
echo Database Name: nyaya_mitra
echo Username: nyaya_admin
echo Password: ____________________
echo.
echo === EC2 INSTANCE ===
echo Instance ID: ____________________
echo Public IP: ____________________
echo Public DNS: ____________________
echo SSH Key: nyaya-mitra-key.pem
echo.
echo === S3 BUCKET ===
echo Bucket Name: ____________________
echo Website URL: ____________________
echo.
echo === CLOUDFRONT ===
echo Distribution ID: ____________________
echo CloudFront URL: ____________________
echo.
echo === DOMAIN (Optional) ===
echo Domain Name: ____________________
) > deployment-info.txt

echo ✓ Created deployment-info.txt
echo.

echo ========================================
echo   ✓ DEPLOYMENT PREPARATION COMPLETE!
echo ========================================
echo.
echo Your project is ready for AWS deployment!
echo.
echo NEXT STEPS:
echo 1. Open START_AWS_DEPLOYMENT.md
echo 2. Follow the step-by-step guide
echo 3. Fill in deployment-info.txt as you go
echo.
echo ESTIMATED TIME: 3-4 hours
echo ESTIMATED COST: $75-95/month
echo.
echo Good luck! 🚀
echo.
pause
