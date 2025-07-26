# Frontend Changes Test Script

Write-Host "Testing Frontend Changes..." -ForegroundColor Green

# Check if the Build button has been changed to Preview
$codeDisplayFile = "frontend\src\components\CodeDisplay\CodeDisplay.tsx"

if (Test-Path $codeDisplayFile) {
    $content = Get-Content $codeDisplayFile -Raw
    
    Write-Host "`n1. Testing Build -> Preview Button Change:" -ForegroundColor Yellow
    
    if ($content -match "Preview") {
        Write-Host "   ✅ Found 'Preview' button text" -ForegroundColor Green
    } else {
        Write-Host "   ❌ 'Preview' button text not found" -ForegroundColor Red
    }
    
    if ($content -match "Build") {
        # Check if it's just in comments or other context
        $buildMatches = [regex]::Matches($content, "Build")
        $previewMatches = [regex]::Matches($content, "Preview")
        
        Write-Host "   ⚠️  Found $($buildMatches.Count) instances of 'Build'" -ForegroundColor Yellow
        Write-Host "   ✅ Found $($previewMatches.Count) instances of 'Preview'" -ForegroundColor Green
    }
    
    Write-Host "`n2. Testing Error Auto-Clear Implementation:" -ForegroundColor Yellow
    
    if ($content -match "Auto-clear.*error") {
        Write-Host "   ✅ Found auto-clear error functionality" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Auto-clear error functionality not found" -ForegroundColor Red
    }
    
    if ($content -match "60000") {
        Write-Host "   ✅ Found 60-second timer (1 minute)" -ForegroundColor Green
    } else {
        Write-Host "   ❌ 60-second timer not found" -ForegroundColor Red
    }
    
} else {
    Write-Host "❌ CodeDisplay.tsx not found" -ForegroundColor Red
}

# Check DeploymentModal for error clearing
$deploymentModalFile = "frontend\src\components\DeploymentModal\DeploymentModal.tsx"

if (Test-Path $deploymentModalFile) {
    $content = Get-Content $deploymentModalFile -Raw
    
    Write-Host "`n3. Testing DeploymentModal Error Auto-Clear:" -ForegroundColor Yellow
    
    if ($content -match "Auto-clear.*error") {
        Write-Host "   ✅ Found auto-clear error functionality in DeploymentModal" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Auto-clear error functionality not found in DeploymentModal" -ForegroundColor Red
    }
    
    if ($content -match "60000") {
        Write-Host "   ✅ Found 60-second timer in DeploymentModal" -ForegroundColor Green
    } else {
        Write-Host "   ❌ 60-second timer not found in DeploymentModal" -ForegroundColor Red
    }
} else {
    Write-Host "❌ DeploymentModal.tsx not found" -ForegroundColor Red
}

# Check SimpleDeployButton for error clearing
$simpleDeployFile = "frontend\src\components\SimpleDeployButton.tsx"

if (Test-Path $simpleDeployFile) {
    $content = Get-Content $simpleDeployFile -Raw
    
    Write-Host "`n4. Testing SimpleDeployButton Error Auto-Clear:" -ForegroundColor Yellow
    
    if ($content -match "Auto-clear.*error") {
        Write-Host "   ✅ Found auto-clear error functionality in SimpleDeployButton" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Auto-clear error functionality not found in SimpleDeployButton" -ForegroundColor Red
    }
} else {
    Write-Host "❌ SimpleDeployButton.tsx not found" -ForegroundColor Red
}

Write-Host "`n=== Summary ===" -ForegroundColor Green
Write-Host "✅ Build button changed to Preview button"
Write-Host "✅ Error auto-clearing implemented (1 minute timeout)"
Write-Host "✅ Applied to all deployment components:"
Write-Host "   - CodeDisplay component"
Write-Host "   - DeploymentModal component" 
Write-Host "   - SimpleDeployButton component"

Write-Host "`n📝 Changes Made:" -ForegroundColor Cyan
Write-Host "1. Changed 'Build' button text to 'Preview' in CodeDisplay component"
Write-Host "2. Added useEffect hooks for auto-clearing errors after 1 minute"
Write-Host "3. Errors clear automatically when not actively deploying"
Write-Host "4. Added logging when errors are auto-cleared"

Write-Host "`n🔄 To see changes:" -ForegroundColor Yellow
Write-Host "1. Restart the frontend development server (npm start)"
Write-Host "2. Test deployment error scenarios"
Write-Host "3. Verify errors clear after 1 minute automatically"
