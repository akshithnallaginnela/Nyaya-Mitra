# Nyaya Mitra - Quick Start Deployment Guide

This is a condensed version of the full deployment guide. Use this for quick reference.

## Prerequisites Check

Run this first:
```bash
pre-deployment-check.bat
```

## 5-Step Deployment

### Step 1: Enable Bedrock (5 min)

1. AWS Console → Bedrock → Model access
2. Enable "Claude 3 Haiku"
3. Create IAM user with `AmazonBedrockFullAccess`
4. Generate access keys → Save them!

### Step 2: Create Database (10 min)

1. AWS Console → RDS → Create database
2. PostgreSQL 15, db.t3.micro, 20GB
3. Name: `nyaya-mitra-db`
4. Username: `nyaya_admin`
5. Save endpoint and password!

### Step 3: Launch EC2 (10 min)

1. AWS Console → EC2 → Launch instance
2. Ubuntu 22.04, t3.small, 20GB
3. Name: `nyaya-mitra-backend`
4. Create security group (ports: 22, 80, 443, 8000)
5. Download key pair!
6. Update RDS security group to allow EC2

### Step 4: Deploy Backend (60 min)

```bash
# Connect to EC2
ssh -i nyaya-mitra-key.pem ubuntu@<ec2-ip>

# Install dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3-pip git postgresql-client nginx

# Setup application
sudo mkdir -p /opt/nyaya-mitra
sudo chown ubuntu:ubuntu /opt/nyaya-mitra
cd /opt/nyaya-mitra
git clone <your-repo> .

# Setup Python
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Configure environment
nano .env
# Add all required variables (see full guide)

# Initialize database
python3 -c "from database import init_db; init_db()"

# Create systemd service (see full guide for service file)
sudo nano /etc/systemd/system/nyaya-mitra-backend.service
sudo systemctl enable nyaya-mitra-backend
sudo systemctl start nyaya-mitra-backend

# Configure Nginx (see full guide for nginx config)
sudo nano /etc/nginx/sites-available/nyaya-mitra
sudo ln -s /etc/nginx/sites-available/nyaya-mitra /etc/nginx/sites-enabled/
sudo systemctl restart nginx

# Test
curl http://localhost:8000/health
```

### Step 5: Deploy Frontend (30 min)

```bash
# On your local machine
cd frontend

# Configure
echo "VITE_API_URL=http://<ec2-ip>" > .env.production

# Build
npm install
npm run build

# Create S3 bucket
aws s3 mb s3://nyaya-mitra-frontend-<random>

# Enable static hosting (via console)
# Upload files
aws s3 sync dist/ s3://nyaya-mitra-frontend-<random>/ --delete

# Create CloudFront distribution (via console)
# Configure error pages for React Router

# Update backend CORS
# SSH to EC2, edit .env, add CloudFront URL to CORS_ORIGINS
# Restart backend: sudo systemctl restart nyaya-mitra-backend
```

## Environment Variables Template

```env
# Database
DATABASE_URL=postgresql://nyaya_admin:PASSWORD@ENDPOINT:5432/nyaya_mitra

# JWT
JWT_SECRET=<generate-with-python>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# AI Provider
AI_PROVIDER=bedrock

# AWS Bedrock
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0

# Vector DB
VECTOR_DB_TYPE=chroma

# Application
ENVIRONMENT=production
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=https://<cloudfront-url>,http://localhost:3000
```

## Generate Secrets

```bash
# JWT Secret
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Common Commands

### Check Backend Status
```bash
sudo systemctl status nyaya-mitra-backend
sudo journalctl -u nyaya-mitra-backend -f
```

### Restart Backend
```bash
sudo systemctl restart nyaya-mitra-backend
```

### Update Application
```bash
cd /opt/nyaya-mitra
git pull
cd backend
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart nyaya-mitra-backend
```

### Update Frontend
```bash
# Local machine
cd frontend
npm run build
aws s3 sync dist/ s3://your-bucket/ --delete
aws cloudfront create-invalidation --distribution-id <id> --paths "/*"
```

### View Logs
```bash
# Backend
sudo journalctl -u nyaya-mitra-backend -n 100

# Nginx access
sudo tail -f /var/log/nginx/access.log

# Nginx errors
sudo tail -f /var/log/nginx/error.log
```

## Testing Checklist

- [ ] Health check: `curl http://<ec2-ip>/health`
- [ ] DB health: `curl http://<ec2-ip>/db-health`
- [ ] API docs: `http://<ec2-ip>/docs`
- [ ] Frontend loads
- [ ] User registration works
- [ ] User login works
- [ ] Chat works (Bedrock)
- [ ] All features functional

## Cost Monitoring

```bash
# Check current month costs
aws ce get-cost-and-usage \
  --time-period Start=2026-03-01,End=2026-03-07 \
  --granularity DAILY \
  --metrics BlendedCost
```

## Troubleshooting

### Backend won't start
```bash
sudo journalctl -u nyaya-mitra-backend -n 50
# Check .env file
# Check database connection
```

### Bedrock access denied
```bash
# Verify IAM permissions
aws bedrock list-foundation-models --region us-east-1
# Check model access in Bedrock console
```

### Frontend not loading
- Check CloudFront distribution status
- Clear browser cache
- Check browser console
- Verify API URL in build

### Database connection failed
- Check RDS security group
- Verify EC2 security group is allowed
- Test connection: `psql -h <endpoint> -U nyaya_admin -d nyaya_mitra`

## Security Checklist

- [ ] Changed all default passwords
- [ ] Generated strong JWT secret
- [ ] AWS keys stored securely
- [ ] RDS not publicly accessible
- [ ] SSH restricted to your IP
- [ ] HTTPS enabled
- [ ] Security groups minimal
- [ ] Backups enabled
- [ ] Budget alerts set

## Cost Estimate

- EC2 t3.small: ~$15/month
- RDS db.t3.micro: ~$15/month
- S3 + CloudFront: ~$5/month
- Bedrock: ~$10-20/month
- **Total: ~$45-55/month**
- **Your $200 credits = 3-4 months**

## Support

- Full guide: `AWS_BEDROCK_DEPLOYMENT_GUIDE.md`
- Checklist: `DEPLOYMENT_CHECKLIST.md`
- AWS Docs: https://docs.aws.amazon.com
- Bedrock Docs: https://docs.aws.amazon.com/bedrock

---

**Ready to deploy? Follow the full guide in AWS_BEDROCK_DEPLOYMENT_GUIDE.md**
