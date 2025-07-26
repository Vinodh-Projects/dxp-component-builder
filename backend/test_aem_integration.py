"""
Integration test for AEM Deployment Service
This test verifies the complete workflow from component generation to AEM deployment
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000/api/v1"

def test_aem_server_connectivity():
    """Test AEM server connectivity"""
    print("🔍 Testing AEM server connectivity...")
    
    try:
        response = requests.get(f"{BASE_URL}/aem/server/status")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ AEM Server Status: {'Available' if result.get('server_available') else 'Unavailable'}")
            return result.get('server_available', False)
        else:
            print(f"❌ Server status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

def test_deployment_config():
    """Test deployment configuration"""
    print("\n🔧 Testing deployment configuration...")
    
    try:
        response = requests.get(f"{BASE_URL}/aem/config")
        if response.status_code == 200:
            config = response.json()
            print("✅ Deployment Configuration:")
            print(f"   - Project Path: {config.get('project_path')}")
            print(f"   - AEM Server: {config.get('aem_server_url')}")
            print(f"   - Maven Profiles: {config.get('maven_profiles')}")
            print(f"   - Skip Tests: {config.get('skip_tests')}")
            return True
        else:
            print(f"❌ Config retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Config test failed: {str(e)}")
        return False

def test_async_deployment():
    """Test asynchronous deployment"""
    print("\n🚀 Testing asynchronous deployment...")
    
    try:
        # Start deployment
        response = requests.post(f"{BASE_URL}/aem/deploy")
        if response.status_code == 202:
            result = response.json()
            deployment_id = result.get('deployment_id')
            print(f"✅ Deployment started with ID: {deployment_id}")
            
            # Poll for status
            max_attempts = 30  # 5 minutes max
            attempt = 0
            
            while attempt < max_attempts:
                time.sleep(10)  # Wait 10 seconds
                attempt += 1
                
                status_response = requests.get(f"{BASE_URL}/aem/deploy/status/{deployment_id}")
                if status_response.status_code == 200:
                    status = status_response.json()
                    current_status = status.get('status')
                    
                    print(f"📊 Deployment Status (attempt {attempt}): {current_status}")
                    
                    if current_status in ['completed', 'failed']:
                        success = status.get('success', False)
                        if success:
                            print("✅ Deployment completed successfully!")
                            print(f"   - Build Duration: {status.get('build_duration', 'N/A')}s")
                            print(f"   - Deploy Duration: {status.get('deploy_duration', 'N/A')}s")
                            packages = status.get('deployed_packages', [])
                            if packages:
                                print(f"   - Deployed Packages: {', '.join(packages)}")
                        else:
                            print("❌ Deployment failed!")
                            print(f"   - Error: {status.get('message', 'Unknown error')}")
                        return success
                else:
                    print(f"❌ Status check failed: {status_response.status_code}")
                    
            print("⏰ Deployment timeout after 5 minutes")
            return False
            
        else:
            print(f"❌ Deployment start failed: {response.status_code}")
            if response.text:
                print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Async deployment test failed: {str(e)}")
        return False

def test_module_build():
    """Test module-specific build"""
    print("\n🔨 Testing module-specific build (ui.apps)...")
    
    try:
        response = requests.post(f"{BASE_URL}/aem/build/ui.apps")
        if response.status_code == 200:
            result = response.json()
            success = result.get('success', False)
            if success:
                print("✅ ui.apps module built successfully!")
                print(f"   - Module: {result.get('module')}")
                print(f"   - Message: {result.get('message')}")
            else:
                print("❌ ui.apps module build failed!")
                print(f"   - Error: {result.get('message', 'Unknown error')}")
            return success
        else:
            print(f"❌ Module build failed: {response.status_code}")
            if response.text:
                print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Module build test failed: {str(e)}")
        return False

def test_deployment_history():
    """Test deployment history"""
    print("\n📜 Testing deployment history...")
    
    try:
        response = requests.get(f"{BASE_URL}/aem/deploy/history")
        if response.status_code == 200:
            history = response.json()
            total = history.get('total_deployments', 0)
            print(f"✅ Found {total} deployment(s) in history")
            
            deployments = history.get('deployments', {})
            for dep_id, dep_info in deployments.items():
                status = dep_info.get('status', 'unknown')
                success = dep_info.get('success', 'N/A')
                print(f"   - {dep_id}: {status} (success: {success})")
            
            return True
        else:
            print(f"❌ History retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ History test failed: {str(e)}")
        return False

def main():
    """Run complete integration test suite"""
    print("🧪 AEM Deployment Service Integration Test")
    print("=" * 50)
    
    tests = [
        ("Server Connectivity", test_aem_server_connectivity),
        ("Deployment Config", test_deployment_config),
        ("Module Build", test_module_build),
        ("Deployment History", test_deployment_history),
        ("Async Deployment", test_async_deployment),  # Run this last as it takes time
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*50)
    print("🏁 TEST SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! AEM Deployment Service is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    main()
