# Test Simple Deploy Endpoint
# This script tests the new simple deployment endpoint

$baseUrl = "http://localhost:8000"

Write-Host "Testing Simple Deploy Endpoints..." -ForegroundColor Green

# Test 1: Simple Deploy (Background)
Write-Host "`n1. Testing Simple Deploy (Background)..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/aem/deploy/simple-bg" -Method POST -ContentType "application/json"
    Write-Host "✓ Simple Deploy Started:" -ForegroundColor Green
    Write-Host "  Deployment ID: $($response.deployment_id)" -ForegroundColor Cyan
    Write-Host "  Status: $($response.status)" -ForegroundColor Cyan
    Write-Host "  Message: $($response.message)" -ForegroundColor Cyan
    Write-Host "  Maven Command: $($response.maven_command)" -ForegroundColor Cyan
    
    $deploymentId = $response.deployment_id
    
    # Monitor deployment status
    Write-Host "`n2. Monitoring Deployment Status..." -ForegroundColor Yellow
    $maxAttempts = 10
    $attempt = 0
    
    do {
        Start-Sleep -Seconds 5
        $attempt++
        Write-Host "  Checking status (attempt $attempt/$maxAttempts)..." -ForegroundColor Gray
        
        $statusResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/aem/deploy/status/$deploymentId" -Method GET
        Write-Host "  Status: $($statusResponse.status)" -ForegroundColor Cyan
        
        if ($statusResponse.status -eq "completed") {
            Write-Host "✓ Deployment Completed Successfully!" -ForegroundColor Green
            if ($statusResponse.duration) {
                Write-Host "  Duration: $($statusResponse.duration) seconds" -ForegroundColor Cyan
            }
            if ($statusResponse.deployed_packages) {
                Write-Host "  Deployed Packages: $($statusResponse.deployed_packages -join ', ')" -ForegroundColor Cyan
            }
            break
        } elseif ($statusResponse.status -eq "failed") {
            Write-Host "✗ Deployment Failed!" -ForegroundColor Red
            Write-Host "  Error: $($statusResponse.error)" -ForegroundColor Red
            break
        }
        
    } while ($attempt -lt $maxAttempts -and $statusResponse.status -eq "in_progress")
    
    if ($attempt -eq $maxAttempts -and $statusResponse.status -eq "in_progress") {
        Write-Host "⚠ Deployment still in progress after $maxAttempts attempts" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "✗ Error testing simple deploy:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

# Test 2: Simple Deploy (Synchronous) - Only if background test succeeded
Write-Host "`n3. Testing Simple Deploy (Synchronous)..." -ForegroundColor Yellow
Write-Host "⚠ Note: This will wait for completion, may take several minutes" -ForegroundColor Yellow

$syncChoice = Read-Host "Do you want to test synchronous deployment? (y/N)"
if ($syncChoice -eq "y" -or $syncChoice -eq "Y") {
    try {
        Write-Host "Starting synchronous deployment..." -ForegroundColor Gray
        $syncResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/aem/deploy/simple" -Method POST -ContentType "application/json"
        
        if ($syncResponse.success) {
            Write-Host "✓ Synchronous Deployment Completed!" -ForegroundColor Green
            Write-Host "  Message: $($syncResponse.message)" -ForegroundColor Cyan
            Write-Host "  Duration: $($syncResponse.duration) seconds" -ForegroundColor Cyan
            Write-Host "  Maven Command: $($syncResponse.maven_command)" -ForegroundColor Cyan
        } else {
            Write-Host "✗ Synchronous Deployment Failed!" -ForegroundColor Red
            Write-Host "  Error: $($syncResponse.error)" -ForegroundColor Red
        }
        
    } catch {
        Write-Host "✗ Error testing synchronous deploy:" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
    }
} else {
    Write-Host "Skipping synchronous test." -ForegroundColor Gray
}

# Test 3: Check AEM Server Status
Write-Host "`n4. Checking AEM Server Status..." -ForegroundColor Yellow
try {
    $statusResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/aem/status" -Method GET
    Write-Host "✓ AEM Server Status:" -ForegroundColor Green
    Write-Host "  Server URL: $($statusResponse.server_url)" -ForegroundColor Cyan
    Write-Host "  Status: $($statusResponse.status)" -ForegroundColor Cyan
    Write-Host "  Message: $($statusResponse.message)" -ForegroundColor Cyan
} catch {
    Write-Host "✗ Error checking AEM status:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

Write-Host "`nTesting Complete!" -ForegroundColor Green
Write-Host "`nAvailable Endpoints:" -ForegroundColor Yellow
Write-Host "  POST /api/v1/aem/deploy/simple-bg   - Simple deploy (background)" -ForegroundColor Cyan
Write-Host "  POST /api/v1/aem/deploy/simple      - Simple deploy (synchronous)" -ForegroundColor Cyan
Write-Host "  GET  /api/v1/aem/deploy/status/{id} - Check deployment status" -ForegroundColor Cyan
Write-Host "  GET  /api/v1/aem/status             - Check AEM server status" -ForegroundColor Cyan
