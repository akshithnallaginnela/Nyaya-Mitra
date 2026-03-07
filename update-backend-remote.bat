@echo off
REM Backend Update Script for Nyaya Mitra (Remote EC2)
REM Use this to update backend code on EC2 after changes

echo ========================================
echo Nyaya Mitra Backend Update Script
echo ========================================
echo.

REM Get EC2 details
set /p EC2_IP="Enter your EC2 public IP: "
if "%EC2_IP%"=="" (
    echo [ERROR] EC2 IP is required
    pause
    exit /b 1
)

set /p KEY_FILE="Enter path to your .pem key file: "
if "%KEY_FILE%"=="" (
    echo [ERROR] Key file path is required
    pause
    exit /b 1
)

if not exist "%KEY_FILE%" (
    echo [ERROR] Key file not found: %KEY_FILE%
    pause
    exit /b 1
)

echo.
echo ========================================
echo Step 1: Uploading Backend Code
echo ========================================
echo.

REM Upload backend directory to EC2
echo Uploading backend files to EC2...
scp -i "%KEY_FILE%" -r backend ubuntu@%EC2_IP%:/tmp/backend-update
if %errorlevel% neq 0 (
    echo [ERROR] Failed to upload files
    echo Make sure:
    echo   1. EC2 IP is correct
    echo   2. Key file has correct permissions
    echo   3. Security group allows SSH from your IP
    pause
    exit /b 1
)

echo [SUCCESS] Files uploaded
echo.

echo ========================================
echo Step 2: Updating Backend on EC2
echo ========================================
echo.

REM Create update script
echo Creating update script...
(
echo #!/bin/bash
echo set -e
echo echo "Stopping backend service..."
echo sudo systemctl stop nyaya-mitra-backend
echo echo "Backing up current backend..."
echo sudo cp -r /opt/nyaya-mitra/backend /opt/nyaya-mitra/backend.backup.$(date +%%Y%%m%%d-%%H%%M%%S^)
echo echo "Updating backend files..."
echo sudo rsync -av --exclude='.venv' --exclude='__pycache__' --exclude='.env' /tmp/backend-update/ /opt/nyaya-mitra/backend/
echo echo "Updating dependencies..."
echo cd /opt/nyaya-mitra/backend
echo source .venv/bin/activate
echo pip install -r requirements.txt
echo echo "Restarting backend service..."
echo sudo systemctl start nyaya-mitra-backend
echo echo "Checking service status..."
echo sleep 3
echo sudo systemctl status nyaya-mitra-backend --no-pager
echo echo "Cleaning up..."
echo rm -rf /tmp/backend-update
echo echo "Update complete!"
) > update-script.sh

REM Upload and execute update script
echo Uploading update script...
scp -i "%KEY_FILE%" update-script.sh ubuntu@%EC2_IP%:/tmp/update-script.sh
if %errorlevel% neq 0 (
    echo [ERROR] Failed to upload update script
    pause
    exit /b 1
)

echo Executing update on EC2...
ssh -i "%KEY_FILE%" ubuntu@%EC2_IP% "chmod +x /tmp/update-script.sh && /tmp/update-script.sh"
if %errorlevel% neq 0 (
    echo [ERROR] Update failed on EC2
    echo Check the error messages above
    pause
    exit /b 1
)

REM Clean up local script
del update-script.sh

echo.
echo ========================================
echo Step 3: Verifying Update
echo ========================================
echo.

echo Testing backend health...
curl -s http://%EC2_IP%/health
if %errorlevel% neq 0 (
    echo [WARN] Health check failed
    echo Backend may still be starting up
) else (
    echo [SUCCESS] Backend is responding
)

echo.
echo ========================================
echo Backend Update Complete!
echo ========================================
echo.
echo Your backend has been updated on EC2.
echo.
echo To view logs:
echo   ssh -i "%KEY_FILE%" ubuntu@%EC2_IP%
echo   sudo journalctl -u nyaya-mitra-backend -f
echo.
echo To check status:
echo   ssh -i "%KEY_FILE%" ubuntu@%EC2_IP%
echo   sudo systemctl status nyaya-mitra-backend
echo.
echo If there are issues, you can rollback:
echo   ssh -i "%KEY_FILE%" ubuntu@%EC2_IP%
echo   sudo systemctl stop nyaya-mitra-backend
echo   sudo rm -rf /opt/nyaya-mitra/backend
echo   sudo mv /opt/nyaya-mitra/backend.backup.YYYYMMDD-HHMMSS /opt/nyaya-mitra/backend
echo   sudo systemctl start nyaya-mitra-backend
echo.
pause
