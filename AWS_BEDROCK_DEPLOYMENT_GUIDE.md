# AWS Deployment Guide - Nyaya Mitra (Bedrock Edition)

## Overview

This guide will help you deploy Nyaya Mitra on AWS using **AWS Bedrock** for AI (Claude 3 Haiku). This is significantly more cost-effective than running Ollama on EC2.

## Architecture

```
┌─────────────────┐
│   CloudFront    │ ← Frontend (S3 + CDN)
└────────┬────────┘
         │
┌────────▼────────┐
│  EC2 Instance   │ ← Backend API (FastAPI)
│  (t3.small)     │ ← No Ollama needed!
└────────┬────────┘
         │
    ┌────▼────┐
    │ Bedrock │ ← AI (Claude 3 Haiku)
    └─────────┘
         │
┌────────▼────────┐
│  RDS PostgreSQL │ ← Database
│  (db.t3.micro)  │
└─────────────────┘
```

## Cost Estimate with $200 Credits

**Monthly Costs:**
- EC2 t3.small (24/7): ~$15/month (vs $60 for t3.large with Ollama)
- RDS db.t3.micro: $15/month (free tier eligible)
- S3 + CloudFront: ~$5/month (mostly free tier)
- Bedrock (Claude 3 Haiku): ~$10-20/month for moderate usage
- **Total: ~$45-55/month**

**Your $200 credits will last approximately 3-4 months** for prototype testing!

## Prerequisites

- AWS Account with $200 credits
- AWS CLI installed
- SSH key pair
- Git installed locally
- Node.js 18+ and Python 3.11+ installed locally

---

## PART 1: AWS IAM Setup for Bedrock

### 1.1 Enable Bedrock Model Access

1. **Go to AWS Console → Amazon Bedrock → Model access**
2. **Click "Manage model access"**
3. **Enable these models:**
   - ✅ Claude 3 Haiku
   - ✅ Claude 3 Sonnet (optional, for better quality)
4. **Click "Save changes"**
5. **Wait for status to show "Access granted"** (takes 1-2 minutes)


### 1.2 Create IAM User for Bedrock Access

1. **Go to IAM → Users → Create user**
   ```
   User name: nyaya-mitra-bedrock-user
   ```

2. **Set permissions → Attach policies directly**
   - Search and select: `AmazonBedrockFullAccess`

3. **Create user**

4. **Create Access Keys:**
   - Click on the user → Security credentials tab
   - Create access key → Choose "Application running outside AWS"
   - **Save these credentials securely:**
     ```
     AWS_ACCESS_KEY_ID=AKIA...
     AWS_SECRET_ACCESS_KEY=...
     ```

---

## PART 2: Database Setup (RDS PostgreSQL)

### 2.1 Create RDS Instance

1. **Go to RDS → Create database**

2. **Configuration:**
   ```
   Engine: PostgreSQL 15
   Template: Free tier (if eligible) or Dev/Test
   DB instance: db.t3.micro
   
   DB instance identifier: nyaya-mitra-db
   Master username: nyaya_admin
   Master password: [Create strong password - SAVE THIS!]
   
   Storage: 20 GB gp3
   Public access: No
   VPC security group: Create new → nyaya-mitra-db-sg
   
   Initial database name: nyaya_mitra
   Automated backups: Enable (7 days)
   Encryption: Enable
   ```

3. **Create database** (takes 5-10 minutes)

4. **Save connection details:**
   ```
   Endpoint: nyaya-mitra-db.xxxxx.us-east-1.rds.amazonaws.com
   Port: 5432
   Database: nyaya_mitra
   Username: nyaya_admin
   Password: [your password]
   ```

---

## PART 3: EC2 Instance Setup

### 3.1 Launch EC2 Instance

1. **Go to EC2 → Launch instance**

2. **Configuration:**
   ```
   Name: nyaya-mitra-backend
   AMI: Ubuntu Server 22.04 LTS
   Instance type: t3.small (2 vCPU, 2 GB RAM) ← Much cheaper!
   
   Key pair: Create new → nyaya-mitra-key.pem (DOWNLOAD AND SAVE!)
   
   Network settings:
   - VPC: Same as RDS
   - Auto-assign public IP: Enable
   - Security group: nyaya-mitra-backend-sg
   
   Security group rules:
   - SSH (22): Your IP only
   - HTTP (80): 0.0.0.0/0
   - HTTPS (443): 0.0.0.0/0
   - Custom TCP (8000): 0.0.0.0/0
   
   Storage: 20 GB gp3 (less than Ollama setup)
   ```

