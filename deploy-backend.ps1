# Deploy Backend to EC2
# This script deploys the Nyaya Mitra backend to the EC2 instance

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
Write-Host "Deploying Backend to EC2" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "EC2 IP: $EC2_IP" -ForegroundColor Yellow
Write-Host ""

# Create backend setup script
$setupScript = @"
#!/bin/bash
set -e

echo "========================================="
echo "Nyaya Mitra Backend Setup"
echo "========================================="
echo ""

# Update system
echo "Step 1: Updating system..."
sudo apt update
sudo DEBIAN_FRONTEND=noninteractive apt upgrade -y

# Install dependencies
echo "Step 2: Installing dependencies..."
sudo apt install -y python3.11 python3.11-venv python3-pip git postgresql-client nginx

# Create application directory
echo "Step 3: Creating application directory..."
sudo mkdir -p /opt/nyaya-mitra
sudo chown ubuntu:ubuntu /opt/nyaya-mitra

# Upload backend code (will be done separately)
echo "Step 4: Backend code will be uploaded..."

echo ""
echo "========================================="
echo "System setup complete!"
echo "========================================="
"@

$setupScript | Out-File -FilePath setup-ec2.sh -Encoding UTF8

Write-Host "Step 1: Uploading setup script to EC2..." -ForegroundColor Green
scp -i nyaya-mitra-key.pem -o StrictHostKeyChecking=no setup-ec2.sh ubuntu@${EC2_IP}:/tmp/setup-ec2.sh
Write-Host "[SUCCESS] Setup script uploaded" -ForegroundColor Green
Write-Host ""

Write-Host "Step 2: Running setup script on EC2..." -ForegroundColor Green
Write-Host "[INFO] This will take 3-5 minutes..." -ForegroundColor Yellow
ssh -i nyaya-mitra-key.pem -o StrictHostKeyChecking=no ubuntu@${EC2_IP} "chmod +x /tmp/setup-ec2.sh && /tmp/setup-ec2.sh"
Write-Host "[SUCCESS] System setup complete" -ForegroundColor Green
Write-Host ""

Write-Host "Step 3: Uploading backend code..." -ForegroundColor Green
scp -i nyaya-mitra-key.pem -r backend ubuntu@${EC2_IP}:/opt/nyaya-mitra/
Write-Host "[SUCCESS] Backend code uploaded" -ForegroundColor Green
Write-Host ""

# Create .env file
$envContent = @"
# Database Configuration
DATABASE_URL=postgresql://nyaya_admin:${DB_PASSWORD}@${DB_ENDPOINT}:5432/nyaya_mitra

# JWT Configuration
JWT_SECRET=${JWT_SECRET}
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# AI Provider Configuration
AI_PROVIDER=bedrock

# AWS Bedrock Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_KEY}
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0

# Vector Database
VECTOR_DB_TYPE=chroma

# Application Settings
ENVIRONMENT=production
LOG_LEVEL=INFO

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
"@

$envContent | Out-File -FilePath backend-env -Encoding UTF8

Write-Host "Step 4: Uploading environment configuration..." -ForegroundColor Green
scp -i nyaya-mitra-key.pem backend-env ubuntu@${EC2_IP}:/opt/nyaya-mitra/backend/.env
Write-Host "[SUCCESS] Environment configuration uploaded" -ForegroundColor Green
Write-Host ""

# Create backend installation script
$backendInstall = @"
#!/bin/bash
set -e

cd /opt/nyaya-mitra/backend

echo "Installing Python dependencies..."
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Installing spaCy model..."
python -m spacy download en_core_web_sm

echo "Initializing database..."
python3 -c "from database import init_db; init_db()"

echo "Backend installation complete!"
"@

$backendInstall | Out-File -FilePath install-backend.sh -Encoding UTF8

Write-Host "Step 5: Installing backend dependencies..." -ForegroundColor Green
Write-Host "[INFO] This will take 5-10 minutes..." -ForegroundColor Yellow
scp -i nyaya-mitra-key.pem install-backend.sh ubuntu@${EC2_IP}:/tmp/install-backend.sh
ssh -i nyaya-mitra-key.pem ubuntu@${EC2_IP} "chmod +x /tmp/install-backend.sh && /tmp/install-backend.sh"
Write-Host "[SUCCESS] Backend dependencies installed" -ForegroundColor Green
Write-Host ""

# Create systemd service
$systemdService = @"
[Unit]
Description=Nyaya Mitra FastAPI Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/nyaya-mitra/backend
Environment="PATH=/opt/nyaya-mitra/backend/.venv/bin"
ExecStart=/opt/nyaya-mitra/backend/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"@

$systemdService | Out-File -FilePath nyaya-mitra-backend.service -Encoding UTF8

Write-Host "Step 6: Creating systemd service..." -ForegroundColor Green
scp -i nyaya-mitra-key.pem nyaya-mitra-backend.service ubuntu@${EC2_IP}:/tmp/nyaya-mitra-backend.service
ssh -i nyaya-mitra-key.pem ubuntu@${EC2_IP} "sudo mv /tmp/nyaya-mitra-backend.service /etc/systemd/system/ && sudo systemctl daemon-reload && sudo systemctl enable nyaya-mitra-backend && sudo systemctl start nyaya-mitra-backend"
Write-Host "[SUCCESS] Backend service started" -ForegroundColor Green
Write-Host ""

# Create Nginx configuration
$nginxConfig = @"
server {
    listen 80;
    server_name _;

    client_max_body_size 10M;

    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade `$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host `$host;
        proxy_set_header X-Real-IP `$remote_addr;
        proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto `$scheme;
        proxy_cache_bypass `$http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    location /health {
        proxy_pass http://localhost:8000/health;
    }

    location /db-health {
        proxy_pass http://localhost:8000/db-health;
    }

    location /docs {
        proxy_pass http://localhost:8000/docs;
    }

    location /redoc {
        proxy_pass http://localhost:8000/redoc;
    }
}
"@

$nginxConfig | Out-File -FilePath nginx-config -Encoding UTF8

Write-Host "Step 7: Configuring Nginx..." -ForegroundColor Green
scp -i nyaya-mitra-key.pem nginx-config ubuntu@${EC2_IP}:/tmp/nginx-config
ssh -i nyaya-mitra-key.pem ubuntu@${EC2_IP} "sudo mv /tmp/nginx-config /etc/nginx/sites-available/nyaya-mitra && sudo ln -sf /etc/nginx/sites-available/nyaya-mitra /etc/nginx/sites-enabled/ && sudo rm -f /etc/nginx/sites-enabled/default && sudo nginx -t && sudo systemctl restart nginx"
Write-Host "[SUCCESS] Nginx configured" -ForegroundColor Green
Write-Host ""

Write-Host "Step 8: Testing backend..." -ForegroundColor Green
Start-Sleep -Seconds 5
$healthCheck = Invoke-WebRequest -Uri "http://${EC2_IP}/health" -UseBasicParsing
Write-Host "[SUCCESS] Backend is responding: $($healthCheck.Content)" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Backend Deployment Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend URL: http://${EC2_IP}" -ForegroundColor Yellow
Write-Host "API Docs: http://${EC2_IP}/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next: Run .\deploy-frontend.ps1 to deploy the frontend" -ForegroundColor Green
Write-Host ""

# Clean up temporary files
Remove-Item setup-ec2.sh, backend-env, install-backend.sh, nyaya-mitra-backend.service, nginx-config -ErrorAction SilentlyContinue
