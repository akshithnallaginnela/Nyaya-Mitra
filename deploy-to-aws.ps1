# Nyaya Mitra AWS Deployment Script
# This script automates the deployment to AWS

param(
    [string]$DBPassword = "",
    [string]$JWTSecret = "",
    [string]$KeyPairName = "nyaya-mitra-key"
)

# Load AWS credentials from separate file
if (Test-Path "aws-credentials.ps1") {
    . .\aws-credentials.ps1
} else {
    Write-Host "[ERROR] aws-credentials.ps1 not found!" -ForegroundColor Red
    Write-Host "Please create aws-credentials.ps1 with your AWS credentials" -ForegroundColor Yellow
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Nyaya Mitra AWS Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Generate secrets if not provided
if ([string]::IsNullOrEmpty($DBPassword)) {
    $DBPassword = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 16 | ForEach-Object {[char]$_})
    Write-Host "[INFO] Generated DB Password: $DBPassword" -ForegroundColor Yellow
}

if ([string]::IsNullOrEmpty($JWTSecret)) {
    $JWTSecret = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
    Write-Host "[INFO] Generated JWT Secret: $JWTSecret" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 1: Verifying AWS Connection..." -ForegroundColor Green
$identity = aws sts get-caller-identity | ConvertFrom-Json
Write-Host "[SUCCESS] Connected as: $($identity.Arn)" -ForegroundColor Green
Write-Host ""

# Save deployment info
$deploymentInfo = @{
    Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    AWSAccount = $identity.Account
    AWSRegion = "us-east-1"
    DBPassword = $DBPassword
    JWTSecret = $JWTSecret
}

$deploymentInfo | ConvertTo-Json | Out-File "deployment-info.json"
Write-Host "[INFO] Deployment info saved to deployment-info.json" -ForegroundColor Yellow
Write-Host ""
