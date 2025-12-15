# Stop and Clean Script
# Gift Exchange Game - Stop Services

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  Stop and Clean Services" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

$clean = Read-Host "Clean all data (including database)? (y/n)"

if ($clean -eq "y") {
    Write-Host "[Cleaning] Stopping services and removing volumes..." -ForegroundColor Yellow
    docker-compose down -v
    Write-Host "[Done] All services stopped, data cleaned" -ForegroundColor Green
} else {
    Write-Host "[Stopping] Only stopping services, keeping data..." -ForegroundColor Yellow
    docker-compose down
    Write-Host "[Done] Services stopped, data kept" -ForegroundColor Green
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
