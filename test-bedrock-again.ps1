# Test Bedrock Access
Write-Host "Testing AWS Bedrock access..." -ForegroundColor Cyan

. .\aws-credentials.ps1

aws bedrock-runtime invoke-model `
  --model-id anthropic.claude-3-haiku-20240307-v1:0 `
  --body file://test-bedrock-body.json `
  --region us-east-1 `
  test-output.json 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ SUCCESS! Bedrock is now working!" -ForegroundColor Green
    Write-Host "`nResponse from Claude:" -ForegroundColor Yellow
    $response = Get-Content test-output.json | ConvertFrom-Json
    Write-Host $response.content[0].text
    Write-Host "`n✅ Your chat assistant should now work at http://3.94.129.107" -ForegroundColor Green
} else {
    Write-Host "`n❌ Still waiting for payment method to be processed" -ForegroundColor Red
    Write-Host "Please wait a few more minutes and run this script again: .\test-bedrock-again.ps1" -ForegroundColor Yellow
}
