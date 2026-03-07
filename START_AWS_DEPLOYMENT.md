# 🚀 Start AWS Deployment - Nyaya Mitra

**Ready to deploy? Follow this guide step-by-step!**

---

## 📋 Pre-Deployment Checklist

Before starting AWS deployment, ensure:

- [ ] ✅ Application runs successfully on local machine
- [ ] ✅ All features tested locally
- [ ] ✅ Backend tests pass
- [ ] ✅ Frontend builds without errors
- [ ] ✅ Database seeds work correctly
- [ ] ✅ Ollama responds to queries
- [ ] ✅ AWS account created
- [ ] ✅ Credit card added to AWS account
- [ ] ✅ AWS CLI installed (optional but recommended)

---

## 🎯 Deployment Strategy

We'll deploy in this order:

1. **Database First** (RDS PostgreSQL) - 30 min
2. **Backend Server** (EC2 + Ollama) - 60 min
3. **Frontend** (S3 + CloudFront) - 30 min
4. **Testing** - 30 min
5. **SSL/Domain** (Optional) - 30 min

**Total Time: ~3-4 hours**

---

## 📚 Your Deployment Guides

I've created three guides for you:

### 1. **AWS_MVP_DEPLOYMENT_GUIDE.md** ⭐ START HERE
   - Complete step-by-step instructions
   - Every command you need
   - Troubleshooting for each step
   - **Use this as your main guide**

### 2. **AWS_DEPLOYMENT_CHECKLIST.md**
   - Quick reference checklist
   - Track your progress
   - Verification commands
   - **Use this to track completion**

### 3. **AWS_DEPLOYMENT_GUIDE.md**
   - Alternative deployment approach
   - Additional context
   - **Reference if needed**

---

## 🚦 Step-by-Step Deployment Process

### Phase 1: Prepare for Deployment (15 minutes)

#### 1.1 Test Local Build

```cmd
# Test backend
cd backend
.venv\Scripts\activate
python -c "from database import init_db; print('Backend OK')"

# Test frontend build
cd ..\frontend
npm run build
```

If both succeed, you're ready! ✅

#### 1.2 Gather Information

Create a file `deployment-info.txt` and fill in as you go:

```txt
=== AWS DEPLOYMENT INFO ===

AWS Account ID: __________________
AWS Region: us-east-1 (or your choice)

=== DATABASE ===
RDS Endpoint: ____________________
Database Name: nyaya_mitra
Username: nyaya_admin
Password: ____________________

=== EC2 INSTANCE ===
Instance ID: ____________________
Public IP: ____________________
Public DNS: ____________________
SSH Key: nyaya-mitra-key.pem

=== S3 BUCKET ===
Bucket Name: ____________________
Website URL: ____________________

=== CLOUDFRONT ===
Distribution ID: ____________________
CloudFront URL: ____________________

=== DOMAIN (Optional) ===
Domain Name: ____________________
```

---

### Phase 2: Deploy Database (30 minutes)

**Open:** `AWS_MVP_DEPLOYMENT_GUIDE.md` → Part 1

**Quick Steps:**
1. Go to AWS Console → RDS
2. Create PostgreSQL database (db.t3.micro)
3. Save endpoint and credentials
4. Configure security group

**Verification:**
```cmd
# You'll test this from EC2 later
```

✅ **Checkpoint:** RDS endpoint saved in `deployment-info.txt`

---

### Phase 3: Deploy Backend (60 minutes)

**Open:** `AWS_MVP_DEPLOYMENT_GUIDE.md` → Part 2 & 3

**Quick Steps:**

#### 3.1 Launch EC2 (15 min)
1. Go to AWS Console → EC2
2. Launch Ubuntu 22.04 instance (t3.large)
3. Download SSH key
4. Configure security groups
5. Save public IP

#### 3.2 Connect and Setup (45 min)
```cmd
# Connect to EC2
ssh -i nyaya-mitra-key.pem ubuntu@<your-ec2-ip>

# Follow Part 3 of the guide:
# - Install Python, Ollama
# - Download Mistral model
# - Upload backend code
# - Configure .env
# - Initialize database
# - Start services
```

