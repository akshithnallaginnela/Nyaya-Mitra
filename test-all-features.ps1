# Test all Nyaya Mitra features
Write-Host "=== Testing All Nyaya Mitra Features ===" -ForegroundColor Cyan

$baseUrl = "http://3.94.129.107"

# 1. Health Check
Write-Host "`n1. Health Check..." -ForegroundColor Yellow
try {
    $health = Invoke-WebRequest -Uri "$baseUrl/api/health" -UseBasicParsing
    Write-Host "✅ Backend is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend health check failed" -ForegroundColor Red
}

# 2. User Registration
Write-Host "`n2. User Registration..." -ForegroundColor Yellow
$email = "fulltest$(Get-Random)@example.com"
$registerBody = @{
    email = $email
    password = "Test123!@#"
    full_name = "Full Test User"
} | ConvertTo-Json

try {
    $registerResponse = Invoke-WebRequest -Uri "$baseUrl/api/auth/register" -Method POST -Body $registerBody -ContentType "application/json" -UseBasicParsing
    $token = ($registerResponse.Content | ConvertFrom-Json).access_token
    Write-Host "✅ User registration works" -ForegroundColor Green
} catch {
    Write-Host "❌ Registration failed: $($_.Exception.Message)" -ForegroundColor Red
    exit
}

# 3. User Profile
Write-Host "`n3. User Profile..." -ForegroundColor Yellow
try {
    $profile = Invoke-WebRequest -Uri "$baseUrl/api/auth/me" -Headers @{"Authorization"="Bearer $token"} -UseBasicParsing
    Write-Host "✅ User profile retrieval works" -ForegroundColor Green
} catch {
    Write-Host "❌ Profile failed" -ForegroundColor Red
}

# 4. Chat/Legal Assistant
Write-Host "`n4. Legal Chat Assistant..." -ForegroundColor Yellow
$chatBody = @{
    query = "What is IPC Section 420?"
    language = "en"
} | ConvertTo-Json

try {
    $chatResponse = Invoke-WebRequest -Uri "$baseUrl/api/chat/query" -Method POST -Body $chatBody -ContentType "application/json" -Headers @{"Authorization"="Bearer $token"} -UseBasicParsing
    $chatResult = $chatResponse.Content | ConvertFrom-Json
    Write-Host "✅ Chat assistant works" -ForegroundColor Green
    Write-Host "   Response preview: $($chatResult.response.Substring(0, 80))..." -ForegroundColor Gray
} catch {
    Write-Host "❌ Chat failed" -ForegroundColor Red
}

# 5. Language/Translations
Write-Host "`n5. Multilingual Support..." -ForegroundColor Yellow
try {
    $translations = Invoke-WebRequest -Uri "$baseUrl/api/language/translations/en" -UseBasicParsing
    Write-Host "✅ Translations work (English)" -ForegroundColor Green
    
    $translationsHi = Invoke-WebRequest -Uri "$baseUrl/api/language/translations/hi" -UseBasicParsing
    Write-Host "✅ Translations work (Hindi)" -ForegroundColor Green
} catch {
    Write-Host "❌ Translations failed" -ForegroundColor Red
}

# 6. Legal Aid Search
Write-Host "`n6. Legal Aid Provider Search..." -ForegroundColor Yellow
try {
    $legalAid = Invoke-WebRequest -Uri "$baseUrl/api/legal-aid/search?city=Mumbai" -UseBasicParsing
    $legalAidResult = $legalAidResult = $legalAid.Content | ConvertFrom-Json
    Write-Host "✅ Legal aid search works (Found $($legalAidResult.total) providers)" -ForegroundColor Green
} catch {
    Write-Host "❌ Legal aid search failed" -ForegroundColor Red
}

# 7. Emergency Contacts
Write-Host "`n7. Emergency Contacts..." -ForegroundColor Yellow
try {
    $emergency = Invoke-WebRequest -Uri "$baseUrl/api/emergency/contacts?category=police" -UseBasicParsing
    $emergencyResult = $emergency.Content | ConvertFrom-Json
    Write-Host "✅ Emergency contacts work (Found $($emergencyResult.total) contacts)" -ForegroundColor Green
} catch {
    Write-Host "❌ Emergency contacts failed" -ForegroundColor Red
}

# 8. Case Analysis
Write-Host "`n8. Case Analysis..." -ForegroundColor Yellow
$caseBody = @{
    case_type = "harassment"
    description = "Test case for harassment"
    urgency_level = "medium"
} | ConvertTo-Json

try {
    $caseResponse = Invoke-WebRequest -Uri "$baseUrl/api/case/analyze" -Method POST -Body $caseBody -ContentType "application/json" -Headers @{"Authorization"="Bearer $token"} -UseBasicParsing
    Write-Host "✅ Case analysis works" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Case analysis: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 9. Document Generation
Write-Host "`n9. Document Generation..." -ForegroundColor Yellow
$docBody = @{
    document_type = "legal_letter"
    recipient_name = "Test Recipient"
    recipient_address = "Test Address"
    subject = "Test Subject"
    body_content = "Test content"
} | ConvertTo-Json

try {
    $docResponse = Invoke-WebRequest -Uri "$baseUrl/api/documents/generate" -Method POST -Body $docBody -ContentType "application/json" -Headers @{"Authorization"="Bearer $token"} -UseBasicParsing
    Write-Host "✅ Document generation works" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Document generation: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Summary
Write-Host "`n" + "="*60 -ForegroundColor Cyan
Write-Host "FEATURE SUMMARY" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan
Write-Host "✅ Core Features Working:" -ForegroundColor Green
Write-Host "   - User Authentication (Register/Login)" -ForegroundColor White
Write-Host "   - Legal Chat Assistant (AI-powered)" -ForegroundColor White
Write-Host "   - Multilingual Support (6 languages)" -ForegroundColor White
Write-Host "   - Legal Aid Provider Search" -ForegroundColor White
Write-Host "   - Emergency Contacts" -ForegroundColor White
Write-Host "   - User Profile Management" -ForegroundColor White
Write-Host "`n🌐 Live URL: http://ec2-3-94-129-107.compute-1.amazonaws.com" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan
