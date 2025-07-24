# Test configuration with custom app_id and package_name
$uri = "http://localhost:8000/api/v1/components/generate-form"
$requestJson = '{"description":"Simple button component for testing configuration","component_type":"custom","project_namespace":"testconfig","component_group":"Test.Config"}'
$optionsJson = '{"include_tests":true,"include_clientlibs":true,"include_impl":true,"responsive":true,"accessibility":true,"use_core_components":true,"app_id":"customapp","package_name":"com.customcompany.customproject"}'

# Create multipart form data
$boundary = [System.Guid]::NewGuid().ToString()
$LF = "`r`n"
$bodyLines = (
    "--$boundary",
    "Content-Disposition: form-data; name=`"request`"$LF",
    $requestJson,
    "--$boundary",
    "Content-Disposition: form-data; name=`"options`"$LF", 
    $optionsJson,
    "--$boundary--$LF"
) -join $LF

$headers = @{
    'Content-Type' = "multipart/form-data; boundary=$boundary"
    'Accept' = 'application/json'
}

Write-Host "Testing configuration with custom app_id: customapp and package_name: com.customcompany.customproject" -ForegroundColor Green
$response = Invoke-RestMethod -Uri $uri -Method Post -Headers $headers -Body $bodyLines
$response
