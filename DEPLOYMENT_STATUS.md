# Nyaya Mitra AWS Deployment Status

## ✅ Completed Steps

### 1. AWS Infrastructure Created
- ✅ EC2 Key Pair created (`nyaya-mitra-key.pem`)
- ✅ Backend Security Group created
- ✅ Database Security Group created
- ✅ EC2 Instance launched (t3.small)
- ✅ RDS PostgreSQL database creation initiated

### 2. EC2 Instance Details
- **Instance ID**: Check `deployment-info.json`
- **Public IP**: Check `deployment-info.json`
- **Status**: Running
- **SSH Key**: `nyaya-mitra-key.pem` (in project root)

### 3. RDS Database
- **Status**: Being created (takes 5-10 minutes)
- **Engine**: PostgreSQL 15
- **Instance Class**: db.t3.micro
- **Storage**: 20 GB gp3

## 🔄 Next Steps

### Option 1: Automated Deployment (Recommended)

Run this command to automatically wait for RDS and deploy everything:

```powershell
.\check-and-deploy.ps1
```

This script will:
1. Wait for RDS database to be ready
2. Automatically deploy the backend
3. Prompt you to deploy the frontend

### Option 2: Manual Step-by-Step

If you prefer to do it manually:

1. **Wait for RDS** (5-10 minutes from now)
   - Check status in AWS Console → RDS → Databases
   - Or run: `aws rds describe-db-instances --db-instance-identifier nyaya-mitra-db --query 'DBInstances[0].DBInstanceStatus' --output text`

2. **Deploy Backend**
   ```powershell
   .\deploy-backend.ps1
   ```

3. **Deploy Frontend**
   ```powershell
   .\deploy-frontend.ps1
   ```

## 📋 Deployment Information

All deployment details are saved in `deployment-info.json`:
- EC2 Public IP
- RDS Endpoint
- Database credentials
- JWT Secret
- Security Group IDs

**IMPORTANT**: Keep `deployment-info.json` and `nyaya-mitra-key.pem` secure!

## 🔍 Checking Status

### Check RDS Status
```powershell
aws rds describe-db-instances --db-instance-identifier nyaya-mitra-db --query 'DBInstances[0].DBInstanceStatus' --output text
```

### Check EC2 Status
```powershell
aws ec2 describe-instances --instance-ids <instance-id> --query 'Reservations[0].Instances[0].State.Name' --output text
```

### Test Backend (after deployment)
```powershell
curl http://<ec2-public-ip>/health
```

## 💰 Cost Estimate

Your deployment will cost approximately:
- EC2 t3.small: ~$15/month
- RDS db.t3.micro: ~$15/month
- S3 + CloudFront: ~$5/month
- Bedrock (usage-based): ~$10-20/month

**Total: ~$45-55/month**

With your $200 credits, this will last 3-4 months!

## 🆘 Troubleshooting

### If RDS takes too long
- Check AWS Console → RDS → Databases
- Look for any error messages
- Ensure you have sufficient limits in your AWS account

### If EC2 connection fails
- Ensure `nyaya-mitra-key.pem` has correct permissions
- Check security group allows SSH from your IP
- Verify EC2 instance is running

### If backend deployment fails
- Check EC2 instance logs
- Verify RDS endpoint is correct
- Ensure security groups allow EC2 to access RDS

## 📞 Need Help?

- Check `DEPLOYMENT_TROUBLESHOOTING.md` for common issues
- Review AWS Console for service status
- Check deployment logs in the terminal

## ⏱️ Estimated Timeline

- ✅ Infrastructure setup: Complete (~5 minutes)
- 🔄 RDS database creation: In progress (5-10 minutes)
- ⏳ Backend deployment: Pending (~10 minutes)
- ⏳ Frontend deployment: Pending (~15 minutes)

**Total remaining time: ~30-35 minutes**

---

**Current Status**: Waiting for RDS database to be ready

**Next Action**: Run `.\check-and-deploy.ps1` to continue automatically
