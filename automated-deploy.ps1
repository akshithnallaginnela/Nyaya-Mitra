# Nyaya Mitra - Automated AWS Deployment Script
# Run this script to deploy everything to AWS

# Load AWS credentials from separate file
if (Test-Path "aws-credentials.ps1") {
    . .\aws-credentials.ps1
} else {
    Write-Host "[ERROR] aws-credentials.ps1 not found!" -ForegroundColor Red
    Write-Host "Please create aws-credentials.ps1 with your AWS credentials" -ForegroundColor Yellow
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Nyaya Mitra AWS Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Generate secure passwords
$DBPassword = -join ((65..90) + (97..122) + (48..57) + 33,35,36,37,38,42,43,45,61,63,64,94 | Get-Random -Count 20 | ForEach-Object {[char]$_})
$JWTSecret = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})

Write-Host "[INFO] Generated secure passwords" -ForegroundColor Yellow
Write-Host ""

# Step 1: Get VPC ID
Write-Host "Step 1: Getting Default VPC..." -ForegroundColor Green
$vpcId = aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query 'Vpcs[0].VpcId' --output text --region us-east-1
Write-Host "[SUCCESS] VPC ID: $vpcId" -ForegroundColor Green
Write-Host ""

# Step 2: Create Backend Security Group
Write-Host "Step 2: Creating Backend Security Group..." -ForegroundColor Green
$backendSgId = aws ec2 create-security-group `
    --group-name "nyaya-mitra-backend-sg-$(Get-Date -Format 'yyyyMMddHHmmss')" `
    --description "Nyaya Mitra Backend Security Group" `
    --vpc-id $vpcId `
    --region us-east-1 `
    --query 'GroupId' `
    --output text

Write-Host "[SUCCESS] Backend SG: $backendSgId" -ForegroundColor Green
Write-Host ""

# Step 3: Add inbound rules to backend SG
Write-Host "Step 3: Configuring Backend Security Group Rules..." -ForegroundColor Green
aws ec2 authorize-security-group-ingress --group-id $backendSgId --ip-permissions `
    IpProtocol=tcp,FromPort=22,ToPort=22,IpRanges='[{CidrIp=0.0.0.0/0,Description="SSH"}]' `
    IpProtocol=tcp,FromPort=80,ToPort=80,IpRanges='[{CidrIp=0.0.0.0/0,Description="HTTP"}]' `
    IpProtocol=tcp,FromPort=443,ToPort=443,IpRanges='[{CidrIp=0.0.0.0/0,Description="HTTPS"}]' `
    IpProtocol=tcp,FromPort=8000,ToPort=8000,IpRanges='[{CidrIp=0.0.0.0/0,Description="FastAPI"}]' `
    --region us-east-1

Write-Host "[SUCCESS] Security rules configured" -ForegroundColor Green
Write-Host ""

# Step 4: Create Database Security Group
Write-Host "Step 4: Creating Database Security Group..." -ForegroundColor Green
$dbSgId = aws ec2 create-security-group `
    --group-name "nyaya-mitra-db-sg-$(Get-Date -Format 'yyyyMMddHHmmss')" `
    --description "Nyaya Mitra Database Security Group" `
    --vpc-id $vpcId `
    --region us-east-1 `
    --query 'GroupId' `
    --output text

Write-Host "[SUCCESS] Database SG: $dbSgId" -ForegroundColor Green
Write-Host ""

# Step 5: Allow backend to access database
Write-Host "Step 5: Configuring Database Security Group Rules..." -ForegroundColor Green
aws ec2 authorize-security-group-ingress `
    --group-id $dbSgId `
    --protocol tcp `
    --port 5432 `
    --source-group $backendSgId `
    --region us-east-1

Write-Host "[SUCCESS] Database access configured" -ForegroundColor Green
Write-Host ""

# Step 6: Create RDS Database
Write-Host "Step 6: Creating RDS PostgreSQL Database..." -ForegroundColor Green
Write-Host "[INFO] This will take 5-10 minutes..." -ForegroundColor Yellow

$dbIdentifier = "nyaya-mitra-db"
aws rds create-db-instance `
    --db-instance-identifier $dbIdentifier `
    --db-instance-class db.t3.micro `
    --engine postgres `
    --engine-version 15.4 `
    --master-username nyaya_admin `
    --master-user-password $DBPassword `
    --allocated-storage 20 `
    --storage-type gp3 `
    --vpc-security-group-ids $dbSgId `
    --db-name nyaya_mitra `
    --backup-retention-period 7 `
    --no-publicly-accessible `
    --storage-encrypted `
    --region us-east-1 | Out-Null

