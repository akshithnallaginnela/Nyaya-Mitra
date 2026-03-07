# Check RDS status and deploy backend when ready

# Load AWS credentials from separate file
if (Test-Path "aws-credentials.ps1") {
    . .\aws-credentials.ps1
} else {
    Write-Host "[ERROR] aws-credentials.ps1 not found!" -ForegroundColor Red
    Write-Host "Please create aws-credentials.ps1 with your AWS credentials" -ForegroundColor Yellow
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Checking RDS Database Status" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$maxAttempts = 30
$attempt = 0

while ($attempt -lt $maxAttempts) {
    $attempt++
    Write-Host "Attempt $attempt/$maxAttempts - Checking database status..." -ForegroundColor Yellow
    
    try {
        $status = aws rds describe-db-instances `
            --db-instance-identifier nyaya-mitra-db `
            --query 'DBInstances[0].DBInstanceStatus' `
            --output text `
            --region us-east-1 2>$null
        
        Write-Host "Status: $status" -ForegroundColor White
        
        if ($status -eq "available") {
            Write-Host "[SUCCESS] Database is ready!" -ForegroundColor Green
            
            # Get endpoint
            $endpoint = aws rds describe-db-instances `
                --db-instance-identifier nyaya-mitra-db `
                --query 'DBInstances[0].Endpoint.Address' `
                --output text `
                --region us-east-1
            
            Write-Host "Endpoint: $endpoint" -ForegroundColor Yellow
            
            # Update deployment info
            $deploymentInfo = Get-Content deployment-info.json | ConvertFrom-Json
            $deploymentInfo.RDSEndpoint = $endpoint
            $deploymentInfo | ConvertTo-Json | Out-File deployment-info.json
            
            Write-Host ""
            Write-Host "========================================" -ForegroundColor Cyan
            Write-Host "Database Ready! Starting Backend Deployment" -ForegroundColor Cyan
            Write-Host "========================================" -ForegroundColor Cyan
            Write-Host ""
            
            # Run backend deployment
            .\deploy-backend.ps1
            
            break
        }
        else {
            Write-Host "[INFO] Database is still being created..." -ForegroundColor Yellow
            Write-Host "Waiting 30 seconds before next check..." -ForegroundColor White
            Start-Sleep -Seconds 30
        }
    }
    catch {
        Write-Host "[ERROR] Failed to check database status: $_" -ForegroundColor Red
        Start-Sleep -Seconds 30
    }
}

if ($attempt -ge $maxAttempts) {
    Write-Host "[ERROR] Database did not become available within expected time" -ForegroundColor Red
    Write-Host "Please check AWS Console for RDS status" -ForegroundColor Yellow
}
"@
