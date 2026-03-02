# AWS MVP Deployment Guide - Nyaya Mitra

This guide will help you deploy Nyaya Mitra on AWS for MVP testing with minimal costs.

## Architecture Overview

```
┌─────────────────┐
│   CloudFront    │ ← Frontend (S3)
└────────┬────────┘
         │
┌────────▼────────┐
│  EC2 Instance   │ ← Backend + Ollama
│  (t3.large)     │
└────────┬────────┘
         │
┌────────▼────────┐
│  RDS PostgreSQL │ ← Database
│  (db.t3.micro)  │
└─────────────────┘
```

## Prerequisites

- AWS Account with billing enabled
- AWS CLI installed and configured
- Domain name (optional, can use AWS provided URLs)
- SSH key pair for EC2 access

## Step-by-Step Setup

---

## Part 1: Database Setup (RDS PostgreSQL)

### 1.1 Create RDS PostgreSQL Instance

1. **Go to AWS Console → RDS → Create Database**

2. **Choose Configuration:**
   - Engine: PostgreSQL 14 or 15
   - Template: Free tier (if eligible) or Dev/Test
   - DB Instance: db.t3.micro (Free tier) or db.t3.small

3. **Settings:**
   ```
   DB instance identifier: nyaya-mitra-db
   Master username: nyaya_admin
   Master password: [Create strong password - save this!]
   ```

4. **Instance Configuration:**
   - DB instance class: db.t3.micro (1 vCPU, 1 GB RAM)
   - Storage: 20 GB General Purpose SSD (gp3)
   - Enable storage autoscaling: Yes (max 100 GB)

5. **Connectivity:**
   - VPC: Default VPC (or create new)
   - Public access: No (for security)
   - VPC security group: Create new → `nyaya-mitra-db-sg`
   - Availability Zone: No preference

6. **Database Authentication:**
   - Password authentication

7. **Additional Configuration:**
   - Initial database name: `nyaya_mitra`
   - Backup retention: 7 days
   - Enable encryption: Yes
   - Enable automated backups: Yes

8. **Click "Create Database"** (takes 5-10 minutes)

9. **Save Connection Details:**
   ```
   Endpoint: nyaya-mitra-db.xxxxxxxxx.us-east-1.rds.amazonaws.com
   Port: 5432
   Database: nyaya_mitra
   Username: nyaya_admin
   Password: [your password]
   ```

---

## Part 2: EC2 Instance Setup (Backend + Ollama)

### 2.1 Launch EC2 Instance

1. **Go to AWS Console → EC2 → Launch Instance**

2. **Name and Tags:**
   ```
   Name: nyaya-mitra-backend
   ```

3. **Choose AMI:**
   - Ubuntu Server 22.04 LTS (Free tier eligible)
   - 64-bit (x86)

4. **Instance Type:**
   - t3.large (2 vCPU, 8 GB RAM) - Needed for Ollama
   - Note: This is NOT free tier, costs ~$60/month

5. **Key Pair:**
   - Create new key pair or use existing
   - Name: `nyaya-mitra-key`
   - Type: RSA
   - Format: .pem (for SSH)
   - **Download and save the .pem file securely!**

6. **Network Settings:**
   - VPC: Same as RDS (Default VPC)
   - Auto-assign public IP: Enable
   - Create security group: `nyaya-mitra-backend-sg`
   - Add rules:
     - SSH (22) - Your IP only
     - HTTP (80) - Anywhere (0.0.0.0/0)
     - HTTPS (443) - Anywhere (0.0.0.0/0)
     - Custom TCP (8000) - Anywhere (for FastAPI)

7. **Configure Storage:**
   - 30 GB gp3 (for OS, code, Ollama model)

8. **Advanced Details:**
   - Leave defaults

9. **Click "Launch Instance"**

10. **Save Instance Details:**
    ```
    Instance ID: i-xxxxxxxxxxxxxxxxx
    Public IP: xx.xx.xx.xx
    Public DNS: ec2-xx-xx-xx-xx.compute-1.amazonaws.com
    ```

### 2.2 Configure Security Groups

**Update RDS Security Group to allow EC2 access:**

1. Go to RDS → Databases → nyaya-mitra-db → Connectivity & security
2. Click on the VPC security group
3. Edit inbound rules → Add rule:
   ```
   Type: PostgreSQL
   Protocol: TCP
   Port: 5432
   Source: Custom → Select nyaya-mitra-backend-sg
   Description: Allow backend access
   ```

---

## Part 3: Backend Setup on EC2

### 3.1 Connect to EC2 Instance

```bash
# Set permissions on key file
chmod 400 nyaya-mitra-key.pem

# Connect via SSH
ssh -i nyaya-mitra-key.pem ubuntu@<your-ec2-public-ip>
```

### 3.2 Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip git postgresql-client

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Verify Ollama installation
ollama --version
```

### 3.3 Pull Mistral Model

```bash
# This will download ~4GB model
ollama pull mistral:7b

# Verify model is available
ollama list
```

### 3.4 Clone and Setup Backend

```bash
# Create application directory
sudo mkdir -p /opt/nyaya-mitra
sudo chown ubuntu:ubuntu /opt/nyaya-mitra
cd /opt/nyaya-mitra

# Clone your repository (or upload files)
# Option 1: If using Git
git clone <your-repo-url> .

# Option 2: If uploading manually, use SCP from your local machine:
# scp -i nyaya-mitra-key.pem -r backend ubuntu@<ec2-ip>:/opt/nyaya-mitra/

# Create virtual environment
cd backend
python3.11 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install spaCy English model
python -m spacy download en_core_web_sm
```

### 3.5 Configure Environment Variables

```bash
# Create .env file
nano /opt/nyaya-mitra/backend/.env
```

Add the following (replace with your actual values):

```env
# Database Configuration
DATABASE_URL=postgresql://nyaya_admin:YOUR_PASSWORD@nyaya-mitra-db.xxxxxxxxx.us-east-1.rds.amazonaws.com:5432/nyaya_mitra

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Encryption Configuration
ENCRYPTION_KEY=your-encryption-key-base64-encoded-32-bytes

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434

# Application Configuration
ENVIRONMENT=production
DEBUG=False
```

**Generate secure keys:**

```bash
# Generate JWT secret (32+ characters)
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate encryption key
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Save and exit (Ctrl+X, Y, Enter)

### 3.6 Initialize Database

```bash
# Test database connection
python3 -c "from database import init_db; init_db()"

# If successful, you should see tables created
```

### 3.7 Seed Initial Data

```bash
# Seed emergency contacts
python3 -c "
from database import get_db
from emergency_contacts_seed_data import seed_emergency_contacts
with get_db() as db:
    seed_emergency_contacts(db)
print('Emergency contacts seeded')
"

# Seed legal aid providers (if you have the seed file)
python3 -c "
from database import get_db
from legal_aid_providers_seed_data import seed_legal_aid_providers
with get_db() as db:
    seed_legal_aid_providers(db)
print('Legal aid providers seeded')
"
```

### 3.8 Create Systemd Service for Backend

```bash
# Create service file
sudo nano /etc/systemd/system/nyaya-mitra-backend.service
```

Add the following:

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

# Enable service to start on boot
sudo systemctl enable nyaya-mitra-backend

# Start the service
sudo systemctl start nyaya-mitra-backend

# Check status
sudo systemctl status nyaya-mitra-backend

# View logs
sudo journalctl -u nyaya-mitra-backend -f
```

### 3.9 Create Systemd Service for Ollama

```bash
# Create service file
sudo nano /etc/systemd/system/ollama.service
```

Add the following:

```ini
[Unit]
Description=Ollama Service
After=network.target

