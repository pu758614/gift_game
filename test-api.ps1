# API Test Script
# Gift Exchange Game - API Testing

# Set API URL
$API_URL = "http://localhost:5000"

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  API Test Script" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# 1. Health Check
Write-Host "[Test 1] Health check..." -ForegroundColor Green
try {
    $response = Invoke-RestMethod -Uri "$API_URL/api/health" -Method Get
    Write-Host "結果: $($response | ConvertTo-Json)" -ForegroundColor Yellow
} catch {
    Write-Host "錯誤: $_" -ForegroundColor Red
}

Write-Host ""

# 2. Submit Form
Write-Host "[Test 2] Submit test form..." -ForegroundColor Green
$formData = @{
    player_name = "Test Player"
    who_likes = "Coffee lovers"
    usage_situation = "Need energy boost at work"
    usage_time = "Morning"
    usage_time_2 = "Afternoon tea time"
    happiness_reason = "The aroma and taste of coffee brings relaxation and joy"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$API_URL/api/submit-form" -Method Post -Body $formData -ContentType "application/json"
    $giftId = $response.gift_id
    Write-Host "Result: Gift ID = $giftId" -ForegroundColor Yellow

    Write-Host ""

    # 3. Generate Gift
    Write-Host "[Test 3] Generate gift image..." -ForegroundColor Green
    $response = Invoke-RestMethod -Uri "$API_URL/api/generate-gift/$giftId" -Method Post
    Write-Host "AI Guess: $($response.gift.ai_guess)" -ForegroundColor Yellow
    Write-Host "Image URL: $($response.gift.image_url)" -ForegroundColor Yellow

    Write-Host ""

    # 4. Confirm Gift
    Write-Host "[Test 4] Confirm gift..." -ForegroundColor Green
    $response = Invoke-RestMethod -Uri "$API_URL/api/confirm/$giftId" -Method Post
    Write-Host "Result: Confirmed successfully" -ForegroundColor Yellow

    Write-Host ""

    # 5. Get All Gifts
    Write-Host "[Test 5] Get gift list..." -ForegroundColor Green
    $response = Invoke-RestMethod -Uri "$API_URL/api/gifts" -Method Get
    Write-Host "Total: $($response.total) gifts" -ForegroundColor Yellow

} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Testing completed!" -ForegroundColor Green
Write-Host "Visit http://localhost:3000 for frontend" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
