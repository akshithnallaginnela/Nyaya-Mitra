# 🚀 AWS Deployment Quick Reference

**One-page cheat sheet for deploying Nyaya Mitra**

---

## 📋 Before You Start

```cmd
# Run this to verify you're ready
prepare-for-deployment.cmd
```

---

## 🎯 Deployment Order

```
1. RDS PostgreSQL (30 min)
   ↓
2. EC2 + Backend (60 min)
   ↓
3. S3 + Frontend (30 min)
   ↓
4. CloudFront (20 min)
   ↓
5. Testing (30 min)
```

**Total: 3-4 hours**

---

## 🔑 Essential AWS Services

| Service | Purpose | Size | Cost/Month |
|---------|---------|------|------------|
| RDS PostgreSQL | Database | db.t3.micro | $15 (Free: $0) |
| EC2 Ubuntu | Backend + Ollama | t3.large | $60 |
| S3 | Frontend files | 5GB | $1 (Free: $0) |
| CloudFront | CDN + HTTPS | 100GB | $10 (Free: $0) |

**Total: ~$75-95/month**

---

## 📝 Quick Commands

### RDS Setup
```sql
-- After creating RDS, connect and verify
psql -h <rds-endpoint> -U nyaya_admin -d nyaya_mitra
```

### EC2 Setup
```bash
# Connect to EC2
ssh -i nyaya-mitra-key.pem ubuntu@<ec2-ip>

# Install everything
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv git
curl -fsSL https://ollama.com/install.sh | sh
ollama pull mistral:7b

# Setup backend
cd /opt/nyaya-mitra/backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -c "from database import init_db; init_db()"
```

### Frontend Build
```cmd
# On your local machine
cd frontend
echo VITE_API_URL=http://<ec2-ip> > .env.production
npm run build

# Upload to S3
aws s3 sync dist/ s3://your-bucket-name/ --delete
```

### Service Management
```bash
# Start backend
sudo systemctl start nyaya-mitra-backend

# View logs
sudo journalctl -u nyaya-mitra-backend -f

# Restart services
sudo systemctl restart nyaya-mitra-backend
sudo systemctl restart ollama
sudo systemctl restart nginx
```

---

## 🔒 Security Checklist

- [ ] RDS not publicly accessible
- [ ] EC2 SSH restricted to your IP
- [ ] Strong passwords for all services
- [ ] JWT_SECRET changed from default
- [ ] ENCRYPTION_KEY generated
- [ ] HTTPS enabled (CloudFront)
- [ ] Security groups properly configured
- [ ] Backups enabled

---

## 🧪 Testing Commands

### Backend Health
```bash
curl http://<ec2-ip>/health
curl http://<ec2-ip>/db-health
curl http://<ec2-ip>/docs
```

### Register User
```bash
curl -X POST http://<ec2-ip>/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","full_name":"Test User"}'
```

### Login
```bash
curl -X POST http://<ec2-ip>/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'
```

---

## 🆘 Troubleshooting

### Backend Not Responding
```bash
ssh -i nyaya-mitra-key.pem ubuntu@<ec2-ip>
sudo systemctl status nyaya-mitra-backend
sudo journalctl -u nyaya-mitra-backend -n 50
sudo systemctl restart nyaya-mitra-backend
```

### Database Connection Failed
```bash
# Check security group
# Verify DATABASE_URL in .env
psql -h <rds-endpoint> -U nyaya_admin -d nyaya_mitra
```

### Ollama Not Working
```bash
sudo systemctl status ollama
ollama list
sudo systemctl restart ollama
```

### Frontend Not Loading
```bash
# Check S3 bucket policy
# Verify files uploaded
aws s3 ls s3://your-bucket-name/

# Clear CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id <id> --paths "/*"
```

---

## 💾 Backup Commands

### RDS Snapshot
```bash
aws rds create-db-snapshot \
  --db-instance-identifier nyaya-mitra-db \
  --db-snapshot-identifier backup-$(date +%Y%m%d)
```

### EC2 AMI
```bash
aws ec2 create-image \
  --instance-id <instance-id> \
  --name "nyaya-mitra-backup-$(date +%Y%m%d)"
```

---

## 📊 Monitoring

### Check Costs
```bash
# AWS Console → Billing Dashboard
# Or use CLI:
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost
```

### View Logs
```bash
# Backend logs
ssh -i nyaya-mitra-key.pem ubuntu@<ec2-ip>
sudo journalctl -u nyaya-mitra-backend -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 🔄 Update Procedures

### Update Backend Code
```bash
# SSH to EC2
ssh -i nyaya-mitra-key.pem ubuntu@<ec2-ip>

# Pull latest code
cd /opt/nyaya-mitra
git pull

# Restart service
sudo systemctl restart nyaya-mitra-backend
```

### Update Frontend
```cmd
# On local machine
cd frontend
npm run build
aws s3 sync dist/ s3://your-bucket-name/ --delete
aws cloudfront create-invalidation --distribution-id <id> --paths "/*"
```

---

## 📞 Important URLs

```
AWS Console: https://console.aws.amazon.com
Backend API: http://<ec2-ip>:8000
API Docs: http://<ec2-ip>:8000/docs
Frontend: https://<cloudfront-url>
RDS Console: https://console.aws.amazon.com/rds
EC2 Console: https://console.aws.amazon.com/ec2
S3 Console: https://console.aws.amazon.com/s3
CloudFront Console: https://console.aws.amazon.com/cloudfront
```

---

## 📚 Full Documentation

- **Complete Guide:** `AWS_MVP_DEPLOYMENT_GUIDE.md`
- **Checklist:** `AWS_DEPLOYMENT_CHECKLIST.md`
- **Getting Started:** `START_AWS_DEPLOYMENT.md`
- **Local Setup:** `LOCAL_SETUP_GUIDE.md`

---

## ⚡ Quick Start

```cmd
# 1. Prepare
prepare-for-deployment.cmd

# 2. Read
START_AWS_DEPLOYMENT.md

# 3. Deploy
Follow AWS_MVP_DEPLOYMENT_GUIDE.md

# 4. Track
Use AWS_DEPLOYMENT_CHECKLIST.md

# 5. Test
Test all features

# 6. Monitor
Check logs and costs
```

---

## 💡 Pro Tips

1. **Save everything** in `deployment-info.txt`
2. **Take snapshots** before major changes
3. **Monitor costs** daily for first week
4. **Stop EC2** when not testing (saves $60/month)
5. **Use free tier** for first 12 months
6. **Set budget alerts** at $50/month
7. **Keep SSH key** safe and backed up
8. **Document changes** as you make them

---

## 🎯 Success Criteria

✅ Backend responds to `/health`
✅ Database connected and seeded
✅ Ollama generates responses
✅ Frontend loads via HTTPS
✅ Users can register/login
✅ All features work
✅ Backups configured
✅ Monitoring active
✅ Costs within budget

---

**Need help? Open the full guides!**

**Ready? Run:** `prepare-for-deployment.cmd`