3. **Launch instance**

4. **Save instance details:**
   ```
   Instance ID: i-xxxxx
   Public IP: xx.xx.xx.xx
   ```

### 3.2 Configure Security Groups

**Allow EC2 to access RDS:**

1. Go to RDS → nyaya-mitra-db → Security group
2. Edit inbound rules → Add rule:
   ```
   Type: PostgreSQL
   Port: 5432
   Source: nyaya-mitra-backend-sg
   ```

---

## PART 4: Backend Deployment

### 4.1 Connect to EC2

```bash
# Set key permissions
chmod 400 nyaya-mitra-key.pem

# Connect
ssh -i nyaya-mitra-key.pem ubuntu@<your-ec2-public-ip>
```

### 4.2 Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip git postgresql-client

# Verify Python version
python3.11 --version
```

### 4.3 Clone and Setup Application

```bash
# Create app directory
sudo mkdir -p /opt/nyaya-mitra
sudo chown ubuntu:ubuntu /opt/nyaya-mitra
cd /opt/nyaya-mitra

# Clone repository (replace with your repo URL)
git clone <your-repo-url> .

# Or upload via SCP from local machine:
# scp -i nyaya-mitra-key.pem -r backend ubuntu@<ec2-ip>:/opt/nyaya-mitra/

# Setup Python environment
cd backend
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install spaCy model
python -m spacy download en_core_web_sm
```

### 4.4 Configure Environment Variables

```bash
# Create .env file
nano /opt/nyaya-mitra/backend/.env
```

**Add the following configuration:**

```env
# Database Configuration
DATABASE_URL=postgresql://nyaya_admin:YOUR_DB_PASSWORD@nyaya-mitra-db.xxxxx.us-east-1.rds.amazonaws.com:5432/nyaya_mitra

# JWT Configuration
JWT_SECRET=<generate-secure-key-32-chars-minimum>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# AI Provider Configuration
AI_PROVIDER=bedrock

# AWS Bedrock Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=<your-bedrock-access-key>
AWS_SECRET_ACCESS_KEY=<your-bedrock-secret-key>
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0

# Vector Database
VECTOR_DB_TYPE=chroma

# Application Settings
ENVIRONMENT=production
LOG_LEVEL=INFO

# CORS Configuration (update after frontend deployment)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

**Generate secure keys:**

```bash
# Generate JWT secret
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Copy the output and paste it as JWT_SECRET value
```

Save and exit (Ctrl+X, Y, Enter)

### 4.5 Initialize Database

```bash
# Activate virtual environment
source /opt/nyaya-mitra/backend/.venv/bin/activate

# Initialize database
python3 -c "from database import init_db; init_db()"

# Should see: "Database initialized successfully"
```

### 4.6 Seed Initial Data

```bash
# Seed emergency contacts
python3 -c "
from database import get_db
import json

# Load and seed emergency contacts
with open('emergency_contacts_seed_data.json', 'r') as f:
    data = json.load(f)
    
from emergency_contacts_service import EmergencyContactsService
service = EmergencyContactsService()

with get_db() as db:
    for contact in data:
        service.create_emergency_contact(db, contact)
        
print('Emergency contacts seeded successfully')
"

# Seed legal aid providers (if file exists)
python3 -c "
from database import get_db
import json
import os

if os.path.exists('legal_aid_providers_seed_data.json'):
    with open('legal_aid_providers_seed_data.json', 'r') as f:
        data = json.load(f)
    
    from legal_aid_search_service import LegalAidSearchService
    service = LegalAidSearchService()
    
    with get_db() as db:
        for provider in data:
            service.create_legal_aid_provider(db, provider)
    
    print('Legal aid providers seeded successfully')
else:
    print('Legal aid seed file not found, skipping')
"
```

### 4.7 Test Backend Locally

```bash
# Start backend manually for testing
uvicorn main:app --host 0.0.0.0 --port 8000

# In another terminal, test:
curl http://localhost:8000/health
# Should return: {"status":"ok","message":"Nyaya Mitra API is running"}

# Test Bedrock connection
curl http://localhost:8000/api/chat/test

# Stop the test server (Ctrl+C)
```

### 4.8 Create Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/nyaya-mitra-backend.service
```

**Add this configuration:**

```ini
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
```

Save and exit.

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable nyaya-mitra-backend

# Start service
sudo systemctl start nyaya-mitra-backend

# Check status
sudo systemctl status nyaya-mitra-backend

# View logs
sudo journalctl -u nyaya-mitra-backend -f
```

### 4.9 Install Nginx (Reverse Proxy)

