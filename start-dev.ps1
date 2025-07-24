# Start all services in development mode (PowerShell)

Write-Host "🚀 Starting DXP Component Builder in Development Mode..." -ForegroundColor Green

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found. Copying from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Please edit .env file with your API keys before running again." -ForegroundColor Green
    exit 1
}

# Start services
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

Write-Host "🎉 Services started successfully!" -ForegroundColor Green
Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🔧 Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "🗄️  Redis: localhost:6379" -ForegroundColor Cyan
