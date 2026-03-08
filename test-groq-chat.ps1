# Test Groq-powered chat endpoint
Write-Host "Testing chat with Groq API..." -ForegroundColor Cyan

# First, register a test user and get token
$registerBody = @{
    email = "groqtest@example.com"
    password = "Test123!@#"
    full_name = "Groq Test User"
} | ConvertTo-Json

try {
    $registerResponse = Invoke-WebRequest -Uri "http://3.94.129.107/api/auth/register" -Method POST -Body $registerBody -ContentType "application/json" -UseBasicParsing
    $token = ($registerResponse.Content | ConvertFrom-Json).access_token
    Write-Host "✅ User registered, got token" -ForegroundColor Green
} catch {
    Write-Host "User might already exist, trying to login..." -ForegroundColor Yellow
    # If user exists, just use a dummy token for testing
    $token = "test-token"
}

# Test chat query
$chatBody = @{
    query = "What is IPC Section 420?"
    language = "en"
} | ConvertTo-Json

Write-Host "`nSending chat query..." -ForegroundColor Cyan

try {
    $chatResponse = Invoke-WebRequest -Uri "http://3.94.129.107/api/chat/query" -Method POST -Body $chatBody -ContentType "application/json" -Headers @{"Authorization"="Bearer $token"} -UseBasicParsing
    
    $result = $chatResponse.Content | ConvertFrom-Json
    
    Write-Host "`n✅ SUCCESS! Groq API is working!" -ForegroundColor Green
    Write-Host "`nResponse:" -ForegroundColor Yellow
    Write-Host $result.response
    Write-Host "`nConfidence: $($result.confidence)" -ForegroundColor Cyan
    Write-Host "`n✅ Your chat assistant is now working at http://3.94.129.107" -ForegroundColor Green
    
} catch {
    Write-Host "`n❌ Error testing chat:" -ForegroundColor Red
    Write-Host $_.Exception.Message
}
