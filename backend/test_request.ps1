$uri = "http://localhost:8000/api/v1/components/generate-form"
$requestJson = '{"description":"A hero banner component with title and background image","component_type":"hero-banner","fields":[{"name":"title","label":"Title","type":"textfield","required":true,"description":"Hero banner title"}],"project_namespace":"wknd","component_group":"WKND.Content"}'
$optionsJson = '{"include_tests":true,"include_clientlibs":true,"include_impl":true,"responsive":true,"accessibility":true,"use_core_components":true,"app_id":"testapp","package_name":"com.test.project"}'

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

$response = Invoke-RestMethod -Uri $uri -Method Post -Headers $headers -Body $bodyLines
$response
