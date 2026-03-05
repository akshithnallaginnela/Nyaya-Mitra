@echo off
REM ============================================
REM Nyaya Mitra - AWS Deployment Script (Windows)
REM ============================================
REM Usage: scripts\deploy.bat [environment]
REM Example: scripts\deploy.bat production
REM
REM Prerequisites:
REM   - AWS CLI configured (aws configure)
REM   - Docker Desktop running
REM   - Terraform installed
REM   - Node.js installed
REM ============================================

setlocal enabledelayedexpansion

set "ENVIRONMENT=%~1"
if "%ENVIRONMENT%"=="" set "ENVIRONMENT=production"
set "AWS_REGION=ap-south-1"
set "PROJECT_NAME=nyaya-mitra"

echo ============================================
echo   Nyaya Mitra — AWS Deployment (Windows)
echo   Environment: %ENVIRONMENT%
echo   Region: %AWS_REGION%
echo ============================================
echo.

REM ─── Step 1: Validate Prerequisites ───
echo [1/7] Validating prerequisites...

where aws >nul 2>&1
if errorlevel 1 (
    echo ❌ AWS CLI is required. Install: https://aws.amazon.com/cli/
    pause
    exit /b 1
)

where docker >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is required. Install: https://docs.docker.com/desktop/windows/
    pause
    exit /b 1
)

where terraform >nul 2>&1
if errorlevel 1 (
    echo ❌ Terraform is required. Install: https://terraform.io/downloads
    pause
    exit /b 1
)

where node >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is required. Install: https://nodejs.org/
    pause
    exit /b 1
)

REM Get AWS Account ID
for /f "tokens=*" %%i in ('aws sts get-caller-identity --query Account --output text 2^>nul') do set "AWS_ACCOUNT_ID=%%i"
if "%AWS_ACCOUNT_ID%"=="" (
    echo ❌ AWS credentials not configured. Run: aws configure
    pause
    exit /b 1
)

set "ECR_REGISTRY=%AWS_ACCOUNT_ID%.dkr.ecr.%AWS_REGION%.amazonaws.com"
set "ECR_REPO=%ECR_REGISTRY%/%PROJECT_NAME%-backend"

echo   ✅ AWS Account: %AWS_ACCOUNT_ID%
echo   ✅ ECR Registry: %ECR_REGISTRY%
echo.

REM ─── Step 2: Infrastructure (Terraform) ───
echo [2/7] Deploying infrastructure with Terraform...

pushd infrastructure\terraform

if not exist "terraform.tfvars" (
    echo ⚠️  terraform.tfvars not found!
    echo    Copy terraform.tfvars.example to terraform.tfvars and fill in your values.
    popd
    pause
    exit /b 1
)

terraform init -input=false
if errorlevel 1 (
    echo ❌ Terraform init failed
    popd
    pause
    exit /b 1
)

terraform plan -out=tfplan
if errorlevel 1 (
    echo ❌ Terraform plan failed
    popd
    pause
    exit /b 1
)

terraform apply -auto-approve tfplan
if errorlevel 1 (
    echo ❌ Terraform apply failed
    popd
    pause
    exit /b 1
)

del /f tfplan 2>nul

REM Get outputs
for /f "tokens=*" %%i in ('terraform output -raw frontend_bucket') do set "FRONTEND_BUCKET=%%i"
for /f "tokens=*" %%i in ('terraform output -raw cloudfront_domain') do set "CLOUDFRONT_DOMAIN=%%i"
for /f "tokens=*" %%i in ('terraform output -raw alb_dns') do set "ALB_DNS=%%i"

popd

echo   ✅ Infrastructure deployed
echo   Frontend Bucket: %FRONTEND_BUCKET%
echo   CloudFront: %CLOUDFRONT_DOMAIN%
echo.

REM ─── Step 3: Build Backend Docker Image ───
echo [3/7] Building backend Docker image...

REM Login to ECR
for /f "tokens=*" %%i in ('aws ecr get-login-password --region %AWS_REGION%') do (
    echo %%i | docker login --username AWS --password-stdin %ECR_REGISTRY%
)

pushd backend

for /f "tokens=*" %%i in ('git rev-parse --short HEAD 2^>nul') do set "COMMIT_SHA=%%i"
if "%COMMIT_SHA%"=="" set "COMMIT_SHA=latest"

docker build -t "%ECR_REPO%:%COMMIT_SHA%" -t "%ECR_REPO%:latest" .
if errorlevel 1 (
    echo ❌ Docker build failed
    popd
    pause
    exit /b 1
)

popd

echo   ✅ Docker image built
echo.

REM ─── Step 4: Push to ECR ───
echo [4/7] Pushing image to ECR...

docker push "%ECR_REPO%:%COMMIT_SHA%"
docker push "%ECR_REPO%:latest"

echo   ✅ Image pushed to ECR
echo.

REM ─── Step 5: Deploy Backend (Update ECS) ───
echo [5/7] Deploying backend to ECS...

aws ecs update-service ^
    --cluster "%PROJECT_NAME%-cluster" ^
    --service "%PROJECT_NAME%-backend" ^
    --force-new-deployment ^
    --region "%AWS_REGION%" ^
    --no-cli-pager

echo   ✅ ECS service updated
echo.

REM ─── Step 6: Build & Deploy Frontend ───
echo [6/7] Building and deploying frontend...

pushd frontend

set "VITE_API_URL=https://%CLOUDFRONT_DOMAIN%"
call npm ci --production=false
call npm run build

REM Upload to S3
aws s3 sync dist\ "s3://%FRONTEND_BUCKET%" ^
    --delete ^
    --cache-control "public, max-age=31536000, immutable" ^
    --exclude "index.html" ^
    --exclude "*.json"

aws s3 cp dist\index.html "s3://%FRONTEND_BUCKET%/index.html" ^
    --cache-control "no-cache, no-store, must-revalidate"

popd

echo   ✅ Frontend deployed to S3
echo.

REM ─── Step 7: Invalidate CloudFront Cache ───
echo [7/7] Invalidating CloudFront cache...

for /f "tokens=*" %%i in ('aws cloudfront list-distributions --query "DistributionList.Items[?Comment==''Nyaya Mitra CDN''].Id" --output text') do set "CLOUDFRONT_ID=%%i"

if not "%CLOUDFRONT_ID%"=="" (
    aws cloudfront create-invalidation ^
        --distribution-id "%CLOUDFRONT_ID%" ^
        --paths "/*" ^
        --no-cli-pager
    echo   ✅ CloudFront cache invalidated
) else (
    echo   ⚠️ Could not find CloudFront distribution ID
)

echo.
echo ============================================
echo   ✅ Deployment Complete!
echo ============================================
echo.
echo   🌐 Application:  https://%CLOUDFRONT_DOMAIN%
echo   🔧 API Backend:  http://%ALB_DNS%
echo.
echo   ⏳ ECS deployment may take 2-5 minutes.
echo ============================================
echo.
pause
