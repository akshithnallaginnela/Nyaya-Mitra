#!/bin/bash
# ============================================
# Nyaya Mitra — Full AWS Deployment Script
# ============================================
# Usage: ./scripts/deploy.sh [environment]
# Example: ./scripts/deploy.sh production
#
# Prerequisites:
#   - AWS CLI configured (aws configure)
#   - Docker installed
#   - Terraform installed
#   - Node.js installed (for frontend build)
# ============================================

set -euo pipefail

# ─── Configuration ───
ENVIRONMENT="${1:-production}"
AWS_REGION="${AWS_REGION:-ap-south-1}"
PROJECT_NAME="nyaya-mitra"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "============================================"
echo "  Nyaya Mitra — AWS Deployment"
echo "  Environment: $ENVIRONMENT"
echo "  Region: $AWS_REGION"
echo "============================================"
echo ""

# ─── Step 1: Validate Prerequisites ───
echo "[1/7] Validating prerequisites..."

command -v aws >/dev/null 2>&1 || { echo "❌ AWS CLI is required. Install: https://aws.amazon.com/cli/"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required. Install: https://docs.docker.com/get-docker/"; exit 1; }
command -v terraform >/dev/null 2>&1 || { echo "❌ Terraform is required. Install: https://terraform.io/downloads"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required. Install: https://nodejs.org/"; exit 1; }

# Verify AWS credentials
aws sts get-caller-identity >/dev/null 2>&1 || { echo "❌ AWS credentials not configured. Run: aws configure"; exit 1; }

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
ECR_REPO="${ECR_REGISTRY}/${PROJECT_NAME}-backend"

echo "  ✅ AWS Account: $AWS_ACCOUNT_ID"
echo "  ✅ ECR Registry: $ECR_REGISTRY"
echo ""

# ─── Step 2: Infrastructure (Terraform) ───
echo "[2/7] Deploying infrastructure with Terraform..."

cd "$ROOT_DIR/infrastructure/terraform"

if [ ! -f "terraform.tfvars" ]; then
    echo "⚠️  terraform.tfvars not found!"
    echo "   Copy terraform.tfvars.example to terraform.tfvars and fill in your values."
    echo "   Then re-run this script."
    exit 1
fi

terraform init -input=false
terraform plan -out=tfplan
terraform apply -auto-approve tfplan
rm -f tfplan

# Get outputs
FRONTEND_BUCKET=$(terraform output -raw frontend_bucket)
CLOUDFRONT_DOMAIN=$(terraform output -raw cloudfront_domain)
ALB_DNS=$(terraform output -raw alb_dns)
CLOUDFRONT_ID=$(aws cloudfront list-distributions --query "DistributionList.Items[?Comment=='Nyaya Mitra CDN'].Id" --output text)

echo "  ✅ Infrastructure deployed"
echo "  Frontend Bucket: $FRONTEND_BUCKET"
echo "  CloudFront: $CLOUDFRONT_DOMAIN"
echo ""

# ─── Step 3: Build & Push Backend Docker Image ───
echo "[3/7] Building backend Docker image..."

cd "$ROOT_DIR/backend"

# Login to ECR
aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$ECR_REGISTRY"

# Build image
COMMIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "latest")
docker build -t "${ECR_REPO}:${COMMIT_SHA}" -t "${ECR_REPO}:latest" .

echo "  ✅ Docker image built"
echo ""

# ─── Step 4: Push to ECR ───
echo "[4/7] Pushing image to ECR..."

docker push "${ECR_REPO}:${COMMIT_SHA}"
docker push "${ECR_REPO}:latest"

echo "  ✅ Image pushed to ECR"
echo ""

# ─── Step 5: Deploy Backend (Update ECS Service) ───
echo "[5/7] Deploying backend to ECS..."

aws ecs update-service \
    --cluster "${PROJECT_NAME}-cluster" \
    --service "${PROJECT_NAME}-backend" \
    --force-new-deployment \
    --region "$AWS_REGION" \
    --no-cli-pager

echo "  ✅ ECS service updated (deploying new tasks...)"
echo ""

# ─── Step 6: Build & Deploy Frontend ───
echo "[6/7] Building and deploying frontend..."

cd "$ROOT_DIR/frontend"

# Set API URL for production build
export VITE_API_URL="https://${CLOUDFRONT_DOMAIN}"

npm ci --production=false
npm run build

# Sync to S3
aws s3 sync dist/ "s3://${FRONTEND_BUCKET}" \
    --delete \
    --cache-control "public, max-age=31536000, immutable" \
    --exclude "index.html" \
    --exclude "*.json"

# Upload index.html with no-cache
aws s3 cp dist/index.html "s3://${FRONTEND_BUCKET}/index.html" \
    --cache-control "no-cache, no-store, must-revalidate"

# Upload manifest/config files with short cache
aws s3 sync dist/ "s3://${FRONTEND_BUCKET}" \
    --include "*.json" \
    --cache-control "public, max-age=60"

echo "  ✅ Frontend deployed to S3"
echo ""

# ─── Step 7: Invalidate CloudFront Cache ───
echo "[7/7] Invalidating CloudFront cache..."

if [ -n "$CLOUDFRONT_ID" ]; then
    aws cloudfront create-invalidation \
        --distribution-id "$CLOUDFRONT_ID" \
        --paths "/*" \
        --no-cli-pager
    echo "  ✅ CloudFront cache invalidated"
else
    echo "  ⚠️  Could not find CloudFront distribution ID. Manual invalidation may be needed."
fi

echo ""
echo "============================================"
echo "  ✅ Deployment Complete!"
echo "============================================"
echo ""
echo "  🌐 Application:  https://${CLOUDFRONT_DOMAIN}"
echo "  🔧 API Backend:  http://${ALB_DNS}"
echo "  📊 CloudWatch:   https://${AWS_REGION}.console.aws.amazon.com/cloudwatch"
echo ""
echo "  ⏳ Note: ECS deployment may take 2-5 minutes to complete."
echo "  Monitor at: https://${AWS_REGION}.console.aws.amazon.com/ecs"
echo "============================================"
