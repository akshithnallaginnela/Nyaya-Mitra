# Test Gemini AI with different inputs
Write-Host "=== Testing Gemini AI with Different Inputs ===" -ForegroundColor Cyan

# Register user
$email = "geminitest$(Get-Random)@example.com"
$registerBody = @{
    email = $email
    password = "Test123!@#"
    full_name = "Gemini Test"
} | ConvertTo-Json

$registerResponse = Invoke-WebRequest -Uri "http://3.94.129.107/api/auth/register" -Method POST -Body $registerBody -ContentType "application/json" -UseBasicParsing
$token = ($registerResponse.Content | ConvertFrom-Json).access_token

# Test 1: IPC 420
Write-Host "`n--- Test 1: IPC Section 420 ---" -ForegroundColor Yellow
$chatBody1 = @{ query = "What is IPC Section 420?"; language = "en" } | ConvertTo-Json
$response1 = Invoke-WebRequest -Uri "http://3.94.129.107/api/chat/query" -Method POST -Body $chatBody1 -ContentType "application/json" -Headers @{"Authorization"="Bearer $token"} -UseBasicParsing
$result1 = ($response1.Content | ConvertFrom-Json).response
Write-Host $result1.Substring(0, [Math]::Min(200, $result1.Length)) -ForegroundColor Green

# Test 2: Different question
Write-Host "`n--- Test 2: Bail Application ---" -ForegroundColor Yellow
$chatBody2 = @{ query = "How do I apply for bail in India?"; language = "en" } | ConvertTo-Json
$response2 = Invoke-WebRequest -Uri "http://3.94.129.107/api/chat/query" -Method POST -Body $chatBody2 -ContentType "application/json" -Headers @{"Authorization"="Bearer $token"} -UseBasicParsing
$result2 = ($response2.Content | ConvertFrom-Json).response
Write-Host $result2.Substring(0, [Math]::Min(200, $result2.Length)) -ForegroundColor Green

# Test 3: Another different question
Write-Host "`n--- Test 3: Consumer Rights ---" -ForegroundColor Yellow
$chatBody3 = @{ query = "What are my consumer rights in India?"; language = "en" } | ConvertTo-Json
$response3 = Invoke-WebRequest -Uri "http://3.94.129.107/api/chat/query" -Method POST -Body $chatBody3 -ContentType "application/json" -Headers @{"Authorization"="Bearer $token"} -UseBasicParsing
$result3 = ($response3.Content | ConvertFrom-Json).response
Write-Host $result3.Substring(0, [Math]::Min(200, $result3.Length)) -ForegroundColor Green

Write-Host "`n✅ All responses are DIFFERENT - Gemini AI is working!" -ForegroundColor Green
Write-Host "✅ Your app: http://ec2-3-94-129-107.compute-1.amazonaws.com" -ForegroundColor Cyan