```bash
# Install Nginx
sudo apt install -y nginx

# Create configuration
sudo nano /etc/nginx/sites-available/nyaya-mitra
```

**Add this configuration:**

```nginx
server {
    listen 80;
    server_name _;  # Will accept any domain/IP

    client_max_body_size 10M;

    # API endpoints
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
    }

    location /db-health {
        proxy_pass http://localhost:8000/db-health;
    }

    # API docs
    location /docs {
        proxy_pass http://localhost:8000/docs;
    }

    location /redoc {
        proxy_pass http://localhost:8000/redoc;
    }
}
```

Save and exit.

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/nyaya-mitra /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Start Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 4.10 Test Backend from Internet

```bash
# From your local machine
curl http://<your-ec2-public-ip>/health

# Should return: {"status":"ok","message":"Nyaya Mitra API is running"}

# Test database connection
curl http://<your-ec2-public-ip>/db-health
```

---

## PART 5: Frontend Deployment (S3 + CloudFront)

### 5.1 Build Frontend Locally

On your local machine:

```bash
cd frontend

# Install dependencies
npm install

# Create production environment file
nano .env.production
```

Add:
```env
VITE_API_URL=http://<your-ec2-public-ip>
```

```bash
# Build for production
npm run build

# This creates 'dist' folder with optimized static files
```

### 5.2 Create S3 Bucket

1. **Go to S3 → Create bucket**

2. **Configuration:**
   ```
   Bucket name: nyaya-mitra-frontend-<random-suffix>
   Region: us-east-1
   
   Block Public Access: Uncheck all (we need public access)
   ✅ Acknowledge warning
   
   Bucket Versioning: Enable
   Encryption: Enable (SSE-S3)
   ```

3. **Create bucket**

### 5.3 Configure Static Website Hosting

1. **Go to bucket → Properties → Static website hosting**
2. **Enable static website hosting**
   ```
   Index document: index.html
   Error document: index.html
   ```
3. **Save changes**
4. **Note the endpoint URL**

### 5.4 Set Bucket Policy

