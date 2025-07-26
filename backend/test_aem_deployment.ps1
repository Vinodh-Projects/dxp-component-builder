# Test AEM Deployment Service Endpoints (PowerShell)
# Make sure the backend is running before executing these tests

Write-Host "Testing AEM Deployment Service Endpoints" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

# 1. Check AEM server status and connectivity
Write-Host "`n1. Checking AEM server status..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/aem/server/status" -Method GET
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

# 2. Get deployment configuration
Write-Host "`n2. Getting deployment configuration..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/aem/config" -Method GET
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

# 3. Deploy project asynchronously (recommended for production)
Write-Host "`n3. Starting asynchronous deployment..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/aem/deploy" -Method POST
    $deploymentId = $response.deployment_id
    $response | ConvertTo-Json -Depth 10
    
    # 4. Check deployment status if we got a deployment ID
    if ($deploymentId) {
        Write-Host "`n4. Checking deployment status..." -ForegroundColor Yellow
        Start-Sleep -Seconds 2  # Wait a bit for deployment to start
        
        $statusResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/aem/deploy/status/$deploymentId" -Method GET
        $statusResponse | ConvertTo-Json -Depth 10
    }
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

# 5. Get deployment history
Write-Host "`n5. Getting deployment history..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/aem/deploy/history" -Method GET
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

# 6. Build specific module (ui.apps)
Write-Host "`n6. Building ui.apps module..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/aem/build/ui.apps" -Method POST
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

# 7. Build specific module (all)
Write-Host "`n7. Building all module..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/aem/build/all" -Method POST
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

Write-Host "`nTesting completed!" -ForegroundColor Green

# Optional: Synchronous deployment (commented out - use with caution)
Write-Host "`nTo test synchronous deployment (WARNING: blocks until complete):" -ForegroundColor Cyan
Write-Host "Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/aem/deploy/sync' -Method POST" -ForegroundColor Cyan
