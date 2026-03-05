# 🚀 Nyaya Mitra — AWS Deployment Guide

Complete step-by-step guide to deploy Nyaya Mitra on AWS using the architecture from the system diagram.

---

## 📋 Prerequisites

Before deploying, install these tools on your machine:

| Tool | Install Link | Purpose |
|------|-------------|---------|
| **AWS CLI v2** | [aws.amazon.com/cli](https://aws.amazon.com/cli/) | AWS operations |
| **Docker Desktop** | [docker.com](https://docs.docker.com/desktop/windows/) | Container building |
| **Terraform** | [terraform.io](https://developer.hashicorp.com/terraform/install) | Infrastructure-as-Code |
| **Node.js 20+** | [nodejs.org](https://nodejs.org/) | Frontend build |
| **Git** | [git-scm.com](https://git-scm.com/) | Version control |

---

## 🔧 Step 1: Configure AWS Credentials

```powershell
# Configure AWS CLI with your credentials
aws configure
# Enter:
#   AWS Access Key ID:     <your-key>
#   AWS Secret Access Key: <your-secret>
#   Default region name:   ap-south-1
#   Default output format: json

# Verify configuration
aws sts get-caller-identity
```

> [!IMPORTANT]
> Use an IAM user with **AdministratorAccess** for initial setup. Later, create limited-scope roles.

---

## 🏗️ Step 2: Deploy Infrastructure with Terraform

```powershell
# Navigate to Terraform directory
cd "C:\Users\Akshith\Nyaya Mitra\infrastructure\terraform"

# Copy the example variables file
copy terraform.tfvars.example terraform.tfvars

# EDIT terraform.tfvars with your actual values:
# - db_password: Use a strong password (16+ chars, mixed case, numbers, symbols)
# - jwt_secret: Generate with: python -c "import secrets; print(secrets.token_hex(32))"
```

Then run:

```powershell
# Initialize Terraform
terraform init

# Preview what will be created
terraform plan

# Deploy (creates ~20 AWS resources)
terraform apply
# Type 'yes' when prompted
```

> [!NOTE]
> First deployment takes **5-10 minutes**. Terraform will output the CloudFront domain, ALB DNS, etc.

---

## 🐳 Step 3: Build & Push Backend Docker Image

```powershell
# Get your AWS account ID and ECR login
$AWS_ACCOUNT_ID = aws sts get-caller-identity --query Account --output text
$ECR_REGISTRY = "$AWS_ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com"

# Login to ECR
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin $ECR_REGISTRY

# Build the backend image
cd "C:\Users\Akshith\Nyaya Mitra\backend"
docker build -t "${ECR_REGISTRY}/nyaya-mitra-backend:latest" .

# Push to ECR
docker push "${ECR_REGISTRY}/nyaya-mitra-backend:latest"
```

---

## 🖥️ Step 4: Set Up Ollama AI Layer on EC2

The AI model (Ollama + Mistral/Llama) runs on a **separate EC2 instance** in the private subnet.

### Option A: GPU Instance (Fast Inference — ~$380/mo)

```powershell
# Launch a g4dn.xlarge instance with Deep Learning AMI
# SSH into the instance and run:
bash scripts/setup-ollama-ec2.sh
```

### Option B: CPU-Only (Budget — ~$30/mo)

```powershell
# Launch a t3.medium or t3.large instance
# SSH into the instance and run:
bash scripts/setup-ollama-ec2.sh
# It will auto-detect CPU-only and pull the smaller model
```

> [!TIP]
> Update `ollama_base_url` in `terraform.tfvars` to point to the private IP of your Ollama EC2 instance (e.g., `http://10.0.10.50:11434`).

---

## 🌐 Step 5: Deploy Frontend to S3 + CloudFront

```powershell
# Get the CloudFront domain from Terraform output
cd "C:\Users\Akshith\Nyaya Mitra\infrastructure\terraform"
$CLOUDFRONT_DOMAIN = terraform output -raw cloudfront_domain
$FRONTEND_BUCKET = terraform output -raw frontend_bucket

# Build frontend with production API URL
cd "C:\Users\Akshith\Nyaya Mitra\frontend"
$env:VITE_API_URL = "https://$CLOUDFRONT_DOMAIN"
npm ci
npm run build

# Deploy to S3
aws s3 sync dist/ "s3://$FRONTEND_BUCKET" --delete

# Invalidate CloudFront cache
$CLOUDFRONT_ID = aws cloudfront list-distributions --query "DistributionList.Items[?Comment=='Nyaya Mitra CDN'].Id" --output text
aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_ID --paths "/*"
```

---

## ✅ Step 6: Verify Deployment

```powershell
# Check backend health
curl "http://<ALB_DNS>/health"
# Expected: {"status":"ok","message":"Nyaya Mitra API is running"}

# Check frontend
# Visit: https://<CLOUDFRONT_DOMAIN>
```

---

## 🔄 Step 7: Set Up CI/CD (GitHub Actions)

Add these GitHub repository secrets:

| Secret | Value |
|--------|-------|
| `AWS_ACCESS_KEY_ID` | Your AWS access key |
| `AWS_SECRET_ACCESS_KEY` | Your AWS secret key |
| `FRONTEND_S3_BUCKET` | S3 bucket name (from Terraform output) |
| `CLOUDFRONT_URL` | CloudFront domain (from Terraform output) |
| `CLOUDFRONT_DISTRIBUTION_ID` | CloudFront distribution ID |
| `ALB_DNS` | ALB DNS name (from Terraform output) |

After adding secrets, every push to `main` will auto-deploy!

---

## 🔒 Security Checklist

- [ ] Change all default passwords in `terraform.tfvars`
- [ ] Generate a strong `jwt_secret`
- [ ] Set up an ACM SSL certificate for your custom domain
- [ ] Enable AWS WAF on the ALB (optional, extra cost)
- [ ] Enable CloudWatch alerts for errors
- [ ] Restrict SSH access to your IP only
- [ ] Enable RDS encryption (already configured)
- [ ] Review IAM policies (follow least-privilege principle)

---

## 💰 Cost Optimization Tips

1. **Use `t3.micro` for RDS** — Free tier eligible for 12 months
2. **Use Fargate Spot** — Up to 70% savings on ECS tasks  
3. **Use `llama3.2:3b` on CPU** — No GPU instance needed (~$350/mo savings)
4. **Enable S3 Lifecycle Rules** — Auto-delete old uploads
5. **Use CloudFront caching** — Reduces backend load
6. **Set up auto-scaling** — Scale down during low traffic

---

## 🧹 Tear Down (if needed)

```powershell
cd "C:\Users\Akshith\Nyaya Mitra\infrastructure\terraform"
terraform destroy
# Type 'yes' to confirm — this deletes ALL AWS resources
```

> [!CAUTION]
> `terraform destroy` will **permanently delete** all data including the RDS database. Take backups first!
