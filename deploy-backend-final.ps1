# Final Backend Deployment Script - Simplified and Reliable
# Creates files locally and uploads them to avoid SSH here-doc issues

# Load AWS credentials
if (Test-Path "aws-credentials.ps1") {
    . .\aws-credentials.ps1
} else {
    Write-Host "[ERROR] aws-credentials.ps1 not found!" -ForegroundColor Red
    exit 1
}

$AWS_ACCESS_KEY = $env:AWS_ACCESS_KEY_ID
$AWS_SECRET_KEY = $env:AWS_SECRET_ACCESS_KEY

# Load deployment info
$deploymentInfo = Get-Content deployment-info.json | ConvertFrom-Json
$EC2_IP = $deploymentInfo.EC2PublicIP
$DB_ENDPOINT = $deploymentInfo.RDSEndpoint
$DB_PASSWORD = $deploymentInfo.DBPassword
$DB_USERNAME = $deploymentInfo.DBUsername
$DB_NAME = $deploymentInfo.DBName
$JWT_SECRET = $deploymentInfo.JWTSecret

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Final Backend Deployment to EC2" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "EC2 IP: $EC2_IP" -ForegroundColor Yellow
Write-Host "Target: http://${EC2_IP}" -ForegroundColor Yellow
Write-Host ""

# Create temporary .env file locally
Write-Host "Creating environment file..." -ForegroundColor Green
$envContent = @"
# Database Configuration
DATABASE_URL=postgresql://${DB_USERNAME}:${DB_PASSWORD}@${DB_ENDPOINT}:5432/${DB_NAME}

# AWS Bedrock Configuration
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_KEY}
AWS_DEFAULT_REGION=us-east-1

# Security
JWT_SECRET_KEY=${JWT_SECRET}
SECRET_KEY=${JWT_SECRET}

# Application Settings
ENVIRONMENT=production
DEBUG=False
ALLOWED_HOSTS=*
CORS_ORIGINS=*
"@

$envContent | Out-File -FilePath "backend/.env.production" -Encoding UTF8 -NoNewline

# Create systemd service file locally
$serviceContent = @"
[Unit]
Description=Nyaya Mitra Backend API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/nyaya-mitra/backend
Environment='PATH=/opt/nyaya-mitra/backend/venv/bin'
EnvironmentFile=/opt/nyaya-mitra/backend/.env
ExecStart=/opt/nyaya-mitra/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"@

$serviceContent | Out-File -FilePath "nyaya-mitra-backend.service" -Encoding UTF8 -NoNewline

