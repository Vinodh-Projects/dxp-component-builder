# Simple binary image upload test
$uri = "http://localhost:8000/api/v1/components/generate-form"

Write-Host "Testing Binary Image Upload..." -ForegroundColor Green

# Create a simple 1x1 red pixel PNG
$base64ImageRed = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/x8AAv8B/QD7SwMAAAAASUVORK5CYII="
$imageBytes = [Convert]::FromBase64String($base64ImageRed)
$imagePath = "test_red.png"
[System.IO.File]::WriteAllBytes($imagePath, $imageBytes)

$requestJson = '{"description":"A red button component from uploaded image","component_type":"button","fields":[{"name":"label","label":"Button Label","type":"textfield","required":true}],"project_namespace":"wknd","component_group":"WKND.Content"}'
$optionsJson = '{"include_tests":true,"include_clientlibs":true,"include_impl":true}'

# Create multipart form data
$boundary = [System.Guid]::NewGuid().ToString()
$LF = "`r`n"

$bodyLines = @()
$bodyLines += "--$boundary"
$bodyLines += "Content-Disposition: form-data; name=`"request`""
$bodyLines += ""
$bodyLines += $requestJson
$bodyLines += "--$boundary"
$bodyLines += "Content-Disposition: form-data; name=`"options`""
$bodyLines += ""
$bodyLines += $optionsJson
$bodyLines += "--$boundary"
$bodyLines += "Content-Disposition: form-data; name=`"image`"; filename=`"$imagePath`""
$bodyLines += "Content-Type: image/png"
$bodyLines += ""

$bodyText = ($bodyLines -join $LF) + $LF
$bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($bodyText)

$endBoundary = $LF + "--$boundary--" + $LF
$endBytes = [System.Text.Encoding]::UTF8.GetBytes($endBoundary)

$fullBody = New-Object byte[] ($bodyBytes.Length + $imageBytes.Length + $endBytes.Length)
[Array]::Copy($bodyBytes, 0, $fullBody, 0, $bodyBytes.Length)
[Array]::Copy($imageBytes, 0, $fullBody, $bodyBytes.Length, $imageBytes.Length)
[Array]::Copy($endBytes, 0, $fullBody, $bodyBytes.Length + $imageBytes.Length, $endBytes.Length)

$headers = @{
    'Content-Type' = "multipart/form-data; boundary=$boundary"
    'Accept' = 'application/json'
}

Write-Host "Image size: $($imageBytes.Length) bytes"
Write-Host "Full request size: $($fullBody.Length) bytes"

try {
    $response = Invoke-RestMethod -Uri $uri -Method Post -Headers $headers -Body $fullBody
    Write-Host "SUCCESS!" -ForegroundColor Green
    Write-Host "Request ID: $($response.request_id)"
    
    # Check status
    Start-Sleep -Seconds 2
    $statusUri = "http://localhost:8000$($response.status_url)"
    $status = Invoke-RestMethod -Uri $statusUri -Method Get
    Write-Host "Status: $($status.status) - $($status.current_step)"
    
} catch {
    Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Cleanup
Remove-Item $imagePath -ErrorAction SilentlyContinue

Write-Host "`nSupported Formats: PNG, JPEG, GIF, WebP (max 20MB)"
Write-Host "Backend converts to base64 data URLs for OpenAI Vision API"
