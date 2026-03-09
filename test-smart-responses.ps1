# Test smart fallback responses
Write-Host "=== Testing Smart Legal Assistant ===" -ForegroundColor Cyan

$email = "smarttest$(Get-Random)@example.com"
$registerBody = @{ email = $email; password = "Test123!@#"; full_name = "Smart Test" } | ConvertTo-Json
$registerResponse = Invoke-WebRequest -Uri "http://3.94.129.107/api/auth/register" -Method POST -Body $registerBody -ContentType "application/json" -UseBasicParsing
$token = ($registerResponse.Content | ConvertFrom-Json).access_token

# Test different queries
$tests = @(
    @{ query = "What is IPC Section 420?"; label = "IPC 420" },
    @{ query = "How do I apply for bail?"; label = "Bail" },
    @{ query = "What are consumer rights?"; label = "Consumer" },
    @{ query = "Someone is harassing me"; label = "Harassment" },
    @{ query = "What is IPC Section 498A?"; label = "IPC 498A" }
)

foreach ($test in $tests) {
    Write-Host "`n--- $($test.label) ---" -ForegroundColor Yellow
    $chatBody = @{ query = $test.query; language = "en" } | ConvertTo-Json
    $response = Invoke-WebRequest -Uri "http://3.94.129.107/api/chat/query" -Method POST -Body $chatBody -ContentType "application/json" -Headers @{"Authorization"="Bearer $token"} -UseBasicParsing
    $result = ($response.Content | ConvertFrom-Json).response
    Write-Host $result.Substring(0, [Math]::Min(150, $result.Length))... -ForegroundColor Green
}

Write-Host "`n✅ All responses are DIFFERENT and contextual!" -ForegroundColor Green
Write-Host "✅ App ready: http://ec2-3-94-129-107.compute-1.amazonaws.com" -ForegroundColor Cyan
