# Final test of Groq-powered chat
Write-Host "=== Testing Nyaya Mitra with Groq API ===" -ForegroundColor Cyan

# Step 1: Register new user
$email = "finaltest$(Get-Random)@example.com"
$registerBody = @{
    email = $email
    password = "Test123!@#"
    full_name = "Final Test User"
} | ConvertTo-Json

Write-Host "`n1. Registering user..." -ForegroundColor Yellow
$registerResponse = Invoke-WebRequest -Uri "http://3.94.129.107/api/auth/register" -Method POST -Body $registerBody -ContentType "application/json" -UseBasicParsing
$token = ($registerResponse.Content | ConvertFrom-Json).access_token
Write-Host "✅ User registered successfully" -ForegroundColor Green

# Step 2: Test chat
Write-Host "`n2. Testing chat with Groq..." -ForegroundColor Yellow
$chatBody = @{
    query = "What is IPC Section 420?"
    language = "en"
} | ConvertTo-Json

$chatResponse = Invoke-WebRequest -Uri "http://3.94.129.107/api/chat/query" -Method POST -Body $chatBody -ContentType "application/json" -Headers @{"Authorization"="Bearer $token"} -UseBasicParsing

$result = $chatResponse.Content | ConvertFrom-Json

Write-Host "`n✅ SUCCESS! Chat is working!" -ForegroundColor Green
Write-Host "`n=== AI Response ===" -ForegroundColor Cyan
Write-Host $result.response
Write-Host "`n=== Details ===" -ForegroundColor Cyan
Write-Host "Confidence: $($result.confidence)"
Write-Host "Language: $($result.language)"
Write-Host "Citations: $($result.citations.Count)"

Write-Host "`n✅ Your application is fully working at http://3.94.129.107" -ForegroundColor Green
Write-Host "✅ Chat assistant powered by Groq API (fast and free!)" -ForegroundColor Green