**Verification:**
```cmd
curl http://<your-ec2-ip>/health
```

Should return: `{"status":"ok"}`

✅ **Checkpoint:** Backend API responding at `http://<ec2-ip>/health`

---

### Phase 4: Deploy Frontend (30 minutes)

**Open:** `AWS_MVP_DEPLOYMENT_GUIDE.md` → Part 4

**Quick Steps:**

#### 4.1 Build Frontend Locally
```cmd
cd frontend

# Update API URL
echo VITE_API_URL=http://<your-ec2-ip> > .env.production

# Build
npm run build
```

#### 4.2 Create S3 Bucket
1. Go to AWS Console → S3
2. Create bucket: `nyaya-mitra-frontend-<random>`
3. Enable static website hosting
4. Set bucket policy (public read)

#### 4.3 Upload Files
```cmd
# Using AWS CLI
aws s3 sync dist/ s3://your-bucket-name/ --delete

# Or upload via AWS Console
```

**Verification:**
Open: `http://your-bucket-name.s3-website-us-east-1.amazonaws.com`

✅ **Checkpoint:** Frontend loads in browser

---

### Phase 5: Setup CloudFront (Optional, 20 minutes)

**Open:** `AWS_MVP_DEPLOYMENT_GUIDE.md` → Part 4.6

**Quick Steps:**
1. Go to AWS Console → CloudFront
2. Create distribution
3. Origin: Your S3 bucket
4. Enable HTTPS redirect
5. Configure error pages (403, 404 → index.html)
6. Wait for deployment (10-15 min)

**Verification:**
Open: `https://your-distribution-id.cloudfront.net`

✅ **Checkpoint:** Frontend loads via HTTPS

---

### Phase 6: End-to-End Testing (30 minutes)

**Test Checklist:**

#### Backend Tests
```cmd
# Health check
curl http://<ec2-ip>/health

# Register user
curl -X POST http://<ec2-ip>/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","full_name":"Test User"}'

# Login
curl -X POST http://<ec2-ip>/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'
```

#### Frontend Tests
- [ ] Open frontend URL
- [ ] Register new account
- [ ] Login
- [ ] Test Chat (ask a legal question)
- [ ] Test Case Analyzer
- [ ] Test Document Generator
- [ ] Test Legal Aid Search
- [ ] Test Evidence Guide
- [ ] Test Emergency SOS

#### Integration Tests
- [ ] Frontend can call backend API
- [ ] Authentication works end-to-end
- [ ] Ollama responds to chat queries
- [ ] Database stores data correctly

✅ **Checkpoint:** All features working!

---

### Phase 7: Security & Monitoring (20 minutes)

**Open:** `AWS_MVP_DEPLOYMENT_GUIDE.md` → Part 8

**Quick Steps:**

#### 7.1 Security
- [ ] Change all default passwords
- [ ] Restrict SSH to your IP only
- [ ] Verify RDS is not publicly accessible
- [ ] Review security group rules

#### 7.2 Backups
```cmd
# Create RDS snapshot
aws rds create-db-snapshot \
  --db-instance-identifier nyaya-mitra-db \
  --db-snapshot-identifier initial-backup

# Create EC2 AMI
aws ec2 create-image \
  --instance-id <your-instance-id> \
  --name "nyaya-mitra-backend-backup"
```

#### 7.3 Monitoring
- [ ] Set up AWS Budget alert ($50/month)
- [ ] Enable CloudWatch logs
- [ ] Test backup restoration

✅ **Checkpoint:** Security measures in place

---

## 🎉 Deployment Complete!

### Your Live URLs:

```
Backend API: http://<ec2-ip>:8000
API Docs: http://<ec2-ip>:8000/docs
Frontend: https://<cloudfront-url>
```

### Save These for Later:

1. **EC2 SSH Command:**
   ```cmd
   ssh -i nyaya-mitra-key.pem ubuntu@<ec2-ip>
   ```

