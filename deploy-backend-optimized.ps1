# Optimized Backend Deployment Script
# Excludes .venv, __pycache__, and other unnecessary files

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
$JWT_SECRET = $deploymentInfo.JWTSecret

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deploying Backend to EC2 (Optimized)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "EC2 IP: $EC2_IP" -ForegroundColor Yellow
Write-Host ""

# Step 1: Update system and install dependencies
Write-Host "Step 1: Installing system dependencies..." -ForegroundColor Green
Write-Host "[INFO] This will take 3-5 minutes..." -ForegroundColor Yellow

ssh -i nyaya-mitra-key.pem -o StrictHostKeyChecking=no ubuntu@${EC2_IP} @"
sudo apt update && \
sudo DEBIAN_FRONTEND=noninteractive apt upgrade -y && \
sudo apt install -y python3.11 python3.11-venv python3-pip git postgresql-client nginx && \
sudo mkdir -p /opt/nyaya-mitra && \
sudo chown ubuntu:ubuntu /opt/nyaya-mitra
"@

Write-Host "[SUCCESS] System dependencies installed" -ForegroundColor Green
Write-Host ""

# Step 2: Upload backend code (excluding .venv, __pycache__, etc.)
Write-Host "Step 2: Uploading backend code (excluding virtual env)..." -ForegroundColor Green
Write-Host "[INFO] This will take 2-3 minutes..." -ForegroundColor Yellow

# Use rsync to exclude unnecessary files
ssh -i nyaya-mitra-key.pem ubuntu@${EC2_IP} "mkdir -p /opt/nyaya-mitra/backend"

# Upload using scp with exclusions via tar
cd backend
tar -czf ../backend-deploy.tar.gz --exclude='.venv' --exclude='__pycache__' --exclude='*.pyc' --exclude='.pytest_cache' --exclude='chroma_db' --exclude='generated_documents' .
cd ..

scp -i nyaya-mitra-key.pem backend-deploy.tar.gz ubuntu@${EC2_IP}:/opt/nyaya-mitra/
ssh -i nyaya-mitra-key.pem ubuntu@${EC2_IP} "cd /opt/nyaya-mitra && tar -xzf backend-deploy.tar.gz -C backend && rm backend-deploy.tar.gz"
Remove-Item backend-deploy.tar.gz

Write-Host "[SUCCESS] Backend code uploaded" -ForegroundColor Green
Write-Host ""

# Step 3: Create .env file
Write-Host "Step 3: Creating environment configuration..." -ForegroundColor Green

ssh -i nyaya-mitra-key.pem ubuntu@${EC2_IP} @"
cat > /opt/nyaya-mitra/backend/.env << 'ENVEOF'
# Database Configuration
DATABASE_URL=postgresql://nyayamitra:${DB_PASSWORD}@${DB_ENDPOINT}:5432/nyayamitra

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
ENVEOF
"@

Write-Host "[SUCCESS] Environment configuration created" -ForegroundColor Green
Write-Host ""

# Step 4: Install Python dependencies
Write-Host "Step 4: Installing Python dependencies..." -ForegroundColor Green
Write-Host "[INFO] This will take 5-7 minutes..." -ForegroundColor Yellow

ssh -i nyaya-mitra-key.pem ubuntu@${EC2_IP} @"
cd /opt/nyaya-mitra/backend && \
python3.11 -m venv venv && \
source venv/bin/activate && \
pip install --upgrade pip && \
pip install -r requirements.txt
"@

Write-Host "[SUCCESS] Python dependencies installed" -ForegroundColor Green
Write-Host ""

# Step 5: Download spaCy model
Write-Host "Step 5: Downloading spaCy language model..." -ForegroundColor Green
Write-Host "[INFO] This will take 2-3 minutes..." -ForegroundColor Yellow

ssh -i nyaya-mitra-key.pem ubuntu@${EC2_IP} @"
cd /opt/nyaya-mitra/backend && \
source venv/bin/activate && \
python -m spacy download en_core_web_sm
"@

Write-Host "[SUCCESS] spaCy model downloaded" -ForegroundColor Green
Write-Host ""

# Step 6: Initialize database
Write-Host "Step 6: Initializing database..." -ForegroundColor Green

ssh -i nyaya-mitra-key.pem ubuntu@${EC2_IP} @"
cd /opt/nyaya-mitra/backend && \
source venv/bin/activate && \
python -c 'from database import init_db; init_db()'
"@

Write-Host "[SUCCESS] Database initialized" -ForegroundColor Green
Write-Host ""

# Step 7: Create systemd service
Write-Host "Step 7: Creating systemd service..." -ForegroundColor Green

ssh -i nyaya-mitra-key.pem ubuntu@${EC2_IP} @"
sudo tee /etc/systemd/system/nyaya-mitra-backend.service > /dev/null << 'SERVICEEOF'
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
SERVICEEOF

sudo systemctl daemon-reload && \
sudo systemctl enable nyaya-mitra-backend && \
sudo systemctl start nyaya-mitra-backend
"@

Write-Host "[SUCCESS] Systemd service created and started" -ForegroundColor Green
Write-Host ""

# Step 8: Configure Nginx
Write-Host "Step 8: Configuring Nginx reverse proxy..." -ForegroundColor Green

ssh -i nyaya-mitra-key.pem ubuntu@${EC2_IP} @"
sudo tee /etc/nginx/sites-available/nyaya-mitra > /dev/null << 'NGINXEOF'
server {
    listen 80;
    server_name _;

    client_max_body_size 50M;

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \\\$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \\\$host;
        proxy_cache_bypass \\\$http_upgrade;
        proxy_set_header X-Real-IP \\\$remote_addr;
        proxy_set_header X-Forwarded-For \\\$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \\\$scheme;
    }

    location / {
        root /var/www/nyaya-mitra;
        try_files \\\$uri \\\$uri/ /index.html;
    }
}
NGINXEOF

sudo ln -sf /etc/nginx/sites-available/nyaya-mitra /etc/nginx/sites-enabled/ && \
sudo rm -f /etc/nginx/sites-enabled/default && \
sudo nginx -t && \
sudo systemctl restart nginx
"@

Write-Host "[SUCCESS] Nginx configured" -ForegroundColor Green
Write-Host ""

# Step 9: Check service status
Write-Host "Step 9: Checking service status..." -ForegroundColor Green

ssh -i nyaya-mitra-key.pem ubuntu@${EC2_IP} "sudo systemctl status nyaya-mitra-backend --no-pager"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Backend Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend API: http://${EC2_IP}/api" -ForegroundColor Yellow
Write-Host "Health Check: http://${EC2_IP}/api/health" -ForegroundColor Yellow
Write-Host ""
Write-Host "To check logs: ssh -i nyaya-mitra-key.pem ubuntu@${EC2_IP} 'sudo journalctl -u nyaya-mitra-backend -f'" -ForegroundColor Cyan
Write-Host ""
