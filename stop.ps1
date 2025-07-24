# Stop all services (PowerShell)

Write-Host "🛑 Stopping DXP Component Builder services..." -ForegroundColor Yellow

# Stop and remove containers
docker-compose down

Write-Host "✅ All services stopped successfully!" -ForegroundColor Green
