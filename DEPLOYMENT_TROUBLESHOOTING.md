# Nyaya Mitra Deployment Troubleshooting Guide

Common issues and solutions during AWS deployment.

## Table of Contents

1. [AWS Bedrock Issues](#aws-bedrock-issues)
2. [Database Connection Issues](#database-connection-issues)
3. [Backend Service Issues](#backend-service-issues)
4. [Frontend Issues](#frontend-issues)
5. [Network & Security Issues](#network--security-issues)
6. [Cost & Billing Issues](#cost--billing-issues)

---

## AWS Bedrock Issues

### Issue: "Access Denied" when calling Bedrock

**Symptoms:**
- Backend logs show: `AccessDeniedException`
- Chat feature returns errors

**Solutions:**

1. **Check Model Access:**
   ```bash
   # List available models
   aws bedrock list-foundation-models --region us-east-1
   
   # If empty, enable model access in console:
   # AWS Console → Bedrock → Model access → Enable Claude 3 Haiku
   ```

2. **Verify IAM Permissions:**
   ```bash
   # Check current user
   aws sts get-caller-identity
   
   # Test Bedrock access
   aws bedrock list-foundation-models --region us-east-1
   ```

3. **Check Environment Variables:**
   ```bash
   # SSH to EC2
   ssh -i nyaya-mitra-key.pem ubuntu@<ec2-ip>
   
   # Check .env file
   cat /opt/nyaya-mitra/backend/.env | grep AWS
   
   # Should show:
   # AWS_REGION=us-east-1
   # AWS_ACCESS_KEY_ID=AKIA...
   # AWS_SECRET_ACCESS_KEY=...
   ```

4. **Verify Credentials:**
   ```bash
   # On EC2, test credentials
   export AWS_ACCESS_KEY_ID=<your-key>
   export AWS_SECRET_ACCESS_KEY=<your-secret>
   aws bedrock list-foundation-models --region us-east-1
   ```

### Issue: "Model not found" error

**Solution:**
- Check `BEDROCK_MODEL_ID` in .env file
- Should be: `anthropic.claude-3-haiku-20240307-v1:0`
- Verify model is enabled in Bedrock console

### Issue: High Bedrock costs

**Symptoms:**
- Unexpected charges
- Token usage very high

**Solutions:**

1. **Check Token Usage:**
   ```bash
   # View CloudWatch metrics
   aws cloudwatch get-metric-statistics \
     --namespace AWS/Bedrock \
     --metric-name InputTokens \
     --start-time 2026-03-01T00:00:00Z \
     --end-time 2026-03-07T23:59:59Z \
     --period 86400 \
     --statistics Sum
   ```

2. **Implement Rate Limiting:**
   - Already implemented in `middleware/security.py`
   - Adjust `requests_per_hour` if needed

3. **Optimize Prompts:**
   - Reduce context window size
   - Implement caching for common queries
   - Use shorter system prompts

---

## Database Connection Issues

### Issue: "Could not connect to database"

**Symptoms:**
- Backend fails to start
- `/db-health` endpoint returns error

**Solutions:**

1. **Check RDS Status:**
   ```bash
   aws rds describe-db-instances \
     --db-instance-identifier nyaya-mitra-db \
     --query 'DBInstances[0].DBInstanceStatus'
   ```

2. **Verify Security Groups:**
   ```bash
   # Check RDS security group allows EC2
   # AWS Console → RDS → nyaya-mitra-db → Connectivity & security
   # Inbound rules should include:
   # Type: PostgreSQL, Port: 5432, Source: nyaya-mitra-backend-sg
   ```

3. **Test Connection from EC2:**
   ```bash
   # SSH to EC2
   ssh -i nyaya-mitra-key.pem ubuntu@<ec2-ip>
   
   # Test PostgreSQL connection
   psql -h <rds-endpoint> -U nyaya_admin -d nyaya_mitra
   # Enter password when prompted
   
   # If connection fails, check:
   # - RDS endpoint is correct
   # - Security group rules
   # - RDS is in "Available" state
   ```

4. **Check DATABASE_URL Format:**
   ```bash
   # Should be:
   # postgresql://nyaya_admin:PASSWORD@ENDPOINT:5432/nyaya_mitra
   
   # Verify in .env file
   cat /opt/nyaya-mitra/backend/.env | grep DATABASE_URL
   ```

### Issue: "Database does not exist"

**Solution:**
```bash
# Connect to PostgreSQL
psql -h <rds-endpoint> -U nyaya_admin -d postgres

# Create database
CREATE DATABASE nyaya_mitra;

# Exit
\q

# Re-run initialization
cd /opt/nyaya-mitra/backend
source .venv/bin/activate
python3 -c "from database import init_db; init_db()"
```

### Issue: "Too many connections"

**Solution:**
```bash
# Check current connections
psql -h <rds-endpoint> -U nyaya_admin -d nyaya_mitra -c \
  "SELECT count(*) FROM pg_stat_activity;"

# Increase max_connections in RDS parameter group
# Or reduce connection pool size in backend
```

---

## Backend Service Issues

### Issue: Backend service won't start

**Symptoms:**
- `systemctl status nyaya-mitra-backend` shows "failed"
- Service keeps restarting

**Solutions:**

1. **Check Service Logs:**
   ```bash
   sudo journalctl -u nyaya-mitra-backend -n 100 --no-pager
   ```

2. **Test Manual Start:**
   ```bash
   cd /opt/nyaya-mitra/backend
   source .venv/bin/activate
   uvicorn main:app --host 0.0.0.0 --port 8000
   
   # Watch for errors
   # Press Ctrl+C to stop
   ```

3. **Common Errors:**

   **Import Error:**
   ```bash
   # Missing dependency
   pip install <missing-package>
   
   # Or reinstall all
   pip install -r requirements.txt
   ```

   **Permission Error:**
   ```bash
   # Fix ownership
   sudo chown -R ubuntu:ubuntu /opt/nyaya-mitra
   ```

   **Port Already in Use:**
   ```bash
   # Find process using port 8000
   sudo lsof -i :8000
   
   # Kill it
   sudo kill -9 <PID>
   
   # Restart service
   sudo systemctl restart nyaya-mitra-backend
   ```

4. **Check Environment Variables:**
   ```bash
   # Verify all required variables are set
   cat /opt/nyaya-mitra/backend/.env
   
   # Required variables:
   # - DATABASE_URL
   # - JWT_SECRET
   # - AWS_ACCESS_KEY_ID
   # - AWS_SECRET_ACCESS_KEY
   # - AI_PROVIDER=bedrock
   ```

### Issue: Backend is slow

**Solutions:**

1. **Check CPU/Memory:**
   ```bash
   # On EC2
   top
   
   # If high usage, consider upgrading to t3.medium
   ```

2. **Check Database Queries:**
   ```bash
   # Enable query logging in RDS
   # Check slow query log
   ```

3. **Add Caching:**
   - Already implemented in `utils/cache.py`
   - Verify Redis is configured (if using)

### Issue: 502 Bad Gateway from Nginx

**Solutions:**

1. **Check Backend Status:**
   ```bash
   sudo systemctl status nyaya-mitra-backend
   ```

2. **Check Nginx Configuration:**
   ```bash
   sudo nginx -t
   
   # If errors, fix and reload
   sudo systemctl reload nginx
   ```

3. **Check Nginx Logs:**
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

---

## Frontend Issues

### Issue: Frontend shows blank page

**Solutions:**

1. **Check Browser Console:**
   - Open Developer Tools (F12)
   - Look for JavaScript errors
   - Check Network tab for failed requests

2. **Verify API URL:**
   ```bash
   # Check built files
   # The API URL should be correct in the build
   
   # Rebuild if needed
   cd frontend
   echo "VITE_API_URL=http://<ec2-ip>" > .env.production
   npm run build
   aws s3 sync dist/ s3://your-bucket/ --delete
   ```

3. **Clear CloudFront Cache:**
   ```bash
   aws cloudfront create-invalidation \
     --distribution-id <your-dist-id> \
     --paths "/*"
   ```

4. **Check S3 Bucket Policy:**
   - Ensure bucket is publicly readable
   - Verify bucket policy is correct

### Issue: CORS errors in browser

**Symptoms:**
- Console shows: "Access-Control-Allow-Origin" error
- API calls fail from frontend

**Solutions:**

1. **Update Backend CORS:**
   ```bash
   # SSH to EC2
   nano /opt/nyaya-mitra/backend/.env
   
   # Add CloudFront URL to CORS_ORIGINS
   CORS_ORIGINS=https://<cloudfront-url>,http://localhost:3000
   
   # Restart backend
   sudo systemctl restart nyaya-mitra-backend
   ```

2. **Verify CORS in main.py:**
   ```python
   # Should have:
   app.add_middleware(
       CORSMiddleware,
       allow_origins=cors_origins,
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

### Issue: React Router 404 errors

**Solution:**
- Ensure CloudFront error pages are configured
- 403 and 404 should redirect to /index.html with 200 status

### Issue: Images/assets not loading

**Solutions:**

1. **Check S3 Upload:**
   ```bash
   aws s3 ls s3://your-bucket/ --recursive
   ```

2. **Re-upload with correct MIME types:**
   ```bash
   cd frontend/dist
   aws s3 sync . s3://your-bucket/ \
     --delete \
     --content-type-by-extension
   ```

---

## Network & Security Issues

### Issue: Can't SSH to EC2

**Solutions:**

1. **Check Security Group:**
   - AWS Console → EC2 → Security Groups
   - Ensure port 22 is open to your IP
   - Update if your IP changed

2. **Check Key Permissions:**
   ```bash
   chmod 400 nyaya-mitra-key.pem
   ```

3. **Verify Instance is Running:**
   ```bash
   aws ec2 describe-instances \
     --instance-ids <your-instance-id> \
     --query 'Reservations[0].Instances[0].State.Name'
   ```

### Issue: Can't access backend from internet

**Solutions:**

1. **Check Security Group:**
   - Ports 80, 443, 8000 should be open to 0.0.0.0/0

2. **Check Nginx Status:**
   ```bash
   sudo systemctl status nginx
   ```

3. **Test Locally First:**
   ```bash
   # On EC2
   curl http://localhost:8000/health
   
   # If works locally but not externally, it's a security group issue
   ```

### Issue: SSL/HTTPS not working

**Solutions:**

1. **Use CloudFront for HTTPS:**
   - CloudFront automatically provides HTTPS
   - Use CloudFront URL instead of direct EC2 IP

2. **Or Install Let's Encrypt on EC2:**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

---

## Cost & Billing Issues

### Issue: Unexpected high costs

**Solutions:**

1. **Check Cost Explorer:**
   ```bash
   aws ce get-cost-and-usage \
     --time-period Start=2026-03-01,End=2026-03-07 \
     --granularity DAILY \
     --metrics BlendedCost \
     --group-by Type=SERVICE
   ```

2. **Common Cost Culprits:**
   - EC2 running 24/7 (stop when not needed)
   - RDS running 24/7 (stop when not needed)
   - Bedrock token usage (implement caching)
   - Data transfer (use CloudFront caching)
   - EBS snapshots (delete old ones)

3. **Stop Resources When Not Needed:**
   ```bash
   # Stop EC2
   aws ec2 stop-instances --instance-ids <id>
   
   # Stop RDS
   aws rds stop-db-instance --db-instance-identifier nyaya-mitra-db
   
   # Start when needed
   aws ec2 start-instances --instance-ids <id>
   aws rds start-db-instance --db-instance-identifier nyaya-mitra-db
   ```

### Issue: Credits not applied

**Solution:**
- Check AWS Billing Dashboard
- Credits are applied automatically
- May take 24-48 hours to reflect
- Contact AWS Support if not applied after 48 hours

---

## General Debugging Steps

### 1. Check All Services

```bash
# Backend
sudo systemctl status nyaya-mitra-backend

# Nginx
sudo systemctl status nginx

# Database (from EC2)
psql -h <rds-endpoint> -U nyaya_admin -d nyaya_mitra -c "SELECT 1;"
```

### 2. Check All Logs

```bash
# Backend logs
sudo journalctl -u nyaya-mitra-backend -n 100

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log

# System logs
sudo journalctl -xe
```

### 3. Test Each Component

```bash
# Test database
curl http://localhost:8000/db-health

# Test backend
curl http://localhost:8000/health

# Test Bedrock
curl -X POST http://localhost:8000/api/chat/test \
  -H "Content-Type: application/json" \
  -d '{"message":"test"}'
```

### 4. Restart Everything

```bash
# Restart backend
sudo systemctl restart nyaya-mitra-backend

# Restart Nginx
sudo systemctl restart nginx

# Reboot EC2 (last resort)
sudo reboot
```

---

## Getting Help

### AWS Support

- Free tier: Community forums
- Paid: AWS Support plans
- Documentation: https://docs.aws.amazon.com

### Check AWS Service Health

- https://status.aws.amazon.com
- Check if there are any outages in your region

### Community Resources

- AWS Forums: https://forums.aws.amazon.com
- Stack Overflow: Tag with `amazon-web-services`, `amazon-bedrock`
- FastAPI Discord: https://discord.gg/fastapi

---

## Prevention Tips

1. **Set Up Monitoring:**
   - CloudWatch alarms for high CPU/memory
   - Budget alerts for costs
   - Log aggregation

2. **Regular Backups:**
   - RDS automated backups (already enabled)
   - EC2 AMI snapshots weekly
   - S3 versioning (already enabled)

3. **Documentation:**
   - Keep deployment notes
   - Document any custom changes
   - Track configuration changes

4. **Testing:**
   - Test in staging first
   - Have rollback plan
   - Keep previous AMI/snapshots

---

**Still having issues? Check the full deployment guide or AWS documentation.**
