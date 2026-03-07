# Nyaya Mitra - AWS Deployment Documentation

Complete deployment documentation for deploying Nyaya Mitra to AWS with Bedrock AI.

## 📁 Documentation Structure

```
.
├── START_HERE_DEPLOYMENT.md              ← Start here! Overview and getting started
├── AWS_BEDROCK_DEPLOYMENT_GUIDE.md       ← Complete step-by-step deployment guide
├── DEPLOYMENT_QUICK_START.md             ← Quick reference with commands
├── DEPLOYMENT_CHECKLIST.md               ← Track your deployment progress
├── DEPLOYMENT_TROUBLESHOOTING.md         ← Solutions to common problems
├── pre-deployment-check.bat              ← Automated prerequisite checker
├── update-frontend.bat                   ← Update frontend after deployment
└── update-backend-remote.bat             ← Update backend after deployment
```

## 🚀 Quick Start

### For First-Time Deployment

1. **Read the overview**
   ```
   START_HERE_DEPLOYMENT.md
   ```

2. **Run prerequisite check**
   ```bash
   pre-deployment-check.bat
   ```

3. **Follow the main guide**
   ```
   AWS_BEDROCK_DEPLOYMENT_GUIDE.md
   ```

4. **Track your progress**
   ```
   DEPLOYMENT_CHECKLIST.md
   ```

### For Updates After Deployment

**Update Frontend:**
```bash
update-frontend.bat
```

**Update Backend:**
```bash
update-backend-remote.bat
```

## 📖 Document Descriptions

### START_HERE_DEPLOYMENT.md
- **Purpose**: Overview and getting started guide
- **When to use**: First document to read before deployment
- **Contents**:
  - Documentation overview
  - Quick start steps
  - Key differences from standard setup
  - Success criteria
  - Support resources

### AWS_BEDROCK_DEPLOYMENT_GUIDE.md
- **Purpose**: Complete step-by-step deployment instructions
- **When to use**: Main reference during deployment
- **Contents**:
  - Architecture overview
  - Detailed setup for each AWS service
  - Configuration examples
  - Testing procedures
  - Maintenance instructions
- **Estimated time**: 3-4 hours

### DEPLOYMENT_QUICK_START.md
- **Purpose**: Condensed version with essential commands
- **When to use**: Quick reference during deployment
- **Contents**:
  - 5-step deployment process
  - Environment variable templates
  - Common commands
  - Testing checklist
  - Troubleshooting quick tips

### DEPLOYMENT_CHECKLIST.md
- **Purpose**: Track deployment progress
- **When to use**: Throughout deployment process
- **Contents**:
  - Phase-by-phase checklist
  - Credential tracking
  - Test results tracking
  - Timeline estimates
  - Quick reference commands

### DEPLOYMENT_TROUBLESHOOTING.md
- **Purpose**: Solutions to common deployment issues
- **When to use**: When encountering problems
- **Contents**:
  - AWS Bedrock issues
  - Database connection problems
  - Backend service issues
  - Frontend problems
  - Network and security issues
  - Cost and billing issues

### pre-deployment-check.bat
- **Purpose**: Automated prerequisite verification
- **When to use**: Before starting deployment
- **Checks**:
  - AWS CLI installed
  - Node.js installed
  - Python installed
  - Git installed
  - AWS credentials configured
  - Project files present

### update-frontend.bat
- **Purpose**: Rebuild and redeploy frontend
- **When to use**: After making frontend changes
- **Actions**:
  - Builds React app
  - Uploads to S3
  - Sets cache headers
  - Invalidates CloudFront cache

### update-backend-remote.bat
- **Purpose**: Update backend code on EC2
- **When to use**: After making backend changes
- **Actions**:
  - Uploads code to EC2
  - Creates backup
  - Updates dependencies
  - Restarts service
  - Verifies health

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     User's Browser                       │
└────────────────────────┬────────────────────────────────┘
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────┐
│              CloudFront CDN (Global)                     │
│              - HTTPS enabled                             │
│              - Caching enabled                           │
│              - Error page handling                       │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                S3 Bucket (Frontend)                      │
│                - Static website hosting                  │
│                - React app (built)                       │
└─────────────────────────────────────────────────────────┘

                         │ API Calls
                         ▼
