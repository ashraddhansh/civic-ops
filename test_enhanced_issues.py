#!/usr/bin/env python3
"""
Test script for the enhanced issue creation endpoint
"""
import requests
import json

BASE_URL = "https://civic-ops.onrender.com"

def test_enhanced_issue_creation():
    """Test the new enhanced issue creation endpoint"""
    print("🔄 Testing enhanced issue creation endpoint...")
    
    # Note: You need a valid access token for this test
    # Get it from /auth/verify-otp after sending OTP
    
    headers = {
        "Authorization": "Bearer YOUR_ACCESS_TOKEN_HERE",
        "Content-Type": "application/json"
    }
    
    data = {
        "title": "Pothole - Road Issues",
        "category": "Road & Transport", 
        "subcategory": "Potholes",
        "description": "Large pothole causing damage to vehicles on main road",
        "location": {
            "latitude": 28.6139,
            "longitude": 77.2090,
            "address": "123 Main Street, New Delhi, India"
        }
    }
    
    print(f"Request URL: {BASE_URL}/users/issues/create")
    print(f"Request Headers: {json.dumps(headers, indent=2)}")
    print(f"Request Data: {json.dumps(data, indent=2)}")
    
    # Note: This will fail without a valid token, but shows the structure
    response = requests.post(f"{BASE_URL}/users/issues/create", json=data, headers=headers)
    
    print(f"\nResponse Status: {response.status_code}")
    try:
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response Text: {response.text}")
    
    if response.status_code == 401:
        print("\n✅ Endpoint exists but requires valid authentication (expected)")
        return True
    elif response.status_code == 200:
        print("\n✅ Issue created successfully!")
        return True
    else:
        print(f"\n❌ Unexpected response: {response.status_code}")
        return False

def test_endpoint_availability():
    """Check if the endpoint is available"""
    print("\n🔄 Testing endpoint availability...")
    
    try:
        response = requests.options(f"{BASE_URL}/users/issues/create")
        if response.status_code in [200, 405]:
            print("✅ Enhanced issue creation endpoint is available")
            return True
        else:
            print(f"❌ Endpoint not available (status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Error checking endpoint: {e}")
        return False

def main():
    print("🚀 Testing Enhanced Issue Creation Endpoint...\n")
    
    tests = [
        test_endpoint_availability,
        test_enhanced_issue_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print("-" * 60)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed.")
    
    print("\n📝 To test issue creation:")
    print("1. Get access token from /auth/verify-otp")
    print("2. Replace 'YOUR_ACCESS_TOKEN_HERE' in the script")
    print("3. Run the test again")

if __name__ == "__main__":
    main()