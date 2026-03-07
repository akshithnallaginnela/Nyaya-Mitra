# Deploy Frontend to S3 and CloudFront

# Load AWS credentials from separate file
if (Test-Path "aws-credentials.ps1") {
    . .\aws-credentials.ps1
} else {
    Write-Host "[ERROR] aws-credentials.ps1 not found!" -ForegroundColor Red
    Write-Host "Please create aws-credentials.ps1 with your AWS credentials" -ForegroundColor Yellow
    exit 1
}

# Load deployment info
$deploymentInfo = Get-Content deployment-info.json | ConvertFrom-Json
$EC2_IP = $deploymentInfo.EC2PublicIP

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deploying Frontend to AWS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Build frontend
Write-Host "Step 1: Building frontend..." -ForegroundColor Green
cd frontend

# Create production environment file
$envProd = "VITE_API_URL=http://$EC2_IP"
$envProd | Out-File -FilePath .env.production -Encoding UTF8

# Install dependencies and build
Write-Host "[INFO] Installing dependencies..." -ForegroundColor Yellow
npm install

Write-Host "[INFO] Building for production..." -ForegroundColor Yellow
npm run build

Write-Host "[SUCCESS] Frontend built successfully" -ForegroundColor Green
Write-Host ""

cd ..

# Step 2: Create S3 bucket
Write-Host "Step 2: Creating S3 bucket..." -ForegroundColor Green
$bucketName = "nyaya-mitra-frontend-$(Get-Date -Format 'yyyyMMddHHmmss')"

aws s3 mb s3://$bucketName --region us-east-1

Write-Host "[SUCCESS] S3 bucket created: $bucketName" -ForegroundColor Green
Write-Host ""

# Step 3: Configure bucket for static website hosting
Write-Host "Step 3: Configuring static website hosting..." -ForegroundColor Green

$websiteConfig = @"
{
    "IndexDocument": {
        "Suffix": "index.html"
    },
    "ErrorDocument": {
        "Key": "index.html"
    }
}
"@

$websiteConfig | Out-File -FilePath website-config.json -Encoding UTF8

aws s3api put-bucket-website `
    --bucket $bucketName `
    --website-configuration file://website-config.json `
    --region us-east-1

Write-Host "[SUCCESS] Static website hosting configured" -ForegroundColor Green
Write-Host ""

# Step 4: Set bucket policy for public access
Write-Host "Step 4: Setting bucket policy..." -ForegroundColor Green

# First, disable block public access
aws s3api put-public-access-block `
    --bucket $bucketName `
    --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false" `
    --region us-east-1

