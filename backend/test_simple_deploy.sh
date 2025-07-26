#!/bin/bash

# Simple test script for the new AEM deployment endpoints
# Run this after starting the backend server

BASE_URL="http://localhost:8000"

echo "🚀 Testing Simple AEM Deployment Endpoints"
echo "==========================================="

# Test 1: Check if server is running
echo
echo "1. Testing server connectivity..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/health")
if [ "$response" = "200" ]; then
    echo "✅ Server is running"
else
    echo "❌ Server not responding (HTTP $response)"
    exit 1
fi

# Test 2: Check AEM server status
echo
echo "2. Checking AEM server status..."
curl -s -X GET "$BASE_URL/api/v1/aem/status" | jq '.' || echo "Response not JSON"

# Test 3: Get deployment configuration
echo
echo "3. Getting deployment configuration..."
curl -s -X GET "$BASE_URL/api/v1/aem/config" | jq '.' || echo "Response not JSON"

# Test 4: Start simple deployment (background)
echo
echo "4. Starting simple deployment (background)..."
response=$(curl -s -X POST "$BASE_URL/api/v1/aem/deploy/simple-bg")
echo "$response" | jq '.' || echo "Response: $response"

# Extract deployment ID if successful
deployment_id=$(echo "$response" | jq -r '.deployment_id // empty')

if [ -n "$deployment_id" ]; then
    echo
    echo "5. Monitoring deployment status..."
    echo "Deployment ID: $deployment_id"
    
    # Poll status a few times
    for i in {1..3}; do
        echo "Checking status (attempt $i)..."
        sleep 5
        curl -s -X GET "$BASE_URL/api/v1/aem/deploy/status/$deployment_id" | jq '.' || echo "Status check failed"
        echo
    done
else
    echo "❌ Failed to start deployment or extract deployment ID"
fi

echo
echo "🎉 Test completed!"
echo
echo "Available endpoints:"
echo "  POST $BASE_URL/api/v1/aem/deploy/simple-bg   # Start background deployment"
echo "  POST $BASE_URL/api/v1/aem/deploy/simple      # Synchronous deployment"
echo "  GET  $BASE_URL/api/v1/aem/deploy/status/{id} # Check status"
echo "  GET  $BASE_URL/api/v1/aem/status             # AEM server status"