[Service]
Type=simple
User=ubuntu
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=10
Environment="OLLAMA_HOST=0.0.0.0:11434"

[Install]
WantedBy=multi-user.target
```

Save and exit.

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable and start Ollama
sudo systemctl enable ollama
sudo systemctl start ollama

# Check status
sudo systemctl status ollama
```

### 3.10 Install and Configure Nginx (Reverse Proxy)

```bash
# Install Nginx
sudo apt install -y nginx

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/nyaya-mitra
```

Add the following:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain or EC2 public IP

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

    # Health check endpoints
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
# Enable the site
sudo ln -s /etc/nginx/sites-available/nyaya-mitra /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx

# Enable Nginx to start on boot
sudo systemctl enable nginx
```

### 3.11 Test Backend

```bash
# Test from EC2 instance
curl http://localhost:8000/health

# Test from your local machine
curl http://<your-ec2-public-ip>/health

# Should return: {"status":"ok","message":"Nyaya Mitra API is running"}
```

---

## Part 4: Frontend Setup (S3 + CloudFront)

### 4.1 Build Frontend Locally

On your local machine:

```bash
cd frontend

# Install dependencies
npm install

# Update API endpoint in .env or vite.config.ts
# Create .env.production file
echo "VITE_API_URL=http://<your-ec2-public-ip>" > .env.production

# Build for production
npm run build

# This creates a 'dist' folder with static files
```

### 4.2 Create S3 Bucket

1. **Go to AWS Console → S3 → Create Bucket**

2. **Bucket Settings:**
   ```
   Bucket name: nyaya-mitra-frontend (must be globally unique)
   Region: us-east-1 (or your preferred region)
   ```

3. **Object Ownership:**
   - ACLs disabled (recommended)

4. **Block Public Access:**
   - Uncheck "Block all public access"
   - Acknowledge the warning

5. **Bucket Versioning:**
   - Enable (recommended)

6. **Encryption:**
   - Enable server-side encryption (SSE-S3)

7. **Click "Create Bucket"**

### 4.3 Configure S3 for Static Website Hosting

1. **Go to your bucket → Properties tab**

2. **Scroll to "Static website hosting"**
   - Enable
   - Index document: `index.html`
   - Error document: `index.html` (for React Router)

3. **Save changes**

4. **Note the endpoint URL:**
   ```
   http://nyaya-mitra-frontend.s3-website-us-east-1.amazonaws.com
   ```

### 4.4 Set Bucket Policy

1. **Go to Permissions tab → Bucket Policy**

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
            "Resource": "arn:aws:s3:::nyaya-mitra-frontend/*"
        }
    ]
}
```

3. **Save changes**

### 4.5 Upload Frontend Files

**Option 1: Using AWS CLI**

```bash
# Configure AWS CLI (if not done)
aws configure

# Upload files
cd frontend/dist
aws s3 sync . s3://nyaya-mitra-frontend/ --delete

# Set cache control for static assets
aws s3 sync . s3://nyaya-mitra-frontend/ \
  --exclude "index.html" \
  --cache-control "public, max-age=31536000, immutable"

# Set cache control for index.html (no cache)
aws s3 cp index.html s3://nyaya-mitra-frontend/index.html \
  --cache-control "no-cache, no-store, must-revalidate"
```

**Option 2: Using AWS Console**

1. Go to your bucket
2. Click "Upload"
3. Drag and drop all files from `frontend/dist`
4. Click "Upload"

### 4.6 Create CloudFront Distribution (Optional but Recommended)

1. **Go to AWS Console → CloudFront → Create Distribution**

2. **Origin Settings:**
   ```
   Origin domain: Select your S3 bucket
   Origin path: Leave empty
   Name: Auto-generated
   ```

3. **Origin Access:**
   - Origin access control settings (recommended)
   - Create new OAC

4. **Default Cache Behavior:**
   ```
   Viewer protocol policy: Redirect HTTP to HTTPS
   Allowed HTTP methods: GET, HEAD, OPTIONS
   Cache policy: CachingOptimized
   ```