$bucketPolicy = @"
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$bucketName/*"
        }
    ]
}
"@

$bucketPolicy | Out-File -FilePath bucket-policy.json -Encoding UTF8

aws s3api put-bucket-policy `
    --bucket $bucketName `
    --policy file://bucket-policy.json `
    --region us-east-1

Write-Host "[SUCCESS] Bucket policy set" -ForegroundColor Green
Write-Host ""

# Step 5: Upload files
Write-Host "Step 5: Uploading frontend files..." -ForegroundColor Green

aws s3 sync frontend/dist/ s3://$bucketName/ --delete --region us-east-1

# Set cache headers
aws s3 sync frontend/dist/ s3://$bucketName/ `
    --exclude "index.html" `
    --cache-control "public, max-age=31536000, immutable" `
    --region us-east-1

aws s3 cp frontend/dist/index.html s3://$bucketName/index.html `
    --cache-control "no-cache, no-store, must-revalidate" `
    --region us-east-1

Write-Host "[SUCCESS] Files uploaded" -ForegroundColor Green
Write-Host ""

# Step 6: Create CloudFront distribution
Write-Host "Step 6: Creating CloudFront distribution..." -ForegroundColor Green
Write-Host "[INFO] This may take 10-15 minutes..." -ForegroundColor Yellow

$s3DomainName = "$bucketName.s3.us-east-1.amazonaws.com"

$distributionConfig = @"
{
    "CallerReference": "nyaya-mitra-$(Get-Date -Format 'yyyyMMddHHmmss')",
    "Comment": "Nyaya Mitra Frontend Distribution",
    "Enabled": true,
    "DefaultRootObject": "index.html",
    "Origins": {
        "Quantity": 1,
        "Items": [
            {
                "Id": "S3-$bucketName",
                "DomainName": "$s3DomainName",
                "S3OriginConfig": {
                    "OriginAccessIdentity": ""
                }
            }
        ]
    },
    "DefaultCacheBehavior": {
        "TargetOriginId": "S3-$bucketName",
        "ViewerProtocolPolicy": "redirect-to-https",
        "AllowedMethods": {
            "Quantity": 2,
            "Items": ["GET", "HEAD"],
            "CachedMethods": {
                "Quantity": 2,
                "Items": ["GET", "HEAD"]
            }
        },
        "ForwardedValues": {
            "QueryString": false,
            "Cookies": {
                "Forward": "none"
            }
        },
        "MinTTL": 0,
        "DefaultTTL": 86400,
        "MaxTTL": 31536000,
        "Compress": true
    },
    "CustomErrorResponses": {
        "Quantity": 2,
        "Items": [
            {
                "ErrorCode": 403,
                "ResponsePagePath": "/index.html",
                "ResponseCode": "200",
                "ErrorCachingMinTTL": 300
            },
            {
                "ErrorCode": 404,
                "ResponsePagePath": "/index.html",
                "ResponseCode": "200",
                "ErrorCachingMinTTL": 300
            }
        ]
    }
}
"@

$distributionConfig | Out-File -FilePath distribution-config.json -Encoding UTF8

$distribution = aws cloudfront create-distribution `
    --distribution-config file://distribution-config.json `
    --region us-east-1 | ConvertFrom-Json

$distributionId = $distribution.Distribution.Id
$cloudfrontUrl = $distribution.Distribution.DomainName

Write-Host "[SUCCESS] CloudFront distribution created" -ForegroundColor Green
Write-Host "Distribution ID: $distributionId" -ForegroundColor Yellow
Write-Host "CloudFront URL: https://$cloudfrontUrl" -ForegroundColor Yellow
Write-Host ""

# Update deployment info
$deploymentInfo.S3Bucket = $bucketName
$deploymentInfo.CloudFrontDistributionId = $distributionId
$deploymentInfo.CloudFrontURL = "https://$cloudfrontUrl"
$deploymentInfo.S3WebsiteURL = "http://$bucketName.s3-website-us-east-1.amazonaws.com"
$deploymentInfo | ConvertTo-Json | Out-File deployment-info.json

# Update backend CORS
Write-Host "Step 7: Updating backend CORS configuration..." -ForegroundColor Green

$newCors = "CORS_ORIGINS=https://$cloudfrontUrl,http://$bucketName.s3-website-us-east-1.amazonaws.com,http://localhost:3000"

ssh -i nyaya-mitra-key.pem ubuntu@$EC2_IP "sed -i 's|CORS_ORIGINS=.*|$newCors|' /opt/nyaya-mitra/backend/.env && sudo systemctl restart nyaya-mitra-backend"

Write-Host "[SUCCESS] Backend CORS updated" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Frontend Deployment Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "S3 Website URL: http://$bucketName.s3-website-us-east-1.amazonaws.com" -ForegroundColor Yellow
Write-Host "CloudFront URL: https://$cloudfrontUrl" -ForegroundColor Yellow
Write-Host ""
Write-Host "[INFO] CloudFront distribution is being deployed (10-15 minutes)" -ForegroundColor Yellow
Write-Host "[INFO] You can access the site via S3 URL immediately" -ForegroundColor Yellow
Write-Host "[INFO] CloudFront URL will be available once deployment completes" -ForegroundColor Yellow
Write-Host ""

# Clean up temporary files
Remove-Item website-config.json, bucket-policy.json, distribution-config.json -ErrorAction SilentlyContinue
"@
