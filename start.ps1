# Quick Start Script
# Gift Exchange Game - Startup Script

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  Gift Exchange Game - Starting" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "[Warning] .env file not found" -ForegroundColor Yellow
    Write-Host "Copying from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "[Notice] Please edit .env file and add your GEMINI_API_KEY" -ForegroundColor Yellow
    Write-Host ""

    $continue = Read-Host "Continue to start? (y/n)"
    if ($continue -ne "y") {
        Write-Host "Startup cancelled" -ForegroundColor Red
        exit
    }
}

# Check if Docker is running
Write-Host "[Check] Checking Docker service..." -ForegroundColor Green
try {
    docker ps | Out-Null
    Write-Host "[Success] Docker is running" -ForegroundColor Green
} catch {
    Write-Host "[Error] Docker is not running or not installed" -ForegroundColor Red
    Write-Host "Please start Docker Desktop first" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "[Starting] Starting services..." -ForegroundColor Green
Write-Host ""

# Start Docker Compose
docker-compose up --build

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  Services stopped" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