5. **Settings:**
   ```
   Price class: Use all edge locations (best performance)
   Alternate domain name (CNAME): your-domain.com (if you have one)
   Custom SSL certificate: Request or import certificate (if using custom domain)
   Default root object: index.html
   ```

6. **Click "Create Distribution"** (takes 10-15 minutes to deploy)

7. **Update S3 Bucket Policy** (CloudFront will provide the policy)

8. **Note CloudFront URL:**
   ```
   https://d1234567890abc.cloudfront.net
   ```

### 4.7 Configure Error Pages for React Router

1. **Go to CloudFront → Your Distribution → Error Pages**

2. **Create Custom Error Response:**
   ```
   HTTP Error Code: 403
   Customize Error Response: Yes
   Response Page Path: /index.html
   HTTP Response Code: 200
   ```

3. **Create another for 404:**
   ```
   HTTP Error Code: 404
   Customize Error Response: Yes
   Response Page Path: /index.html
   HTTP Response Code: 200
   ```

---

## Part 5: SSL/TLS Setup (Optional but Recommended)

### 5.1 Request SSL Certificate (If using custom domain)

1. **Go to AWS Certificate Manager (ACM)**
   - Must be in us-east-1 region for CloudFront

2. **Request Certificate:**
   ```
   Domain names: 
   - your-domain.com
   - www.your-domain.com
   
   Validation method: DNS validation
   ```

3. **Add CNAME records to your domain DNS** (provided by ACM)

4. **Wait for validation** (can take 5-30 minutes)

5. **Attach certificate to CloudFront distribution**

### 5.2 Configure Route 53 (If using custom domain)

1. **Create Hosted Zone** for your domain

2. **Create A Record:**
   ```
   Record name: (leave empty for root domain)
   Record type: A
   Alias: Yes
   Route traffic to: CloudFront distribution
   Select your distribution
   ```

3. **Create CNAME for www:**
   ```
   Record name: www
   Record type: CNAME
   Value: your-domain.com
   ```

---

## Part 6: Testing and Verification

### 6.1 Test Backend

```bash
# Health check
curl https://your-domain.com/health

# Test registration
curl -X POST https://your-domain.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "full_name": "Test User"
  }'

# Test login
curl -X POST https://your-domain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'
```

### 6.2 Test Frontend

1. Open browser and go to your CloudFront URL or custom domain
2. Try to register a new account
3. Login with the account
4. Test each feature:
   - Chat
   - Case Analyzer
   - Document Generator
   - Legal Aid Search
   - Evidence Guide
   - Emergency SOS

### 6.3 Monitor Logs

**Backend logs:**
```bash
# SSH to EC2
ssh -i nyaya-mitra-key.pem ubuntu@<ec2-ip>

# View backend logs
sudo journalctl -u nyaya-mitra-backend -f

# View Ollama logs
sudo journalctl -u ollama -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

**CloudWatch (Optional):**
- Set up CloudWatch agent on EC2 for centralized logging

---

## Part 7: Cost Optimization Tips

### 7.1 Use AWS Free Tier

- RDS db.t3.micro: 750 hours/month free for 12 months
- S3: 5GB storage free for 12 months
- CloudFront: 1TB data transfer free for 12 months

### 7.2 Stop EC2 When Not in Use

```bash
# Stop instance (from AWS CLI)
aws ec2 stop-instances --instance-ids i-xxxxxxxxxxxxxxxxx

