# Gemini Image Generation Test Script
# Test script for Gemini API integration

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Gemini Image Generation Test" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if GEMINI_API_KEY is set
Write-Host "[Step 1] Checking Gemini API Key..." -ForegroundColor Green
$apiKey = docker exec giftgame_backend printenv GEMINI_API_KEY
if ($apiKey -eq "your_gemini_api_key_here" -or [string]::IsNullOrWhiteSpace($apiKey)) {
    Write-Host "WARNING: Gemini API Key is not set!" -ForegroundColor Yellow
    Write-Host "Please edit .env file and set GEMINI_API_KEY" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To get API Key:" -ForegroundColor Cyan
    Write-Host "1. Visit: https://makersuite.google.com/app/apikey" -ForegroundColor Cyan
    Write-Host "2. Login with Google account" -ForegroundColor Cyan
    Write-Host "3. Click 'Get API Key'" -ForegroundColor Cyan
    Write-Host "4. Copy the key to .env file" -ForegroundColor Cyan
    Write-Host ""
    $continue = Read-Host "Continue with test anyway? (y/n)"
    if ($continue -ne "y") {
        exit
    }
} else {
    Write-Host "API Key found: $($apiKey.Substring(0, 10))..." -ForegroundColor Yellow
}
Write-Host ""

# Test data
$testCases = @(
    @{
        name = "Coffee Mug"
        who_likes = "喜歡咖啡的上班族"
        usage_situation = "早上需要提神的時候"
        usage_time = "每天早上 8-10 點"
        usage_time_2 = "下午茶時間 3-4 點"
        happiness_reason = "咖啡的香氣和溫暖讓人感到放鬆和愉悅"
    },
    @{
        name = "Bluetooth Headphones"
        who_likes = "熱愛音樂的年輕人"
        usage_situation = "通勤、運動、工作時聽音樂"
        usage_time = "每天上下班途中"
        usage_time_2 = "週末運動時"
        happiness_reason = "沉浸在音樂世界中，享受個人空間和自由"
    },
    @{
        name = "Scented Candle"
        who_likes = "注重生活品質的人"
        usage_situation = "在家放鬆、冥想、閱讀時"
        usage_time = "晚上睡前"
        usage_time_2 = "週末在家休息時"
        happiness_reason = "溫暖的燭光和香氣營造舒適氛圍，讓心情平靜"
    }
)

$results = @()

foreach ($testCase in $testCases) {
    Write-Host "=====================================" -ForegroundColor Cyan
    Write-Host "  Testing: $($testCase.name)" -ForegroundColor Cyan
    Write-Host "=====================================" -ForegroundColor Cyan
    Write-Host ""

    # Step 1: Submit form
    Write-Host "[1] Submitting form..." -ForegroundColor Green
    $formData = @{
        player_name = "Test - $($testCase.name)"
        who_likes = $testCase.who_likes
        usage_situation = $testCase.usage_situation
        usage_time = $testCase.usage_time
        usage_time_2 = $testCase.usage_time_2
        happiness_reason = $testCase.happiness_reason
    } | ConvertTo-Json

    try {
        $response = Invoke-RestMethod -Uri "http://localhost:5000/api/submit-form" -Method Post -Body $formData -ContentType "application/json"
        $giftId = $response.gift_id
        Write-Host "Gift ID created: $giftId" -ForegroundColor Yellow
        Write-Host ""

        # Step 2: Generate with AI
        Write-Host "[2] Calling Gemini API to guess gift..." -ForegroundColor Green
        $startTime = Get-Date
        $response = Invoke-RestMethod -Uri "http://localhost:5000/api/generate-gift/$giftId" -Method Post
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalSeconds

        Write-Host "AI Guess: $($response.gift.ai_guess)" -ForegroundColor Yellow
        Write-Host "Image URL: $($response.gift.image_url)" -ForegroundColor Yellow
        Write-Host "Generation Time: $([math]::Round($duration, 2)) seconds" -ForegroundColor Yellow
        Write-Host ""

        # Step 3: Test regeneration
        Write-Host "[3] Testing regeneration..." -ForegroundColor Green
        $response2 = Invoke-RestMethod -Uri "http://localhost:5000/api/regenerate/$giftId" -Method Post
        Write-Host "New AI Guess: $($response2.gift.ai_guess)" -ForegroundColor Yellow
        Write-Host "New Image URL: $($response2.gift.image_url)" -ForegroundColor Yellow
        Write-Host ""

        # Collect results
        $results += @{
            TestCase = $testCase.name
            Success = $true
            AIGuess = $response.gift.ai_guess
            RegenerateGuess = $response2.gift.ai_guess
            Duration = [math]::Round($duration, 2)
            GiftId = $giftId
        }

        Write-Host "✓ Test passed for $($testCase.name)" -ForegroundColor Green

    } catch {
        Write-Host "✗ Test failed: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.ErrorDetails) {
            Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
        }

        $results += @{
            TestCase = $testCase.name
            Success = $false
            Error = $_.Exception.Message
        }
    }

    Write-Host ""
    Start-Sleep -Seconds 2
}

# Summary
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Test Summary" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$successCount = ($results | Where-Object { $_.Success -eq $true }).Count
$totalCount = $results.Count

Write-Host "Total Tests: $totalCount" -ForegroundColor White
Write-Host "Passed: $successCount" -ForegroundColor Green
Write-Host "Failed: $($totalCount - $successCount)" -ForegroundColor Red
Write-Host ""

Write-Host "Detailed Results:" -ForegroundColor White
Write-Host "-" * 80 -ForegroundColor Gray
foreach ($result in $results) {
    if ($result.Success) {
        Write-Host "✓ $($result.TestCase)" -ForegroundColor Green
        Write-Host "  AI Guess: $($result.AIGuess)" -ForegroundColor Yellow
        Write-Host "  Regenerate: $($result.RegenerateGuess)" -ForegroundColor Yellow
        Write-Host "  Duration: $($result.Duration)s" -ForegroundColor Cyan
        Write-Host "  Gift ID: $($result.GiftId)" -ForegroundColor Gray
    } else {
        Write-Host "✗ $($result.TestCase)" -ForegroundColor Red
        Write-Host "  Error: $($result.Error)" -ForegroundColor Red
    }
    Write-Host ""
}

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if API key was actually used
if ($successCount -gt 0) {
    Write-Host "Note: If all AI guesses are '神秘禮物', the API key may not be set correctly." -ForegroundColor Yellow
    Write-Host "Check .env file and restart services with:" -ForegroundColor Yellow
    Write-Host "  docker-compose restart backend" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host "View all gifts at: http://localhost:3000/gallery" -ForegroundColor Green
Write-Host "Backend API: http://localhost:5000/api/gifts" -ForegroundColor Green
