@echo off
REM ============================================
REM Nyaya Mitra - AWS Setup & Deploy (Windows)
REM ============================================
REM This script handles EVERYTHING:
REM   1. Checks prerequisites
REM   2. Configures AWS (if needed)
REM   3. Builds Docker image
REM   4. Deploys infrastructure with Terraform
REM   5. Pushes backend to ECR + ECS
REM   6. Deploys frontend to S3 + CloudFront
REM ============================================

setlocal enabledelayedexpansion

echo ============================================
echo   Nyaya Mitra - AWS Setup and Deploy
echo ============================================
echo.

REM ─── Refresh PATH ───
set "PATH=%PATH%;C:\Program Files\Amazon\AWSCLIV2;C:\ProgramData\chocolatey\bin"

REM ─── Step 1: Check prerequisites ───
echo [Step 1/8] Checking prerequisites...

where aws >nul 2>&1
if errorlevel 1 (
    echo ❌ AWS CLI not found. Installing...
    winget install Amazon.AWSCLI --accept-source-agreements --accept-package-agreements
    set "PATH=%PATH%;C:\Program Files\Amazon\AWSCLIV2"
)
echo   ✅ AWS CLI found

where docker >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker not found. Please install Docker Desktop from https://docker.com
    pause
    exit /b 1
)
echo   ✅ Docker found

where terraform >nul 2>&1
if errorlevel 1 (
    echo ❌ Terraform not found. Installing...
    winget install Hashicorp.Terraform --accept-source-agreements --accept-package-agreements
)
echo   ✅ Terraform found

where node >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found. Please install from https://nodejs.org
    pause
    exit /b 1
)
echo   ✅ Node.js found
echo.

REM ─── Step 2: Check AWS credentials ───
echo [Step 2/8] Checking AWS credentials...

aws sts get-caller-identity >nul 2>&1
if errorlevel 1 (
    echo.
    echo ⚠️  AWS credentials not configured!
    echo.
    echo Please enter your AWS credentials:
    echo   - Get them from: AWS Console ^> IAM ^> Users ^> Security Credentials
    echo   - Or create a new user with AdministratorAccess policy
    echo.
    aws configure
    echo.
    
    aws sts get-caller-identity >nul 2>&1
    if errorlevel 1 (
        echo ❌ AWS credential configuration failed. Please try again.
        pause
        exit /b 1
    )
)

for /f "tokens=*" %%i in ('aws sts get-caller-identity --query Account --output text') do set "AWS_ACCOUNT_ID=%%i"
echo   ✅ AWS Account: %AWS_ACCOUNT_ID%
echo.

REM ─── Step 3: Check Docker is running ───
echo [Step 3/8] Checking Docker daemon...

docker info >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Docker Desktop is not running!
    echo    Please start Docker Desktop and wait for it to be ready.
    echo    Then press any key to continue...
    pause >nul
    
    docker info >nul 2>&1
    if errorlevel 1 (
        echo ❌ Docker still not running. Please start Docker Desktop.
        pause
        exit /b 1
    )
)
echo   ✅ Docker is running
echo.

REM ─── Step 4: Setup Terraform variables ───
echo [Step 4/8] Setting up Terraform configuration...

set "TF_DIR=%~dp0..\infrastructure\terraform"

if not exist "%TF_DIR%\terraform.tfvars" (
    echo Creating terraform.tfvars from template...
    
    REM Generate random secrets
    for /f "tokens=*" %%i in ('python -c "import secrets; print(secrets.token_hex(32))"') do set "RANDOM_JWT_SECRET=%%i"
    for /f "tokens=*" %%i in ('python -c "import secrets; print(secrets.token_urlsafe(20))"') do set "RANDOM_DB_PASS=%%i"
    
    (
        echo # Auto-generated Terraform variables
        echo project_name = "nyaya-mitra"
        echo environment  = "production"
        echo aws_region   = "ap-south-1"
        echo domain_name  = "nyayamitra.com"
        echo.
        echo # Database
        echo db_instance_class = "db.t3.micro"
        echo db_name           = "nyaya_mitra"
        echo db_username       = "nyaya_admin"
        echo db_password       = "!RANDOM_DB_PASS!"
        echo.
        echo # ECS
        echo ecs_task_cpu      = "1024"
        echo ecs_task_memory   = "4096"
        echo ecs_desired_count = 1
        echo ecs_max_count     = 4
        echo.
        echo # AI (Amazon Bedrock)
        echo ai_provider      = "bedrock"
        echo bedrock_model_id = "anthropic.claude-3-haiku-20240307-v1:0"
        echo.
        echo # Security
        echo jwt_secret = "!RANDOM_JWT_SECRET!"
    ) > "%TF_DIR%\terraform.tfvars"
    
    echo   ✅ terraform.tfvars created with auto-generated secrets
) else (
    echo   ✅ terraform.tfvars already exists
)
echo.

