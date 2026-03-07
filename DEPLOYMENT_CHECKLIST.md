# Nyaya Mitra AWS Deployment Checklist

Use this checklist to track your deployment progress.

## Pre-Deployment

- [ ] AWS account created and verified
- [ ] $200 credits confirmed in billing
- [ ] AWS CLI installed locally
- [ ] Node.js 18+ installed locally
- [ ] Python 3.11+ installed locally
- [ ] Git repository accessible
- [ ] All passwords and secrets prepared

---

## Phase 1: AWS IAM & Bedrock Setup

- [ ] Bedrock model access enabled (Claude 3 Haiku)
- [ ] IAM user created: `nyaya-mitra-bedrock-user`
- [ ] Bedrock access keys generated and saved
- [ ] Access keys tested with AWS CLI

**Saved Credentials:**
```
AWS_ACCESS_KEY_ID: ________________
AWS_SECRET_ACCESS_KEY: ________________
```

---

## Phase 2: Database (RDS)

- [ ] RDS PostgreSQL instance created
- [ ] Instance identifier: `nyaya-mitra-db`
- [ ] Security group created: `nyaya-mitra-db-sg`
- [ ] Database endpoint noted
- [ ] Master password saved securely

**Database Details:**
```
Endpoint: ________________________________
Port: 5432
Database: nyaya_mitra
Username: nyaya_admin
Password: ________________
```

---

## Phase 3: EC2 Instance

- [ ] EC2 t3.small instance launched
- [ ] Instance name: `nyaya-mitra-backend`
- [ ] Security group created: `nyaya-mitra-backend-sg`
- [ ] SSH key pair downloaded: `nyaya-mitra-key.pem`
- [ ] Public IP address noted
- [ ] RDS security group updated to allow EC2 access

**EC2 Details:**
```
Instance ID: ________________
Public IP: ________________
Key file location: ________________
```

---

## Phase 4: Backend Deployment

- [ ] Connected to EC2 via SSH
- [ ] Python 3.11 installed
- [ ] Application code uploaded/cloned
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] spaCy model downloaded
- [ ] .env file configured with all variables
- [ ] JWT secret generated
- [ ] Database initialized successfully
- [ ] Emergency contacts seeded
- [ ] Legal aid providers seeded (if available)
- [ ] Backend tested locally on EC2
- [ ] Systemd service created and enabled
- [ ] Backend service started successfully
- [ ] Nginx installed and configured
- [ ] Backend accessible from internet

**Test Results:**
```
Health check: [ ] Pass [ ] Fail
DB health check: [ ] Pass [ ] Fail
API docs accessible: [ ] Pass [ ] Fail
```

---

## Phase 5: Frontend Deployment

- [ ] Frontend dependencies installed locally
- [ ] .env.production file created
- [ ] Frontend built successfully
- [ ] S3 bucket created
- [ ] Bucket name noted
- [ ] Static website hosting enabled
- [ ] Bucket policy configured
- [ ] Files uploaded to S3
- [ ] CloudFront distribution created
- [ ] CloudFront URL noted
- [ ] Error pages configured (403, 404)
- [ ] Backend CORS updated with CloudFront URL
- [ ] Backend service restarted

**Frontend Details:**
```
S3 Bucket: ________________________________
CloudFront URL: ________________________________
```

---

## Phase 6: Testing

- [ ] Frontend loads in browser
- [ ] User registration works
- [ ] User login works
- [ ] Chat feature works (Bedrock integration)
- [ ] Case Analyzer works
- [ ] Document Generator works
- [ ] Legal Aid Search works
- [ ] Evidence Guide works
- [ ] Emergency SOS works
- [ ] Language switching works
- [ ] Mobile responsive design verified

---

## Phase 7: Monitoring & Security

- [ ] AWS Budget alert created ($50/month)
- [ ] Cost Explorer enabled
- [ ] CloudWatch metrics reviewed
- [ ] Bedrock usage monitored
- [ ] All default passwords changed
- [ ] SSH access restricted to your IP
- [ ] HTTPS enabled via CloudFront
- [ ] Security groups reviewed
- [ ] RDS automated backups verified
- [ ] EC2 AMI backup created

---

## Phase 8: Documentation

- [ ] All credentials saved in password manager
- [ ] Deployment notes documented
- [ ] Team members notified
- [ ] User testing plan created
- [ ] Feedback collection method established

---

## Post-Deployment (First Week)

- [ ] Day 1: Monitor costs and usage
- [ ] Day 2: Check error logs
- [ ] Day 3: Review Bedrock token usage
- [ ] Day 4: Test all features again
- [ ] Day 5: Gather initial user feedback
- [ ] Day 6: Review CloudWatch metrics
- [ ] Day 7: Create weekly backup

---

## Estimated Timeline

- **Phase 1-2 (IAM + RDS):** 30 minutes
- **Phase 3 (EC2):** 15 minutes
- **Phase 4 (Backend):** 60-90 minutes
- **Phase 5 (Frontend):** 45 minutes
- **Phase 6 (Testing):** 30 minutes
- **Phase 7 (Monitoring):** 20 minutes

**Total: 3-4 hours**

---

## Quick Reference Commands

### Connect to EC2
```bash
ssh -i nyaya-mitra-key.pem ubuntu@<ec2-ip>
```

### Check Backend Status
```bash
sudo systemctl status nyaya-mitra-backend
sudo journalctl -u nyaya-mitra-backend -f
```

### Restart Backend
```bash
sudo systemctl restart nyaya-mitra-backend
```

### Update Frontend
```bash
cd frontend
npm run build
aws s3 sync dist/ s3://your-bucket-name/ --delete
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

### Check Costs
```bash
aws ce get-cost-and-usage \
  --time-period Start=2026-03-01,End=2026-03-07 \
  --granularity DAILY \
  --metrics BlendedCost
```

---

## Emergency Contacts

**AWS Support:** https://console.aws.amazon.com/support/
**Billing Issues:** https://console.aws.amazon.com/billing/

---

## Notes

_Use this space for deployment-specific notes:_

```
[Your notes here]
```

---

**Status:** [ ] Not Started [ ] In Progress [ ] Completed [ ] Issues

**Deployment Date:** _______________
**Deployed By:** _______________
**Production URL:** _______________
