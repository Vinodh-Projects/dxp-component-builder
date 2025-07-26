# Test AEM Deployment Service Endpoints

# Test the AEM deployment service endpoints
# Make sure the backend is running before executing these tests

# 1. Check AEM server status and connectivity
curl -X GET "http://localhost:8000/api/v1/aem/server/status" -H "accept: application/json"

echo "----"

# 2. Get deployment configuration
curl -X GET "http://localhost:8000/api/v1/aem/config" -H "accept: application/json"

echo "----"

# 3. Deploy project asynchronously (recommended for production)
curl -X POST "http://localhost:8000/api/v1/aem/deploy" -H "accept: application/json"

echo "----"

# 4. Check deployment status (replace DEPLOYMENT_ID with actual ID from step 3)
# curl -X GET "http://localhost:8000/api/v1/aem/deploy/status/deploy_1234567890" -H "accept: application/json"

echo "----"

# 5. Get deployment history
curl -X GET "http://localhost:8000/api/v1/aem/deploy/history" -H "accept: application/json"

echo "----"

# 6. Deploy project synchronously (for testing only)
# WARNING: This will block until deployment completes
# curl -X POST "http://localhost:8000/api/v1/aem/deploy/sync" -H "accept: application/json"

echo "----"

# 7. Build specific module (ui.apps)
curl -X POST "http://localhost:8000/api/v1/aem/build/ui.apps" -H "accept: application/json"

echo "----"

# 8. Build specific module (all)
curl -X POST "http://localhost:8000/api/v1/aem/build/all" -H "accept: application/json"