# Create nginx config locally
$nginxContent = @"
server {
    listen 80;
    server_name _;

    client_max_body_size 50M;

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade `$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host `$host;
        proxy_cache_bypass `$http_upgrade;
        proxy_set_header X-Real-IP `$remote_addr;
        proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto `$scheme;
    }

    location / {
        root /var/www/nyaya-mitra;
        try_files `$uri `$uri/ /index.html;
    }
}
"@

$nginxContent | Out-File -FilePath "nyaya-mitra-nginx.conf" -Encoding UTF8 -NoNewline

Write-Host "[SUCCESS] Configuration files created" -ForegroundColor Green
Write-Host ""

# Step 1: Ensure system dependencies
Write-Host "Step 1: Checking system dependencies..." -ForegroundColor Green
ssh -i nyaya-mitra-key.pem -o StrictHostKeyChecking=no ubuntu@${EC2_IP} "sudo apt update && sudo apt install -y python3.11 python3.11-venv python3-pip nginx postgresql-client && sudo mkdir -p /opt/nyaya-mitra && sudo chown ubuntu:ubuntu /opt/nyaya-mitra"
Write-Host "[SUCCESS] System ready" -ForegroundColor Green
Write-Host ""

# Step 2: Upload backend code
Write-Host "Step 2: Uploading backend code..." -ForegroundColor Green
cd backend
tar -czf ../backend-deploy.tar.gz --exclude='.venv' --exclude='__pycache__' --exclude='*.pyc' --exclude='.pytest_cache' --exclude='chroma_db' --exclude='generated_documents' .
cd ..

ssh -i nyaya-mitra-key.pem ubuntu@${EC2_IP} "mkdir -p /opt/nyaya-mitra/backend"
scp -i nyaya-mitra-key.pem backend-deploy.tar.gz ubuntu@${EC2_IP}:/opt/nyaya-mitra/
ssh -i nyaya-mitra-key.pem ubuntu@${EC2_IP} "cd /opt/nyaya-mitra && tar -xzf backend-deploy.tar.gz -C backend && rm backend-deploy.tar.gz"
Remove-Item backend-deploy.tar.gz

Write-Host "[SUCCESS] Code uploaded" -ForegroundColor Green
Write-Host ""

# Step 3: Upload configuration files
Write-Host "Step 3: Uploading configuration..." -ForegroundColor Green
scp -i nyaya-mitra-key.pem backend/.env.production ubuntu@${EC2_IP}:/opt/nyaya-mitra/backend/.env
scp -i nyaya-mitra-key.pem nyaya-mitra-backend.service ubuntu@${EC2_IP}:/tmp/
scp -i nyaya-mitra-key.pem nyaya-mitra-nginx.conf ubuntu@${EC2_IP}:/tmp/

# Clean up local files
Remove-Item backend/.env.production
Remove-Item nyaya-mitra-backend.service
Remove-Item nyaya-mitra-nginx.conf

Write-Host "[SUCCESS] Configuration uploaded" -ForegroundColor Green
Write-Host ""

# Step 4: Install Python dependencies
Write-Host "Step 4: Installing Python dependencies..." -ForegroundColor Green
Write-Host "[INFO] This takes 5-7 minutes..." -ForegroundColor Yellow
ssh -i nyaya-mitra-key.pem ubuntu@${EC2_IP} "cd /opt/nyaya-mitra/backend && python3.11 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"
Write-Host "[SUCCESS] Dependencies installed" -ForegroundColor Green
Write-Host ""

# Step 5: Download spaCy model
Write-Host "Step 5: Downloading spaCy model..." -ForegroundColor Green
ssh -i nyaya-mitra-key.pem ubuntu@${EC2_IP} "cd /opt/nyaya-mitra/backend && source venv/bin/activate && python -m spacy download en_core_web_sm"
Write-Host "[SUCCESS] spaCy model ready" -ForegroundColor Green
Write-Host ""

# Step 6: Initialize database
Write-Host "Step 6: Initializing database..." -ForegroundColor Green
ssh -i nyaya-mitra-key.pem ubuntu@${EC2_IP} "cd /opt/nyaya-mitra/backend && source venv/bin/activate && python -c 'from database import init_db; init_db()'"
Write-Host "[SUCCESS] Database initialized" -ForegroundColor Green
Write-Host ""

# Step 7: Setup systemd service
Write-Host "Step 7: Setting up backend service..." -ForegroundColor Green
ssh -i nyaya-mitra-key.pem ubuntu@${EC2_IP} "sudo mv /tmp/nyaya-mitra-backend.service /etc/systemd/system/ && sudo systemctl daemon-reload && sudo systemctl enable nyaya-mitra-backend && sudo systemctl restart nyaya-mitra-backend"
Write-Host "[SUCCESS] Backend service running" -ForegroundColor Green
Write-Host ""

# Step 8: Configure Nginx
Write-Host "Step 8: Configuring Nginx..." -ForegroundColor Green
ssh -i nyaya-mitra-key.pem ubuntu@${EC2_IP} "sudo mv /tmp/nyaya-mitra-nginx.conf /etc/nginx/sites-available/nyaya-mitra && sudo ln -sf /etc/nginx/sites-available/nyaya-mitra /etc/nginx/sites-enabled/ && sudo rm -f /etc/nginx/sites-enabled/default && sudo nginx -t && sudo systemctl restart nginx"
Write-Host "[SUCCESS] Nginx configured" -ForegroundColor Green
Write-Host ""

# Step 9: Verify deployment
Write-Host "Step 9: Verifying deployment..." -ForegroundColor Green
Start-Sleep -Seconds 5
ssh -i nyaya-mitra-key.pem ubuntu@${EC2_IP} "sudo systemctl status nyaya-mitra-backend --no-pager | head -20"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Backend Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend API: http://${EC2_IP}/api" -ForegroundColor Yellow
Write-Host "Health Check: http://${EC2_IP}/api/health" -ForegroundColor Yellow
Write-Host ""
Write-Host "Testing health endpoint..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://${EC2_IP}/api/health" -TimeoutSec 10
    Write-Host "[SUCCESS] Backend is responding!" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor White
} catch {
    Write-Host "[WARNING] Health check failed - backend may still be starting" -ForegroundColor Yellow
    Write-Host "Check logs: ssh -i nyaya-mitra-key.pem ubuntu@${EC2_IP} 'sudo journalctl -u nyaya-mitra-backend -n 50'" -ForegroundColor Cyan
}
Write-Host ""
