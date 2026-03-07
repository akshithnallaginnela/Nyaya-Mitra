# Simple Backend Deployment Script
# Runs commands directly via SSH to avoid line ending issues

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

# Step 2: Upload backend code
Write-Host "Step 2: Uploading backend code..." -ForegroundColor Green
scp -i nyaya-mitra-key.pem -r backend ubuntu@${EC2_IP}:/opt/nyaya-mitra/
Write-Host "[SUCCESS] Backend code uploaded" -ForegroundColor Green
Write-Host ""

# Step 3: Create .env file
Write-Host "Step 3: Creating environment configuration..." -ForegroundColor Green

$envContent = @"
DATABASE_URL=postgresql://nyaya_admin:${DB_PASSWORD}@${DB_ENDPOINT}:5432/nyaya_mitra
JWT_SECRET=${JWT_SECRET}
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
AI_PROVIDER=bedrock
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_KEY}
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
VECTOR_DB_TYPE=chroma
ENVIRONMENT=production
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
"@

$envContent | Out-File -FilePath backend-env -Encoding UTF8 -NoNewline
scp -i nyaya-mitra-key.pem backend-env ubuntu@${EC2_IP}:/opt/nyaya-mitra/backend/.env
Remove-Item backend-env

Write-Host "[SUCCESS] Environment configuration uploaded" -ForegroundColor Green
Write-Host ""

# Step 4: Install Python dependencies
Write-Host "Step 4: Installing Python dependencies..." -ForegroundColor Green
Write-Host "[INFO] This will take 5-10 minutes..." -ForegroundColor Yellow

ssh -i nyaya-mitra-key.pem ubuntu@${EC2_IP} @"
cd /opt/nyaya-mitra/backend && \
python3.11 -m venv .venv && \
source .venv/bin/activate && \
pip install --upgrade pip && \
pip install -r requirements.txt && \
python -m spacy download en_core_web_sm
"@

Write-Host "[SUCCESS] Python dependencies installed" -ForegroundColor Green
Write-Host ""

# Step 5: Initialize database
Write-Host "Step 5: Initializing database..." -ForegroundColor Green

ssh -i nyaya-mitra-key.pem ubuntu@${EC2_IP} @"
cd /opt/nyaya-mitra/backend && \
source .venv/bin/activate && \
python3 -c 'from database import init_db; init_db()'
"@

Write-Host "[SUCCESS] Database initialized" -ForegroundColor Green
Write-Host ""

# Step 6: Create systemd service
Write-Host "Step 6: Creating systemd service..." -ForegroundColor Green

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

$systemdService | Out-File -FilePath nyaya-mitra-backend.service -Encoding UTF8 -NoNewline
scp -i nyaya-mitra-key.pem nyaya-mitra-backend.service ubuntu@${EC2_IP}:/tmp/nyaya-mitra-backend.service
Remove-Item nyaya-mitra-backend.service

ssh -i nyaya-mitra-key.pem ubuntu@${EC2_IP} @"
sudo mv /tmp/nyaya-mitra-backend.service /etc/systemd/system/ && \
sudo systemctl daemon-reload && \
sudo systemctl enable nyaya-mitra-backend && \
sudo systemctl start nyaya-mitra-backend
"@

Write-Host "[SUCCESS] Backend service started" -ForegroundColor Green
Write-Host ""

# Step 7: Configure Nginx
Write-Host "Step 7: Configuring Nginx..." -ForegroundColor Green

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

$nginxConfig | Out-File -FilePath nginx-config -Encoding UTF8 -NoNewline
scp -i nyaya-mitra-key.pem nginx-config ubuntu@${EC2_IP}:/tmp/nginx-config
Remove-Item nginx-config

ssh -i nyaya-mitra-key.pem ubuntu@${EC2_IP} @"
sudo mv /tmp/nginx-config /etc/nginx/sites-available/nyaya-mitra && \
sudo ln -sf /etc/nginx/sites-available/nyaya-mitra /etc/nginx/sites-enabled/ && \
sudo rm -f /etc/nginx/sites-enabled/default && \
sudo nginx -t && \
sudo systemctl restart nginx
"@

Write-Host "[SUCCESS] Nginx configured" -ForegroundColor Green
Write-Host ""

# Step 8: Test backend
Write-Host "Step 8: Testing backend..." -ForegroundColor Green
Start-Sleep -Seconds 5

try {
    $healthCheck = Invoke-WebRequest -Uri "http://${EC2_IP}/health" -UseBasicParsing
    Write-Host "[SUCCESS] Backend is responding!" -ForegroundColor Green
    Write-Host "Response: $($healthCheck.Content)" -ForegroundColor White
} catch {
    Write-Host "[WARNING] Backend health check failed, but service may still be starting..." -ForegroundColor Yellow
    Write-Host "Check logs with: ssh -i nyaya-mitra-key.pem ubuntu@${EC2_IP} 'sudo journalctl -u nyaya-mitra-backend -n 50'" -ForegroundColor Yellow
}

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
