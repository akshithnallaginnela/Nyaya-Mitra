# AWS Deployment Checklist - Nyaya Mitra MVP

Use this checklist to track your deployment progress.

## Pre-Deployment

- [ ] AWS account created and billing enabled
- [ ] AWS CLI installed and configured
- [ ] Domain name purchased (optional)
- [ ] SSH key pair generated
- [ ] Code repository ready

---

## Phase 1: Database (30 minutes)

- [ ] RDS PostgreSQL instance created (db.t3.micro)
- [ ] Database credentials saved securely
- [ ] Security group created (`nyaya-mitra-db-sg`)
- [ ] Database endpoint noted
- [ ] Backup retention configured (7 days)

**Verification:**
```bash
# Test connection (from EC2 later)
psql -h <rds-endpoint> -U nyaya_admin -d nyaya_mitra
```

---

## Phase 2: EC2 Instance (45 minutes)

- [ ] EC2 instance launched (t3.large, Ubuntu 22.04)
- [ ] Security group created (`nyaya-mitra-backend-sg`)
- [ ] SSH key downloaded and secured
- [ ] Public IP/DNS noted
- [ ] RDS security group updated to allow EC2 access

**Verification:**
```bash
ssh -i nyaya-mitra-key.pem ubuntu@<ec2-ip>
```

---

## Phase 3: Backend Setup (60 minutes)

- [ ] Connected to EC2 via SSH
- [ ] System updated (`apt update && apt upgrade`)
- [ ] Python 3.11 installed
- [ ] Ollama installed
- [ ] Mistral 7B model downloaded
- [ ] Backend code uploaded/cloned
- [ ] Virtual environment created
- [ ] Python dependencies installed
- [ ] spaCy model downloaded
- [ ] `.env` file created with all variables
- [ ] JWT secret generated
- [ ] Encryption key generated
- [ ] Database initialized
- [ ] Emergency contacts seeded
- [ ] Legal aid providers seeded
- [ ] Backend systemd service created
- [ ] Ollama systemd service created
- [ ] Both services started and enabled
- [ ] Nginx installed and configured
- [ ] Nginx restarted

**Verification:**
```bash
# Check services
sudo systemctl status nyaya-mitra-backend
sudo systemctl status ollama
sudo systemctl status nginx

# Test API
curl http://localhost:8000/health
curl http://<ec2-ip>/health
```

---

## Phase 4: Frontend Setup (30 minutes)

- [ ] Frontend built locally (`npm run build`)
- [ ] API URL configured in `.env.production`
- [ ] S3 bucket created (`nyaya-mitra-frontend`)
- [ ] Bucket configured for static website hosting
- [ ] Bucket policy added (public read)
- [ ] Frontend files uploaded to S3
- [ ] S3 website endpoint tested

**Verification:**
```bash
# Test S3 website
curl http://nyaya-mitra-frontend.s3-website-us-east-1.amazonaws.com
```

---

## Phase 5: CloudFront (Optional, 20 minutes)

- [ ] CloudFront distribution created
- [ ] Origin set to S3 bucket
- [ ] HTTPS redirect enabled
- [ ] Error pages configured (403, 404 → index.html)
- [ ] Distribution deployed (wait 10-15 min)
- [ ] CloudFront URL tested

**Verification:**
```bash
# Test CloudFront
curl https://<cloudfront-url>
```

---

## Phase 6: SSL/TLS (Optional, 30 minutes)

- [ ] Domain DNS configured
- [ ] SSL certificate requested in ACM (us-east-1)
- [ ] DNS validation records added
- [ ] Certificate validated
- [ ] Certificate attached to CloudFront
- [ ] Route 53 hosted zone created
- [ ] A record created (alias to CloudFront)
- [ ] CNAME record created (www)

**Verification:**
```bash
# Test custom domain
curl https://your-domain.com/health
```

---

## Phase 7: Testing (30 minutes)

### Backend Tests
- [ ] Health check endpoint works
- [ ] Database health check works
- [ ] User registration works
- [ ] User login works
- [ ] JWT token received
- [ ] Chat query works (tests Ollama)
- [ ] Case analysis works
- [ ] Document generation works
- [ ] Legal aid search works
- [ ] Evidence guide works
- [ ] Emergency contacts work

### Frontend Tests
- [ ] Website loads
- [ ] Registration page works
- [ ] Login page works
- [ ] Dashboard displays
- [ ] Chat interface works
- [ ] Case analyzer works
- [ ] Document generator works
- [ ] Legal aid search works
- [ ] Evidence guide works
- [ ] Emergency SOS works
- [ ] Language selector works

### Integration Tests
- [ ] Frontend can call backend API
- [ ] Authentication flow works end-to-end
- [ ] All features work together
- [ ] Mobile responsive design works
- [ ] CORS configured correctly