REM ─── Step 5: Deploy Infrastructure ───
echo [Step 5/8] Deploying AWS infrastructure with Terraform...
echo   (This creates VPC, RDS, ECS, S3, CloudFront, ALB, IAM...)
echo   This takes about 5-10 minutes on first run.
echo.

pushd "%TF_DIR%"

terraform init -input=false
if errorlevel 1 (
    echo ❌ Terraform init failed
    popd
    pause
    exit /b 1
)

terraform apply -auto-approve
if errorlevel 1 (
    echo ❌ Terraform apply failed
    popd
    pause
    exit /b 1
)

REM Capture outputs
for /f "tokens=*" %%i in ('terraform output -raw frontend_bucket') do set "FRONTEND_BUCKET=%%i"
for /f "tokens=*" %%i in ('terraform output -raw cloudfront_domain') do set "CLOUDFRONT_DOMAIN=%%i"
for /f "tokens=*" %%i in ('terraform output -raw alb_dns') do set "ALB_DNS=%%i"
for /f "tokens=*" %%i in ('terraform output -raw ecr_repository_url') do set "ECR_REPO=%%i"
for /f "tokens=*" %%i in ('terraform output -raw opensearch_endpoint') do set "OPENSEARCH_URL=%%i"
for /f "tokens=*" %%i in ('terraform output -raw cognito_user_pool_id') do set "COGNITO_ID=%%i"

popd

echo.
echo   ✅ Infrastructure deployed!
echo   Frontend bucket: %FRONTEND_BUCKET%
echo   CloudFront:      %CLOUDFRONT_DOMAIN%
echo   ALB DNS:         %ALB_DNS%
echo   ECR Repo:        %ECR_REPO%
echo.

REM ─── Step 6: Build and Push Docker Image ───
echo [Step 6/8] Building and pushing backend Docker image...

set "ECR_REGISTRY=%AWS_ACCOUNT_ID%.dkr.ecr.ap-south-1.amazonaws.com"

REM Login to ECR
for /f "tokens=*" %%i in ('aws ecr get-login-password --region ap-south-1') do (
    echo %%i | docker login --username AWS --password-stdin %ECR_REGISTRY%
)

pushd "%~dp0..\backend"

docker build -t "%ECR_REPO%:latest" .
if errorlevel 1 (
    echo ❌ Docker build failed
    popd
    pause
    exit /b 1
)

docker push "%ECR_REPO%:latest"
if errorlevel 1 (
    echo ❌ Docker push failed
    popd
    pause
    exit /b 1
)

popd

echo   ✅ Backend image pushed to ECR
echo.

REM ─── Step 7: Update ECS Service ───
echo [Step 7/8] Deploying backend to ECS Fargate...

aws ecs update-service ^
    --cluster "nyaya-mitra-cluster" ^
    --service "nyaya-mitra-backend" ^
    --force-new-deployment ^
    --region ap-south-1 ^
    --no-cli-pager

echo   ✅ ECS service deploying (takes 2-5 minutes)
echo.

REM ─── Step 8: Deploy Frontend ───
echo [Step 8/8] Building and deploying frontend...

pushd "%~dp0..\frontend"

set "VITE_API_URL=https://%CLOUDFRONT_DOMAIN%"
call npm ci --production=false
call npm run build

if errorlevel 1 (
    echo ❌ Frontend build failed
    popd
    pause
    exit /b 1
)

REM Upload assets with long cache
aws s3 sync dist\ "s3://%FRONTEND_BUCKET%" ^
    --delete ^
    --cache-control "public, max-age=31536000, immutable" ^
    --exclude "index.html" ^
    --exclude "*.json"

REM Upload index.html with no-cache
aws s3 cp dist\index.html "s3://%FRONTEND_BUCKET%/index.html" ^
    --cache-control "no-cache, no-store, must-revalidate"

popd

REM Invalidate CloudFront
for /f "tokens=*" %%i in ('aws cloudfront list-distributions --query "DistributionList.Items[?Comment==''Nyaya Mitra CDN''].Id" --output text') do set "CF_ID=%%i"
if not "%CF_ID%"=="" (
    aws cloudfront create-invalidation --distribution-id "%CF_ID%" --paths "/*" --no-cli-pager >nul 2>&1
)

echo   ✅ Frontend deployed to S3 + CloudFront
echo.

echo ============================================
echo   🎉 DEPLOYMENT COMPLETE!
echo ============================================
echo.
echo   🌐 Your app is live at:
echo      https://%CLOUDFRONT_DOMAIN%
echo.
echo   🔧 Backend API:
echo      http://%ALB_DNS%/health
echo.
echo   🔍 Vector Database (OpenSearch):
echo      https://%OPENSEARCH_URL%
echo.
echo   🔑 Cognito User Pool:
echo      %COGNITO_ID%
echo.
echo   📊 AWS Console:
echo      https://ap-south-1.console.aws.amazon.com/ecs
echo.
echo   ⏳ Note: ECS backend and OpenSearch may take 5-10 more
echo      minutes to become fully healthy and accessible.
echo ============================================
echo.
pause
