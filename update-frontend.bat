@echo off
REM Frontend Update Script for Nyaya Mitra
REM Use this to rebuild and redeploy frontend after changes

echo ========================================
echo Nyaya Mitra Frontend Update Script
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "frontend\package.json" (
    echo [ERROR] frontend\package.json not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

REM Get S3 bucket name
set /p BUCKET_NAME="Enter your S3 bucket name: "
if "%BUCKET_NAME%"=="" (
    echo [ERROR] Bucket name is required
    pause
    exit /b 1
)

REM Get CloudFront distribution ID (optional)
set /p DIST_ID="Enter CloudFront distribution ID (optional, press Enter to skip): "

echo.
echo ========================================
echo Step 1: Building Frontend
echo ========================================
echo.

cd frontend

REM Install dependencies (in case of updates)
echo Installing dependencies...
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] npm install failed
    cd ..
    pause
    exit /b 1
)

REM Build for production
echo Building for production...
call npm run build
if %errorlevel% neq 0 (
    echo [ERROR] Build failed
    cd ..
    pause
    exit /b 1
)

echo [SUCCESS] Build completed
echo.

echo ========================================
echo Step 2: Uploading to S3
echo ========================================
echo.

REM Upload to S3
echo Uploading files to S3...
aws s3 sync dist/ s3://%BUCKET_NAME%/ --delete
if %errorlevel% neq 0 (
    echo [ERROR] S3 upload failed
    echo Make sure AWS CLI is configured correctly
    cd ..
    pause
    exit /b 1
)

echo [SUCCESS] Files uploaded to S3
echo.

REM Set cache headers for static assets
echo Setting cache headers...
aws s3 sync dist/ s3://%BUCKET_NAME%/ --exclude "index.html" --cache-control "public, max-age=31536000, immutable"
aws s3 cp dist/index.html s3://%BUCKET_NAME%/index.html --cache-control "no-cache, no-store, must-revalidate"

echo [SUCCESS] Cache headers set
echo.

REM Invalidate CloudFront cache if distribution ID provided
if not "%DIST_ID%"=="" (
    echo ========================================
    echo Step 3: Invalidating CloudFront Cache
    echo ========================================
    echo.
    
    echo Creating CloudFront invalidation...
    aws cloudfront create-invalidation --distribution-id %DIST_ID% --paths "/*"
    if %errorlevel% neq 0 (
        echo [WARN] CloudFront invalidation failed
        echo You may need to wait or manually invalidate the cache
    ) else (
        echo [SUCCESS] CloudFront cache invalidated
    )
    echo.
)

cd ..

echo ========================================
echo Frontend Update Complete!
echo ========================================
echo.
echo Your frontend has been updated and deployed.
echo.
if not "%DIST_ID%"=="" (
    echo CloudFront cache has been invalidated.
    echo Changes may take 5-10 minutes to propagate.
) else (
    echo Note: CloudFront cache was not invalidated.
    echo Changes may take up to 24 hours to appear.
    echo To invalidate manually:
    echo   aws cloudfront create-invalidation --distribution-id YOUR_ID --paths "/*"
)
echo.
echo Test your changes at:
echo   https://%BUCKET_NAME%.s3-website-us-east-1.amazonaws.com
if not "%DIST_ID%"=="" (
    echo   or your CloudFront URL
)
echo.
pause
