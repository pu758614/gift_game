# 系統測試腳本
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  System Status Check" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# 檢查容器狀態
Write-Host "[1] Checking container status..." -ForegroundColor Green
docker ps --filter "name=giftgame" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
Write-Host ""

# 測試後端健康檢查
Write-Host "[2] Testing backend health..." -ForegroundColor Green
try {
    $response = Invoke-RestMethod -Uri "http://localhost:5000/api/health" -Method Get
    Write-Host "Status: $($response.status)" -ForegroundColor Yellow
    Write-Host "Message: $($response.message)" -ForegroundColor Yellow
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}
Write-Host ""

# 測試提交表單
Write-Host "[3] Testing form submission..." -ForegroundColor Green
$formData = @{
    player_name = "Test Player"
    who_likes = "Coffee lovers"
    usage_situation = "Morning work"
    usage_time = "8-10 AM"
    usage_time_2 = "After lunch"
    happiness_reason = "Provides energy and joy"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:5000/api/submit-form" -Method Post -Body $formData -ContentType "application/json"
    Write-Host "Gift ID: $($response.gift_id)" -ForegroundColor Yellow
    Write-Host "Message: $($response.message)" -ForegroundColor Yellow
    $giftId = $response.gift_id

    Write-Host ""
    Write-Host "[4] Testing gift generation..." -ForegroundColor Green
    $response = Invoke-RestMethod -Uri "http://localhost:5000/api/generate-gift/$giftId" -Method Post
    Write-Host "AI Guess: $($response.gift.ai_guess)" -ForegroundColor Yellow
    Write-Host "Image URL: $($response.gift.image_url)" -ForegroundColor Yellow

    Write-Host ""
    Write-Host "[5] Testing gift confirmation..." -ForegroundColor Green
    $response = Invoke-RestMethod -Uri "http://localhost:5000/api/confirm/$giftId" -Method Post
    Write-Host "Confirmed: $($response.gift.is_confirmed)" -ForegroundColor Yellow

    Write-Host ""
    Write-Host "[6] Testing gift list..." -ForegroundColor Green
    $response = Invoke-RestMethod -Uri "http://localhost:5000/api/gifts" -Method Get
    Write-Host "Total gifts: $($response.total)" -ForegroundColor Yellow

} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails) {
        Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Test Complete" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Green
Write-Host "Backend:  http://localhost:5000" -ForegroundColor Green