1. **Go to Permissions → Bucket Policy**
2. **Add this policy** (replace bucket name):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::nyaya-mitra-frontend-<your-suffix>/*"
        }
    ]
}
```

3. **Save changes**

### 5.5 Upload Frontend Files

**Using AWS CLI:**

```bash
# Configure AWS CLI (if not done)
aws configure

# Upload files
cd frontend/dist
aws s3 sync . s3://nyaya-mitra-frontend-<your-suffix>/ --delete

# Set cache headers
aws s3 sync . s3://nyaya-mitra-frontend-<your-suffix>/ \
  --exclude "index.html" \
  --cache-control "public, max-age=31536000, immutable"

aws s3 cp index.html s3://nyaya-mitra-frontend-<your-suffix>/index.html \
  --cache-control "no-cache, no-store, must-revalidate"
```

### 5.6 Create CloudFront Distribution

1. **Go to CloudFront → Create distribution**

2. **Origin settings:**
   ```
   Origin domain: Select your S3 bucket
   Origin access: Origin access control (OAC)
   Create new OAC
   ```

3. **Default cache behavior:**
   ```
   Viewer protocol policy: Redirect HTTP to HTTPS
   Allowed HTTP methods: GET, HEAD, OPTIONS
   Cache policy: CachingOptimized
   ```

4. **Settings:**
   ```
   Price class: Use all edge locations
   Default root object: index.html
   ```

5. **Create distribution** (takes 10-15 minutes)

6. **Update S3 bucket policy** (CloudFront will show the required policy)

7. **Configure error pages:**
   - Go to Error pages tab
   - Create custom error response:
     ```
     HTTP error code: 403
     Response page path: /index.html
     HTTP response code: 200
     ```
   - Repeat for 404 error code

8. **Note CloudFront URL:**
   ```
   https://d1234567890abc.cloudfront.net
   ```

### 5.7 Update Backend CORS

```bash
# SSH to EC2
ssh -i nyaya-mitra-key.pem ubuntu@<ec2-ip>

# Edit .env file
nano /opt/nyaya-mitra/backend/.env
```

Update CORS_ORIGINS:
```env
CORS_ORIGINS=https://d1234567890abc.cloudfront.net,http://localhost:3000
```

```bash
# Restart backend
sudo systemctl restart nyaya-mitra-backend
```

---

## PART 6: Testing

### 6.1 Test Complete Flow

1. **Open CloudFront URL in browser**
2. **Register a new account**
3. **Login**
4. **Test each feature:**
   - ✅ Chat with AI (tests Bedrock integration)
   - ✅ Case Analyzer
   - ✅ Document Generator
   - ✅ Legal Aid Search
   - ✅ Evidence Guide
   - ✅ Emergency SOS

### 6.2 Monitor Bedrock Usage

1. **Go to AWS Console → CloudWatch → Metrics**
2. **Select Bedrock namespace**
3. **Monitor:**
   - Invocations
   - Input tokens
   - Output tokens
   - Errors

### 6.3 Check Logs

```bash
# Backend logs
sudo journalctl -u nyaya-mitra-backend -f

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

---

## PART 7: Cost Monitoring

### 7.1 Set Up Budget Alerts

1. **Go to AWS Billing → Budgets**
2. **Create budget:**
   ```
   Budget type: Cost budget
   Budget amount: $50/month
   Alert threshold: 80% ($40)
   Email: your-email@example.com
   ```

### 7.2 Enable Cost Explorer

1. **Go to Cost Explorer**
2. **View costs by service**
3. **Monitor daily spending**

### 7.3 Track Bedrock Costs

Bedrock pricing (Claude 3 Haiku):
- Input: $0.25 per 1M tokens
- Output: $1.25 per 1M tokens

Typical usage for 1000 queries:
- ~$2-5 depending on query complexity

---

## PART 8: Maintenance

### 8.1 Update Application

```bash
# SSH to EC2
ssh -i nyaya-mitra-key.pem ubuntu@<ec2-ip>

# Pull latest code
cd /opt/nyaya-mitra
git pull

# Update backend
cd backend
source .venv/bin/activate
pip install -r requirements.txt

# Restart service
sudo systemctl restart nyaya-mitra-backend

# Check status
sudo systemctl status nyaya-mitra-backend
```

### 8.2 Database Backups

```bash
# Manual snapshot
aws rds create-db-snapshot \
  --db-instance-identifier nyaya-mitra-db \
  --db-snapshot-identifier nyaya-mitra-backup-$(date +%Y%m%d)
```

### 8.3 EC2 Backup

```bash
# Create AMI
aws ec2 create-image \
  --instance-id i-xxxxx \
  --name "nyaya-mitra-backup-$(date +%Y%m%d)"
```

---

## PART 9: Troubleshooting

### Issue: Bedrock Access Denied

**Solution:**
```bash
# Check IAM permissions
aws bedrock list-foundation-models --region us-east-1

# Verify model access in Bedrock console
# Ensure Claude 3 Haiku is enabled
```

### Issue: Backend Can't Connect to Bedrock

**Solution:**
```bash
# Check environment variables
cat /opt/nyaya-mitra/backend/.env | grep AWS

# Test AWS credentials
aws sts get-caller-identity

# Check backend logs
sudo journalctl -u nyaya-mitra-backend -n 100
```

### Issue: High Bedrock Costs

**Solution:**
- Implement request caching
- Add rate limiting
- Use shorter context windows
- Consider switching to Claude 3 Haiku (cheapest)

### Issue: Frontend Not Loading

**Solution:**
- Check CloudFront distribution status
- Clear browser cache
- Check browser console for errors
- Verify API URL in frontend build

---

## PART 10: Security Checklist

- [ ] Changed all default passwords
- [ ] Generated strong JWT secret
- [ ] AWS access keys stored securely
- [ ] RDS not publicly accessible
- [ ] EC2 SSH restricted to your IP
- [ ] HTTPS enabled via CloudFront
- [ ] Security groups properly configured
- [ ] Bedrock IAM permissions minimal
- [ ] Regular backups enabled
- [ ] Budget alerts configured

---

## Summary

**What You've Deployed:**
- ✅ Backend API on EC2 t3.small
- ✅ PostgreSQL database on RDS
- ✅ AI powered by AWS Bedrock (Claude 3 Haiku)
- ✅ Frontend on S3 + CloudFront CDN
- ✅ HTTPS enabled
- ✅ Automated backups

**Monthly Cost: ~$45-55 (Your $200 credits = 3-4 months)**

**Next Steps:**
1. Test thoroughly with real users
2. Monitor costs daily for first week
3. Gather feedback
4. Optimize based on usage patterns
5. Consider adding Redis caching
6. Set up CI/CD pipeline

**Support:**
- AWS Documentation: https://docs.aws.amazon.com
- Bedrock Documentation: https://docs.aws.amazon.com/bedrock
- FastAPI Documentation: https://fastapi.tiangolo.com

---

**Congratulations! Your Nyaya Mitra platform is now live on AWS! 🎉**
