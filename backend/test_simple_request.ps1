$uri = "http://localhost/api/v1/components/generate"
$headers = @{
    'Content-Type' = 'application/json'
    'Accept' = 'application/json'
}

$body = @{
    description = "A hero banner component with title and background image"
    component_type = "hero-banner"
    fields = @(
        @{
            name = "title"
            label = "Title"
            type = "textfield"
            required = $true
            description = "Hero banner title"
        }
    )
    project_namespace = "wknd"
    component_group = "WKND.Content"
} | ConvertTo-Json -Depth 10

Write-Host "Sending request to: $uri"
Write-Host "Body: $body"

try {
    $response = Invoke-RestMethod -Uri $uri -Method Post -Headers $headers -Body $body
    Write-Host "Success!" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails) {
        Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
}
