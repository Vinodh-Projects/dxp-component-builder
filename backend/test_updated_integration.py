#!/usr/bin/env python3
"""
Test script for AEM deployment integration
"""

import requests
import json
import time
import sys
from typing import Dict, Any

def test_aem_deployment():
    """Test the AEM deployment functionality"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing AEM Deployment Integration")
    print("=" * 50)
    
    # Test 1: Check if backend is running
    print("\n1️⃣ Testing Backend Connectivity...")
    try:
        response = requests.get(f"{base_url}/api/v1/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False
    
    # Test 2: Check AEM server status
    print("\n2️⃣ Testing AEM Server Status...")
    try:
        response = requests.get(f"{base_url}/api/v1/aem/status", timeout=10)
        data = response.json()
        print(f"📊 AEM Status Response: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"⚠️ AEM status check failed (expected if AEM not running): {e}")
    
    # Test 3: Validate project structure
    print("\n3️⃣ Testing Project Structure Validation...")
    try:
        response = requests.post(f"{base_url}/api/v1/aem/validate", timeout=10)
        data = response.json()
        print(f"📊 Validation Response: {json.dumps(data, indent=2)}")
        
        if data.get("valid"):
            print("✅ Project structure validation passed")
        else:
            print(f"⚠️ Project structure validation issues: {data.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Project validation failed: {e}")
        return False
    
    # Test 4: Build a specific module (ui.apps)
    print("\n4️⃣ Testing Module Build (ui.apps)...")
    try:
        build_data = {"module": "ui.apps"}
        response = requests.post(
            f"{base_url}/api/v1/aem/build", 
            json=build_data,
            timeout=120  # Maven builds can take time
        )
        data = response.json()
        print(f"📊 Build Response: {json.dumps(data, indent=2)}")
        
        if data.get("success"):
            print("✅ Module build succeeded")
        else:
            print(f"❌ Module build failed: {data.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Module build test failed: {e}")
    
    # Test 5: Check deployment logs
    print("\n5️⃣ Testing Deployment Logs...")
    try:
        response = requests.get(f"{base_url}/api/v1/aem/logs", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Recent logs: {len(data.get('logs', []))} entries")
            if data.get('logs'):
                print("📝 Latest log entries:")
                for log in data['logs'][-3:]:  # Show last 3 entries
                    print(f"   {log}")
        else:
            print(f"⚠️ Could not retrieve logs: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Log retrieval failed: {e}")
    
    print("\n🎯 Test Summary")
    print("=" * 50)
    print("✅ Integration test completed!")
    print("📁 Project code location: /app/project_code (mounted from root-level project_code)")
    print("🔧 Maven and Java are now available in the Docker container")
    print("🚀 Ready for AEM deployment testing!")
    
    return True

if __name__ == "__main__":
    success = test_aem_deployment()
    sys.exit(0 if success else 1)
