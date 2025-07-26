"""
Test script to verify AEM deployment integration with frontend
This script tests the API endpoints that the frontend will call
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_deployment_integration():
    """Test the complete deployment integration workflow"""
    print("🧪 Testing AEM Deployment Integration")
    print("=" * 50)
    
    try:
        # 1. Test server status (this is what frontend checks first)
        print("\n1. Testing AEM server status...")
        response = requests.get(f"{BASE_URL}/aem/server/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Server Status: {status}")
            server_available = status.get('server_available', False)
        else:
            print(f"❌ Server status check failed: {response.status_code}")
            return False
        
        # 2. Test deployment config (frontend may show this in modal)
        print("\n2. Testing deployment configuration...")
        response = requests.get(f"{BASE_URL}/aem/config")
        if response.status_code == 200:
            config = response.json()
            print(f"✅ Config: {config}")
        else:
            print(f"❌ Config retrieval failed: {response.status_code}")
            return False
        
        # 3. Test module build (this is what Build button calls)
        print("\n3. Testing module build (ui.apps)...")
        response = requests.post(f"{BASE_URL}/aem/build/ui.apps")
        if response.status_code == 200:
            build_result = response.json()
            print(f"✅ Build Result: {build_result}")
            build_success = build_result.get('success', False)
        else:
            print(f"❌ Module build failed: {response.status_code}")
            build_success = False
        
        # 4. Test async deployment (this is what Deploy button calls)
        print("\n4. Testing async deployment...")
        response = requests.post(f"{BASE_URL}/aem/deploy")
        if response.status_code == 202:
            deploy_result = response.json()
            deployment_id = deploy_result.get('deployment_id')
            print(f"✅ Deployment Started: {deploy_result}")
            
            # 5. Poll deployment status (this is what modal does)
            print(f"\n5. Polling deployment status for {deployment_id}...")
            max_attempts = 10
            attempt = 0
            
            while attempt < max_attempts:
                time.sleep(5)  # Wait 5 seconds
                attempt += 1
                
                status_response = requests.get(f"{BASE_URL}/aem/deploy/status/{deployment_id}")
                if status_response.status_code == 200:
                    status = status_response.json()
                    current_status = status.get('status')
                    print(f"   Attempt {attempt}: {current_status}")
                    
                    if current_status in ['completed', 'failed']:
                        print(f"✅ Final Status: {status}")
                        deployment_success = status.get('success', False)
                        break
                else:
                    print(f"❌ Status check failed: {status_response.status_code}")
                    deployment_success = False
                    break
            else:
                print("⏰ Deployment status polling timeout")
                deployment_success = False
        else:
            print(f"❌ Deployment start failed: {response.status_code}")
            if response.text:
                print(f"   Error: {response.text}")
            deployment_success = False
        
        # 6. Test deployment history (optional frontend feature)
        print("\n6. Testing deployment history...")
        response = requests.get(f"{BASE_URL}/aem/deploy/history")
        if response.status_code == 200:
            history = response.json()
            print(f"✅ History: {history}")
        else:
            print(f"❌ History retrieval failed: {response.status_code}")
        
        # Summary
        print("\n" + "="*50)
        print("🏁 INTEGRATION TEST SUMMARY")
        print("="*50)
        
        results = {
            "Server Available": server_available,
            "Config Retrieved": True,  # If we got here, config worked
            "Build Successful": build_success,
            "Deployment Successful": deployment_success
        }
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        all_passed = all(results.values())
        
        if all_passed:
            print("\n🎉 All integration tests passed!")
            print("Frontend deployment integration should work correctly.")
        else:
            print("\n⚠️ Some tests failed.")
            print("Frontend may experience issues with deployment features.")
        
        return all_passed
        
    except Exception as e:
        print(f"\n❌ Integration test failed with exception: {str(e)}")
        return False

def test_frontend_api_calls():
    """Test the specific API calls that the frontend makes"""
    print("\n" + "="*50)
    print("🎯 TESTING FRONTEND-SPECIFIC API CALLS")
    print("="*50)
    
    frontend_calls = [
        {
            "name": "Get AEM Server Status (Modal opens)",
            "method": "GET",
            "url": f"{BASE_URL}/aem/server/status",
            "expected_fields": ["server_available", "server_url"]
        },
        {
            "name": "Start Deployment (Deploy button)",
            "method": "POST",
            "url": f"{BASE_URL}/aem/deploy",
            "expected_fields": ["deployment_id", "status", "message"]
        },
        {
            "name": "Build Module (Build button)",
            "method": "POST",
            "url": f"{BASE_URL}/aem/build/ui.apps",
            "expected_fields": ["success", "module", "message"]
        }
    ]
    
    for call in frontend_calls:
        print(f"\n🔍 Testing: {call['name']}")
        try:
            if call['method'] == 'GET':
                response = requests.get(call['url'])
            else:
                response = requests.post(call['url'])
            
            if response.status_code in [200, 202]:
                data = response.json()
                print(f"✅ Response: {response.status_code}")
                
                # Check expected fields
                missing_fields = [field for field in call['expected_fields'] if field not in data]
                if missing_fields:
                    print(f"⚠️ Missing fields: {missing_fields}")
                else:
                    print("✅ All expected fields present")
                
                print(f"📄 Data: {json.dumps(data, indent=2)}")
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting AEM Deployment Frontend Integration Tests")
    print("Make sure the backend server is running on localhost:8000")
    print("Press Ctrl+C to stop\n")
    
    # Run the main integration test
    success = test_deployment_integration()
    
    # Run frontend-specific API tests
    test_frontend_api_calls()
    
    if success:
        print("\n🎉 Integration ready! You can now test the frontend deployment features.")
    else:
        print("\n⚠️ Please fix the issues above before testing frontend integration.")