┌─────────────────────────────────────────────────────────┐
│              EC2 Instance (t3.small)                     │
│              ┌─────────────────────────────┐            │
│              │  Nginx (Reverse Proxy)      │            │
│              └──────────┬──────────────────┘            │
│                         │                                │
│              ┌──────────▼──────────────────┐            │
│              │  FastAPI Backend            │            │
│              │  - Python 3.11              │            │
│              │  - Uvicorn (2 workers)      │            │
│              │  - JWT authentication       │            │
│              │  - Rate limiting            │            │
│              └──────────┬──────────────────┘            │
└─────────────────────────┼────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ RDS          │  │ AWS Bedrock  │  │ ChromaDB     │
│ PostgreSQL   │  │ Claude 3     │  │ (Vector DB)  │
│ db.t3.micro  │  │ Haiku        │  │ (Local)      │
│              │  │              │  │              │
│ - User data  │  │ - AI chat    │  │ - Legal docs │
│ - Cases      │  │ - Analysis   │  │ - RAG system │
│ - Documents  │  │ - Generation │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
```

## 💰 Cost Breakdown

### Monthly Costs (with $200 credits)

| Service | Configuration | Cost/Month | Notes |
|---------|--------------|------------|-------|
| EC2 | t3.small (24/7) | ~$15 | Can stop when not needed |
| RDS | db.t3.micro | ~$15 | Free tier eligible for 12 months |
| S3 | 5GB storage | ~$0.12 | Mostly free tier |
| CloudFront | 100GB transfer | ~$8.50 | Free tier: 1TB/month for 12 months |
| Bedrock | Claude 3 Haiku | ~$10-20 | Pay per use (tokens) |
| Data Transfer | Outbound | ~$5 | First 100GB free |
| **Total** | | **~$45-55** | **$200 credits = 3-4 months** |

### Cost Optimization Tips

1. **Stop EC2 when not needed**
   ```bash
   aws ec2 stop-instances --instance-ids <id>
   ```
   Saves ~$15/month when stopped

2. **Stop RDS when not needed**
   ```bash
   aws rds stop-db-instance --db-instance-identifier nyaya-mitra-db
   ```
   Saves ~$15/month when stopped

3. **Optimize Bedrock usage**
   - Implement caching for common queries
   - Use rate limiting (already implemented)
   - Monitor token usage in CloudWatch

4. **Use CloudFront caching**
   - Reduces backend load
   - Reduces data transfer costs
   - Already configured in deployment

## 🔒 Security Features

### Implemented Security Measures

1. **Network Security**
   - RDS not publicly accessible
   - Security groups with minimal permissions
   - SSH restricted to specific IPs
   - HTTPS via CloudFront

2. **Application Security**
   - JWT authentication
   - Password hashing (bcrypt)
   - Rate limiting (100 requests/hour)
   - Session timeout (30 minutes)
   - CORS configuration
   - Security headers middleware

3. **Data Security**
   - Database encryption at rest
   - TLS for data in transit
   - Encrypted backups
   - S3 bucket encryption

4. **AWS Security**
   - IAM users with minimal permissions
   - Access keys rotation recommended
   - CloudWatch monitoring
   - Automated backups

## 📊 Monitoring and Maintenance

### Daily Checks (First Week)

```bash
# Check costs
aws ce get-cost-and-usage \
  --time-period Start=2026-03-01,End=2026-03-07 \
  --granularity DAILY \
  --metrics BlendedCost

# Check backend health
curl http://<ec2-ip>/health

# Check logs
ssh -i key.pem ubuntu@<ec2-ip>
sudo journalctl -u nyaya-mitra-backend -n 50
```

### Weekly Maintenance

1. **Review CloudWatch metrics**
   - CPU utilization
   - Memory usage
   - Bedrock token usage
   - Error rates

2. **Check backups**
   - RDS automated backups
   - Create manual snapshots

3. **Update dependencies**
   - Security patches
   - Package updates

4. **Review costs**
   - Compare to budget
   - Identify optimization opportunities

### Monthly Maintenance

1. **Create backups**
   ```bash
   # RDS snapshot
   aws rds create-db-snapshot \
     --db-instance-identifier nyaya-mitra-db \
     --db-snapshot-identifier backup-$(date +%Y%m%d)
   
   # EC2 AMI
   aws ec2 create-image \
     --instance-id <id> \
     --name "backup-$(date +%Y%m%d)"
   ```

2. **Review security**
   - Check security group rules
   - Review IAM permissions
   - Rotate access keys

3. **Performance optimization**
   - Analyze slow queries
   - Review cache hit rates
   - Optimize Bedrock usage

## 🧪 Testing Procedures

### After Initial Deployment

1. **Backend Tests**
   ```bash
   # Health check
   curl http://<ec2-ip>/health
   
   # Database health
   curl http://<ec2-ip>/db-health
   
   # API docs
   open http://<ec2-ip>/docs
   ```

2. **Frontend Tests**
   - Load in browser
   - Check console for errors
   - Test responsive design
   - Verify HTTPS

3. **Feature Tests**
   - User registration
   - User login
   - Chat (Bedrock integration)
   - Case analyzer
   - Document generator
   - Legal aid search
   - Evidence guide
   - Emergency SOS

4. **Integration Tests**
   - End-to-end user flow
   - Multi-language support
   - File uploads
   - Document downloads

### Performance Tests

```bash
# Load testing (use Apache Bench)
ab -n 100 -c 10 http://<ec2-ip>/health

# Monitor during load
ssh -i key.pem ubuntu@<ec2-ip>
top
```

## 🆘 Support and Resources

### Documentation
- **AWS Bedrock**: https://docs.aws.amazon.com/bedrock
- **AWS EC2**: https://docs.aws.amazon.com/ec2
- **AWS RDS**: https://docs.aws.amazon.com/rds
- **FastAPI**: https://fastapi.tiangolo.com
- **React**: https://react.dev

### Community
- **AWS Forums**: https://forums.aws.amazon.com
- **Stack Overflow**: Tag with `amazon-bedrock`, `fastapi`, `react`
- **GitHub Issues**: For project-specific issues

### AWS Support
- **Service Health**: https://status.aws.amazon.com
- **Support Center**: https://console.aws.amazon.com/support
- **Billing Support**: Always free

## 📝 Deployment Timeline

### Typical Deployment Schedule

```
Hour 0:00 - Pre-deployment check (15 min)
Hour 0:15 - Enable Bedrock, create IAM (15 min)
Hour 0:30 - Create RDS database (30 min, mostly waiting)
Hour 1:00 - Launch EC2 instance (15 min)
Hour 1:15 - Configure security groups (15 min)
Hour 1:30 - Deploy backend (90 min)
         - Install dependencies
         - Configure environment
         - Initialize database
         - Setup services
         - Configure Nginx
Hour 3:00 - Deploy frontend (45 min)
         - Build locally
         - Create S3 bucket
         - Upload files
         - Setup CloudFront
Hour 3:45 - Testing (30 min)
         - Test all features
         - Verify integration
         - Check security
Hour 4:15 - Setup monitoring (15 min)
         - Budget alerts
         - CloudWatch
Hour 4:30 - DEPLOYMENT COMPLETE! 🎉
```

## 🎯 Success Metrics

### Deployment Success

- [ ] All services running
- [ ] All features functional
- [ ] No errors in logs
- [ ] HTTPS working
- [ ] Costs within budget
- [ ] Backups configured
- [ ] Monitoring enabled

### Application Success

- [ ] Users can register/login
- [ ] Chat responds within 5 seconds
- [ ] Documents generate correctly
- [ ] Search returns results
- [ ] Mobile responsive
- [ ] Multi-language works

### Business Success

- [ ] User feedback positive
- [ ] No critical bugs
- [ ] Performance acceptable
- [ ] Costs sustainable
- [ ] Scalability proven

## 🔄 Update Procedures

### Updating Frontend

```bash
# Make changes to frontend code
cd frontend
# Edit files...

# Run update script
cd ..
update-frontend.bat

# Enter S3 bucket name and CloudFront ID when prompted
```

### Updating Backend

```bash
# Make changes to backend code
cd backend
# Edit files...

# Run update script
cd ..
update-backend-remote.bat

# Enter EC2 IP and key file path when prompted
```

### Rolling Back

**Frontend:**
```bash
# S3 versioning is enabled
aws s3api list-object-versions --bucket <bucket-name>
aws s3api get-object --bucket <bucket-name> --key index.html --version-id <version-id> index.html
```

**Backend:**
```bash
# SSH to EC2
ssh -i key.pem ubuntu@<ec2-ip>

# Restore from backup
sudo systemctl stop nyaya-mitra-backend
sudo rm -rf /opt/nyaya-mitra/backend
sudo mv /opt/nyaya-mitra/backend.backup.YYYYMMDD /opt/nyaya-mitra/backend
sudo systemctl start nyaya-mitra-backend
```

## 📞 Getting Help

### Before Asking for Help

1. Check `DEPLOYMENT_TROUBLESHOOTING.md`
2. Review logs
3. Test components individually
4. Check AWS Service Health Dashboard

### When Asking for Help

Include:
- Error messages (full text)
- Relevant logs
- Steps to reproduce
- What you've already tried
- AWS region
- Service versions

### Where to Ask

1. **AWS Forums**: General AWS questions
2. **Stack Overflow**: Technical questions
3. **GitHub Issues**: Project-specific bugs
4. **AWS Support**: Billing or service issues

## 🎓 Learning Resources

### AWS Basics
- AWS Free Tier: https://aws.amazon.com/free
- AWS Training: https://aws.amazon.com/training
- AWS Documentation: https://docs.aws.amazon.com

### Bedrock
- Bedrock Workshop: https://catalog.workshops.aws/bedrock
- Bedrock Pricing: https://aws.amazon.com/bedrock/pricing
- Claude Documentation: https://docs.anthropic.com/claude

### FastAPI
- FastAPI Tutorial: https://fastapi.tiangolo.com/tutorial
- FastAPI Best Practices: https://github.com/zhanymkanov/fastapi-best-practices

### React
- React Tutorial: https://react.dev/learn
- React Router: https://reactrouter.com

## ✅ Final Checklist

Before going live:

- [ ] All documentation read
- [ ] Deployment completed successfully
- [ ] All tests passing
- [ ] Security checklist completed
- [ ] Monitoring configured
- [ ] Backups verified
- [ ] Budget alerts set
- [ ] Team trained
- [ ] Support plan in place
- [ ] Rollback procedure tested

---

**Ready to deploy? Start with `START_HERE_DEPLOYMENT.md`!**

**Questions? Check `DEPLOYMENT_TROUBLESHOOTING.md` or AWS documentation.**

**Good luck! 🚀**
