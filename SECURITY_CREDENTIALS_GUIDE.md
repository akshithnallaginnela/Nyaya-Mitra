# Security & Credentials Management Guide

## 🔒 Important Security Information

### Files That Should NEVER Be Committed to Git

The following files contain sensitive information and are in `.gitignore`:

1. **aws-credentials.ps1** - Your AWS access keys
2. **deployment-info.json** - Database passwords, JWT secrets, endpoints
3. **nyaya-mitra-key.pem** - SSH private key for EC2 access
4. **backend/.env** - Backend environment variables with secrets

### How Credentials Are Managed

#### AWS Credentials

AWS credentials are stored in `aws-credentials.ps1` (NOT in Git):

```powershell
# aws-credentials.ps1
$env:AWS_ACCESS_KEY_ID = "YOUR_ACCESS_KEY"
$env:AWS_SECRET_ACCESS_KEY = "YOUR_SECRET_KEY"
$env:AWS_DEFAULT_REGION = "us-east-1"
```

All deployment scripts load credentials from this file:
```powershell
. .\aws-credentials.ps1
```

#### Deployment Information

Sensitive deployment data is stored in `deployment-info.json` (NOT in Git):
- Database passwords
- JWT secrets
- RDS endpoints
- EC2 instance IDs

### Setting Up Credentials

#### First Time Setup

1. **Create aws-credentials.ps1**:
   ```powershell
   # Copy from aws-credentials.ps1.example
   cp aws-credentials.ps1.example aws-credentials.ps1
   
   # Edit with your credentials
   notepad aws-credentials.ps1
   ```

2. **Verify .gitignore**:
   ```bash
   # These should be in .gitignore:
   aws-credentials.ps1
   deployment-info.json
   *.pem
   backend/.env
   ```

3. **Never commit secrets**:
   ```bash
   # Before committing, check:
   git status
   
   # Ensure no sensitive files are staged
   ```

### Rotating AWS Credentials

If credentials are ever exposed:

1. **Immediately create new credentials**:
   - AWS Console → IAM → Users → Your User → Security credentials
   - Create access key
   - Delete old key

2. **Update aws-credentials.ps1**:
   ```powershell
   $env:AWS_ACCESS_KEY_ID = "NEW_KEY"
   $env:AWS_SECRET_ACCESS_KEY = "NEW_SECRET"
   ```

3. **Update deployed backend** (if already deployed):
   ```powershell
   # SSH to EC2
   ssh -i nyaya-mitra-key.pem ubuntu@<ec2-ip>
   
   # Edit .env file
   nano /opt/nyaya-mitra/backend/.env
   
   # Update AWS credentials
   # Restart service
   sudo systemctl restart nyaya-mitra-backend
   ```

### Best Practices

#### ✅ DO

- Store credentials in separate files (aws-credentials.ps1, .env)
- Add sensitive files to .gitignore
- Use environment variables
- Rotate credentials regularly
- Use IAM roles when possible (for EC2)
- Enable MFA on AWS account
- Use AWS Secrets Manager for production

#### ❌ DON'T

- Hardcode credentials in scripts
- Commit .env files to Git
- Share credentials via email/chat
- Use root AWS account credentials
- Give credentials more permissions than needed
- Reuse credentials across environments

### GitHub Push Protection

GitHub automatically scans for exposed secrets. If you see:

```
remote: - Push cannot contain secrets
remote: - Amazon AWS Access Key ID
```

**Actions to take:**

1. **Don't bypass the protection!**
2. **Rotate the exposed credentials immediately**
3. **Remove credentials from files**
4. **Use environment variables**
5. **Clean Git history if needed**

### Checking for Exposed Secrets

Before pushing to Git:

```powershell
# Search for potential secrets
git grep -i "AKIA"  # AWS Access Keys
git grep -i "password"
git grep -i "secret"

# Check what's being committed
git diff --cached
```

### Emergency: Credentials Exposed

If credentials are accidentally exposed:

1. **Rotate immediately** (create new, delete old)
2. **Check AWS CloudTrail** for unauthorized access
3. **Review AWS billing** for unexpected charges
4. **Update all systems** with new credentials
5. **Consider AWS Secrets Manager** for future

### Production Recommendations

For production deployments:

1. **Use AWS IAM Roles** for EC2 (no credentials needed)
2. **Use AWS Secrets Manager** for database passwords
3. **Use AWS Systems Manager Parameter Store** for configuration
4. **Enable AWS CloudTrail** for audit logging
5. **Set up AWS Config** for compliance monitoring
6. **Use separate AWS accounts** for dev/staging/prod

### IAM Role for EC2 (Recommended)

Instead of using access keys, attach an IAM role to EC2:

1. **Create IAM Role**:
   - AWS Console → IAM → Roles → Create role
   - Select "AWS service" → "EC2"
   - Attach policies: AmazonBedrockFullAccess
   - Name: nyaya-mitra-ec2-role

2. **Attach to EC2**:
   - EC2 Console → Instances → Select instance
   - Actions → Security → Modify IAM role
   - Select nyaya-mitra-ec2-role

3. **Remove credentials from .env**:
   ```bash
   # No longer needed:
   # AWS_ACCESS_KEY_ID=...
   # AWS_SECRET_ACCESS_KEY=...
   
   # EC2 will use the role automatically
   ```

### Monitoring & Alerts

Set up alerts for security events:

1. **AWS CloudWatch Alarms**:
   - Unusual API calls
   - Failed authentication attempts
   - Unexpected resource creation

2. **AWS GuardDuty**:
   - Threat detection
   - Anomaly detection
   - Automated alerts

3. **AWS Cost Anomaly Detection**:
   - Unexpected spending
   - Resource abuse

### Support

If you suspect a security breach:

1. **AWS Support**: https://console.aws.amazon.com/support
2. **AWS Security**: aws-security@amazon.com
3. **Rotate all credentials immediately**
4. **Review CloudTrail logs**
5. **Check billing for unauthorized usage**

---

## Quick Reference

### Safe Files (Can commit to Git)
- ✅ Deployment scripts (without credentials)
- ✅ Documentation
- ✅ Application code
- ✅ .gitignore
- ✅ README files

### Sensitive Files (NEVER commit)
- ❌ aws-credentials.ps1
- ❌ deployment-info.json
- ❌ *.pem (SSH keys)
- ❌ .env files
- ❌ Any file with passwords/secrets

### Before Every Git Push
```bash
# 1. Check status
git status

# 2. Review changes
git diff

# 3. Ensure no secrets
git grep -i "AKIA"
git grep -i "password"

# 4. Push
git push
```

---

**Remember: Security is not optional. Protect your credentials!**