Write-Host "[SUCCESS] RDS creation initiated" -ForegroundColor Green
Write-Host ""

# Step 7: Launch EC2 Instance
Write-Host "Step 7: Launching EC2 Instance..." -ForegroundColor Green

# Get latest Ubuntu 22.04 AMI
$amiId = aws ec2 describe-images `
    --owners 099720109477 `
    --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" `
    --query 'sort_by(Images, &CreationDate)[-1].ImageId' `
    --output text `
    --region us-east-1

Write-Host "[INFO] Using AMI: $amiId" -ForegroundColor Yellow

$instanceId = aws ec2 run-instances `
    --image-id $amiId `
    --instance-type t3.small `
    --key-name nyaya-mitra-key `
    --security-group-ids $backendSgId `
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=nyaya-mitra-backend}]' `
    --region us-east-1 `
    --query 'Instances[0].InstanceId' `
    --output text

Write-Host "[SUCCESS] EC2 Instance launched: $instanceId" -ForegroundColor Green
Write-Host ""

# Wait for instance to be running
Write-Host "Step 8: Waiting for EC2 instance to be running..." -ForegroundColor Green
aws ec2 wait instance-running --instance-ids $instanceId --region us-east-1
Write-Host "[SUCCESS] EC2 instance is running" -ForegroundColor Green
Write-Host ""

# Get instance public IP
$publicIp = aws ec2 describe-instances `
    --instance-ids $instanceId `
    --query 'Reservations[0].Instances[0].PublicIpAddress' `
    --output text `
    --region us-east-1

Write-Host "[SUCCESS] EC2 Public IP: $publicIp" -ForegroundColor Green
Write-Host ""

# Wait for RDS to be available
Write-Host "Step 9: Waiting for RDS database to be available..." -ForegroundColor Green
Write-Host "[INFO] This may take 5-10 minutes. Please wait..." -ForegroundColor Yellow
aws rds wait db-instance-available --db-instance-identifier $dbIdentifier --region us-east-1
Write-Host "[SUCCESS] RDS database is available" -ForegroundColor Green
Write-Host ""

# Get RDS endpoint
$dbEndpoint = aws rds describe-db-instances `
    --db-instance-identifier $dbIdentifier `
    --query 'DBInstances[0].Endpoint.Address' `
    --output text `
    --region us-east-1

Write-Host "[SUCCESS] RDS Endpoint: $dbEndpoint" -ForegroundColor Green
Write-Host ""

# Save deployment information
$deploymentInfo = @{
    Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Region = "us-east-1"
    VpcId = $vpcId
    BackendSecurityGroup = $backendSgId
    DatabaseSecurityGroup = $dbSgId
    EC2InstanceId = $instanceId
    EC2PublicIP = $publicIp
    RDSIdentifier = $dbIdentifier
    RDSEndpoint = $dbEndpoint
    DBUsername = "nyaya_admin"
    DBPassword = $DBPassword
    DBName = "nyaya_mitra"
    JWTSecret = $JWTSecret
    KeyPairName = "nyaya-mitra-key"
}

$deploymentInfo | ConvertTo-Json | Out-File "deployment-info.json"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AWS Infrastructure Created Successfully!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Deployment Information:" -ForegroundColor Yellow
Write-Host "  EC2 Public IP: $publicIp" -ForegroundColor White
Write-Host "  RDS Endpoint: $dbEndpoint" -ForegroundColor White
Write-Host "  DB Username: nyaya_admin" -ForegroundColor White
Write-Host "  DB Password: $DBPassword" -ForegroundColor White
Write-Host "  JWT Secret: $JWTSecret" -ForegroundColor White
Write-Host ""
Write-Host "[INFO] All details saved to deployment-info.json" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Green
Write-Host "1. Wait 2-3 minutes for EC2 to fully initialize" -ForegroundColor White
Write-Host "2. Run: .\deploy-backend.ps1 to deploy the backend code" -ForegroundColor White
Write-Host "3. Run: .\deploy-frontend.ps1 to deploy the frontend" -ForegroundColor White
Write-Host ""
