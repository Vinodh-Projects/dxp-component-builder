# Start all services in production mode (PowerShell)

Write-Host "🚀 Starting DXP Component Builder in Production Mode..." -ForegroundColor Green

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found. Copying from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Please edit .env file with your API keys before running again." -ForegroundColor Green
    exit 1
}

# Start services with production profile
docker-compose --profile production up --build -d

Write-Host "🎉 Services started successfully!" -ForegroundColor Green
Write-Host "🌐 Application: http://localhost" -ForegroundColor Cyan
Write-Host "🔧 Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "🗄️  Redis: localhost:6379" -ForegroundColor Cyan
