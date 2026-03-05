#!/bin/bash
# ============================================
# Nyaya Mitra — Frontend-Only Deploy to S3
# ============================================
# Quick script to rebuild and deploy only the frontend
# Usage: ./scripts/deploy-frontend.sh
# ============================================

set -euo pipefail

AWS_REGION="${AWS_REGION:-ap-south-1}"
PROJECT_NAME="nyaya-mitra"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🚀 Deploying frontend..."

# Get bucket name from Terraform
cd "$ROOT_DIR/infrastructure/terraform"
FRONTEND_BUCKET=$(terraform output -raw frontend_bucket 2>/dev/null)
CLOUDFRONT_DOMAIN=$(terraform output -raw cloudfront_domain 2>/dev/null)

if [ -z "$FRONTEND_BUCKET" ]; then
    echo "❌ Could not get frontend bucket name. Is infrastructure deployed?"
    exit 1
fi

# Build frontend
cd "$ROOT_DIR/frontend"
export VITE_API_URL="https://${CLOUDFRONT_DOMAIN}"
npm ci --production=false
npm run build

# Deploy to S3
echo "📦 Syncing to S3..."
aws s3 sync dist/ "s3://${FRONTEND_BUCKET}" \
    --delete \
    --cache-control "public, max-age=31536000, immutable" \
    --exclude "index.html" \
    --exclude "*.json"

aws s3 cp dist/index.html "s3://${FRONTEND_BUCKET}/index.html" \
    --cache-control "no-cache, no-store, must-revalidate"

# Invalidate CloudFront
CLOUDFRONT_ID=$(aws cloudfront list-distributions \
    --query "DistributionList.Items[?Comment=='Nyaya Mitra CDN'].Id" \
    --output text)

if [ -n "$CLOUDFRONT_ID" ]; then
    echo "🔄 Invalidating CloudFront cache..."
    aws cloudfront create-invalidation \
        --distribution-id "$CLOUDFRONT_ID" \
        --paths "/*" \
        --no-cli-pager
fi

echo ""
echo "✅ Frontend deployed!"
echo "🌐 https://${CLOUDFRONT_DOMAIN}"
