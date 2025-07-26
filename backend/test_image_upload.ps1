# Test script to check image upload with generate-form endpoint
$uri = "http://localhost:8000/api/v1/components/generate-form"

# Create a simple test image (1x1 pixel PNG)
$base64Image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
$imageBytes = [Convert]::FromBase64String($base64Image)
$imagePath = "test_image.png"
[System.IO.File]::WriteAllBytes($imagePath, $imageBytes)

$requestJson = '{"description":"A simple button component with image background","component_type":"button","fields":[{"name":"label","label":"Button Label","type":"textfield","required":true}],"project_namespace":"wknd","component_group":"WKND.Content"}'
$optionsJson = '{"include_tests":true,"include_clientlibs":true,"include_impl":true}'

# Create multipart form data with image
$boundary = [System.Guid]::NewGuid().ToString()
$LF = "`r`n"

# Read image file
$imageContent = [System.IO.File]::ReadAllBytes($imagePath)

# Create body
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
$bodyLines += "Content-Disposition: form-data; name=`"image`"; filename=`"test_image.png`""
$bodyLines += "Content-Type: image/png"
$bodyLines += ""

$bodyText = ($bodyLines -join $LF) + $LF
$bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($bodyText)

# Combine text and image bytes
$endBoundary = $LF + "--$boundary--" + $LF
$endBytes = [System.Text.Encoding]::UTF8.GetBytes($endBoundary)

$fullBody = New-Object byte[] ($bodyBytes.Length + $imageContent.Length + $endBytes.Length)
[Array]::Copy($bodyBytes, 0, $fullBody, 0, $bodyBytes.Length)
[Array]::Copy($imageContent, 0, $fullBody, $bodyBytes.Length, $imageContent.Length)
[Array]::Copy($endBytes, 0, $fullBody, $bodyBytes.Length + $imageContent.Length, $endBytes.Length)

$headers = @{
    'Content-Type' = "multipart/form-data; boundary=$boundary"
    'Accept' = 'application/json'
}

Write-Host "Testing image upload with generate-form endpoint..."
Write-Host "Request JSON: $requestJson"
Write-Host "Image size: $($imageContent.Length) bytes"

try {
    $response = Invoke-RestMethod -Uri $uri -Method Post -Headers $headers -Body $fullBody
    Write-Host "Success! Response:"
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "Error occurred:"
    Write-Host $_.Exception.Message
    Write-Host "Response content:"
    Write-Host $_.Exception.Response
}

# Cleanup
Remove-Item $imagePath -ErrorAction SilentlyContinue