2. **View Backend Logs:**
   ```cmd
   ssh -i nyaya-mitra-key.pem ubuntu@<ec2-ip>
   sudo journalctl -u nyaya-mitra-backend -f
   ```

3. **Restart Backend:**
   ```cmd
   ssh -i nyaya-mitra-key.pem ubuntu@<ec2-ip>
   sudo systemctl restart nyaya-mitra-backend
   ```

4. **Update Frontend:**
   ```cmd
   cd frontend
   npm run build
   aws s3 sync dist/ s3://your-bucket/ --delete
   aws cloudfront create-invalidation --distribution-id <id> --paths "/*"
   ```

---

## 💰 Cost Tracking

**Expected Monthly Costs:**

| Service | Cost |
|---------|------|
| EC2 t3.large | $60 |
| RDS db.t3.micro | $15 (Free tier: $0) |
| S3 Storage | $1 |
| CloudFront | $10 (Free tier: $0) |
| Data Transfer | $10 |
| **Total** | **~$95/month** |
| **With Free Tier** | **~$75/month** |

**Cost Saving Tips:**
- Stop EC2 when not in use (saves ~$60/month)
- Use Spot Instances (save up to 90%)
- Monitor with AWS Cost Explorer

---

## 🆘 Need Help?

### Common Issues:

**Backend not responding:**
```cmd
ssh -i nyaya-mitra-key.pem ubuntu@<ec2-ip>
sudo systemctl status nyaya-mitra-backend
sudo systemctl restart nyaya-mitra-backend
```

**Database connection failed:**
- Check security group allows EC2
- Verify DATABASE_URL in .env
- Test: `psql -h <rds-endpoint> -U nyaya_admin -d nyaya_mitra`

**Ollama not working:**
```cmd
sudo systemctl status ollama
sudo systemctl restart ollama
ollama list
```

**Frontend not loading:**
- Clear CloudFront cache
- Check S3 bucket policy
- Verify files uploaded correctly

### Get Detailed Help:

1. **For step-by-step instructions:** Open `AWS_MVP_DEPLOYMENT_GUIDE.md`
2. **For troubleshooting:** See Part 9 of the guide
3. **For checklist:** Use `AWS_DEPLOYMENT_CHECKLIST.md`

---

## 📝 Post-Deployment Tasks

### Immediate (Today):
- [ ] Test all features thoroughly
- [ ] Monitor logs for errors
- [ ] Check AWS costs
- [ ] Document any issues

### This Week:
- [ ] Set up custom domain (optional)
- [ ] Configure SSL certificate
- [ ] Add monitoring alerts
- [ ] Create backup schedule

### This Month:
- [ ] Review and optimize costs
- [ ] Plan scaling strategy
- [ ] Gather user feedback
- [ ] Update documentation

---

## 🎯 Next Steps

### For Production:
1. Add Redis for caching
2. Set up CI/CD pipeline
3. Add load balancer
4. Enable auto-scaling
5. Implement comprehensive monitoring
6. Add staging environment

### For Scaling:
1. Use RDS Multi-AZ
2. Add read replicas
3. Use ElastiCache
4. Implement CDN for static assets
5. Consider ECS/EKS for containers

---

## 📞 Support Resources

- **AWS Documentation:** https://docs.aws.amazon.com
- **AWS Support:** https://console.aws.amazon.com/support
- **AWS Status:** https://status.aws.amazon.com
- **Ollama Docs:** https://ollama.ai/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com

---

## ✅ Deployment Success Criteria

Your deployment is successful when:

- [x] Backend API responds to health checks
- [x] Database is accessible and seeded
- [x] Ollama generates AI responses
- [x] Frontend loads in browser
- [x] Users can register and login
- [x] All features work end-to-end
- [x] HTTPS is enabled (via CloudFront)
- [x] Backups are configured
- [x] Monitoring is active
- [x] Costs are within budget

---

**🚀 Ready to deploy? Start with `AWS_MVP_DEPLOYMENT_GUIDE.md` Part 1!**

**Good luck! You've got this! 💪**