---

## Phase 8: Monitoring & Security (20 minutes)

- [ ] CloudWatch logs enabled
- [ ] AWS Budget alert created ($50/month)
- [ ] Cost Explorer enabled
- [ ] All passwords changed from defaults
- [ ] SSH restricted to your IP only
- [ ] RDS not publicly accessible
- [ ] Security groups reviewed
- [ ] Backup retention verified
- [ ] Manual RDS snapshot created
- [ ] EC2 AMI backup created

---

## Phase 9: Documentation (15 minutes)

- [ ] Connection details documented
- [ ] Credentials stored securely (password manager)
- [ ] Architecture diagram created
- [ ] Deployment notes written
- [ ] Known issues documented
- [ ] Troubleshooting guide reviewed

---

## Post-Deployment

### Day 1
- [ ] Monitor logs for errors
- [ ] Check CloudWatch metrics
- [ ] Test all features again
- [ ] Verify backups are working

### Week 1
- [ ] Review AWS costs
- [ ] Check for security alerts
- [ ] Monitor performance
- [ ] Gather user feedback

### Month 1
- [ ] Review and optimize costs
- [ ] Plan scaling strategy
- [ ] Update documentation
- [ ] Plan production deployment

---

## Quick Reference

### Important URLs
```
Backend API: http://<ec2-ip>:8000
API Docs: http://<ec2-ip>:8000/docs
Frontend (S3): http://<bucket-name>.s3-website-<region>.amazonaws.com
Frontend (CloudFront): https://<distribution-id>.cloudfront.net
Custom Domain: https://your-domain.com
```

### Important Commands

**SSH to EC2:**
```bash
ssh -i nyaya-mitra-key.pem ubuntu@<ec2-ip>
```

**Check Backend Status:**
```bash
sudo systemctl status nyaya-mitra-backend
sudo journalctl -u nyaya-mitra-backend -f
```

**Restart Backend:**
```bash
sudo systemctl restart nyaya-mitra-backend
```

**Update Frontend:**
```bash
# Build locally
npm run build

# Upload to S3
aws s3 sync dist/ s3://nyaya-mitra-frontend/ --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id <distribution-id> \
  --paths "/*"
```

**Database Backup:**
```bash
aws rds create-db-snapshot \
  --db-instance-identifier nyaya-mitra-db \
  --db-snapshot-identifier backup-$(date +%Y%m%d)
```

**View Costs:**
```bash
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost
```

---

## Troubleshooting Quick Fixes

**Backend not responding:**
```bash
sudo systemctl restart nyaya-mitra-backend
sudo systemctl restart nginx
```

**Ollama not working:**
```bash
sudo systemctl restart ollama
ollama list  # Verify model is loaded
```

**Database connection failed:**
```bash
# Check security group allows EC2
# Test connection
psql -h <rds-endpoint> -U nyaya_admin -d nyaya_mitra
```

**Frontend not loading:**
```bash
# Clear CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id <id> --paths "/*"
```

---

## Emergency Contacts

- AWS Support: https://console.aws.amazon.com/support
- AWS Status: https://status.aws.amazon.com
- Billing Support: https://console.aws.amazon.com/billing

---

## Estimated Timeline

- **Total Setup Time:** 4-5 hours
- **Testing Time:** 1-2 hours
- **Total:** 5-7 hours for complete MVP deployment

---

## Cost Tracking

| Service | Monthly Cost | Notes |
|---------|-------------|-------|
| EC2 t3.large | $60.74 | Can stop when not in use |
| RDS db.t3.micro | $14.60 | Free tier: $0 for 12 months |
| EBS Storage | $3.00 | 30GB |
| S3 Storage | $0.12 | Free tier: $0 for 12 months |
| CloudFront | $8.50 | Free tier: $0 for 12 months |
| Data Transfer | $9.00 | Varies by usage |
| **Total** | **~$95/month** | **~$75/month with free tier** |

---

## Success Criteria

✅ All services running without errors
✅ All features tested and working
✅ Frontend accessible via HTTPS
✅ Backend API responding correctly
✅ Database connected and seeded
✅ Ollama generating responses
✅ Monitoring and alerts configured
✅ Backups enabled and tested
✅ Security best practices followed
✅ Documentation complete

---

## Next Steps After MVP

1. Add Redis for caching
2. Set up CI/CD pipeline
3. Add load balancer for high availability
4. Enable auto-scaling
5. Add comprehensive monitoring
6. Implement log aggregation
7. Set up staging environment
8. Add performance testing
9. Optimize Ollama performance
10. Plan production scaling

---

**Good luck with your deployment! 🚀**