# Start instance
aws ec2 start-instances --instance-ids i-xxxxxxxxxxxxxxxxx
```

Note: You'll only pay for storage when stopped (~$3/month for 30GB)

### 7.3 Use Spot Instances (Advanced)

- Can save up to 90% on EC2 costs
- Risk: Instance can be terminated with 2-minute notice

### 7.4 Monitor Costs

1. **Set up AWS Budgets:**
   - Go to AWS Billing → Budgets
   - Create budget alert for $50/month

2. **Enable Cost Explorer:**
   - Track daily spending
   - Identify cost spikes

---

## Part 8: Backup and Maintenance

### 8.1 Automated RDS Backups

- Already enabled (7-day retention)
- Manual snapshot before major changes:
  ```bash
  aws rds create-db-snapshot \
    --db-instance-identifier nyaya-mitra-db \
    --db-snapshot-identifier nyaya-mitra-backup-$(date +%Y%m%d)
  ```

### 8.2 EC2 Snapshots

```bash
# Create AMI of EC2 instance
aws ec2 create-image \
  --instance-id i-xxxxxxxxxxxxxxxxx \
  --name "nyaya-mitra-backend-backup-$(date +%Y%m%d)" \
  --description "Backup before update"
```

### 8.3 S3 Versioning

- Already enabled
- Can restore previous versions if needed

---

## Part 9: Troubleshooting

### Common Issues

**1. Backend not accessible:**
```bash
# Check if service is running
sudo systemctl status nyaya-mitra-backend

# Check logs
sudo journalctl -u nyaya-mitra-backend -n 50

# Restart service
sudo systemctl restart nyaya-mitra-backend
```

**2. Database connection errors:**
```bash
# Test connection from EC2
psql -h nyaya-mitra-db.xxxxxxxxx.us-east-1.rds.amazonaws.com \
     -U nyaya_admin -d nyaya_mitra

# Check security group rules
# Ensure EC2 security group is allowed in RDS security group
```

**3. Ollama not responding:**
```bash
# Check Ollama status
sudo systemctl status ollama

# Test Ollama
curl http://localhost:11434/api/tags

# Restart Ollama
sudo systemctl restart ollama
```

**4. Frontend not loading:**
- Check CloudFront distribution status (must be "Deployed")
- Clear browser cache
- Check browser console for errors
- Verify API URL in frontend build

**5. CORS errors:**
- Check backend CORS configuration in `main.py`
- Ensure CloudFront URL is in allowed origins

---

## Part 10: Security Checklist

- [ ] Changed all default passwords
- [ ] Generated strong JWT secret key
- [ ] Generated encryption key
- [ ] RDS is not publicly accessible
- [ ] EC2 SSH restricted to your IP only
- [ ] HTTPS enabled (CloudFront or Nginx with Let's Encrypt)
- [ ] Security groups properly configured
- [ ] Secrets stored in AWS Secrets Manager (optional)
- [ ] Regular backups enabled
- [ ] CloudWatch alarms set up
- [ ] AWS Budget alerts configured

---

## Estimated Monthly Costs

```
EC2 t3.large (24/7):        $60.74
RDS db.t3.micro:            $14.60 (free tier: $0)
EBS Storage (30GB):         $3.00
S3 Storage (5GB):           $0.12 (free tier: $0)
CloudFront (100GB):         $8.50 (free tier: $0)
Data Transfer:              $9.00
─────────────────────────────────
Total (with free tier):     ~$75/month
Total (without free tier):  ~$95/month
```

---

## Next Steps

1. ✅ Complete this setup
2. ✅ Test all features thoroughly
3. ✅ Monitor for 24-48 hours
4. ✅ Gather user feedback
5. ⏭️ Scale up if needed (add load balancer, auto-scaling)
6. ⏭️ Add monitoring and alerting
7. ⏭️ Implement CI/CD pipeline
8. ⏭️ Add Redis for caching
9. ⏭️ Optimize Ollama performance
10. ⏭️ Consider managed Kubernetes (EKS) for production

---

## Support and Resources

- AWS Documentation: https://docs.aws.amazon.com
- Ollama Documentation: https://ollama.ai/docs
- FastAPI Documentation: https://fastapi.tiangolo.com
- React Documentation: https://react.dev

For issues, check the troubleshooting section or AWS support forums.
