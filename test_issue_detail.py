#!/usr/bin/env python3
"""
Test script for the updated /users/issues/{issue_id} endpoint
"""

import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000"

def test_issue_detail_endpoint(access_token: str, issue_id: str):
    """Test the /users/issues/{issue_id} endpoint"""
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    print(f"🔍 Testing /users/issues/{issue_id} endpoint...")
    print("=" * 60)
    
    # Test the endpoint
    response = requests.get(f"{BASE_URL}/users/issues/{issue_id}", headers=headers)
    
    print(f"📊 Status Code: {response.status_code}")
    print(f"📋 Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ SUCCESS! Issue retrieved successfully")
        print(f"📄 Response Structure:")
        print(json.dumps(data, indent=2))
        
        # Validate response structure
        assert "success" in data and data["success"] == True
        assert "message" in data
        assert "data" in data and "issue" in data["data"]
        
        issue = data["data"]["issue"]
        
        # Check all required fields
        required_fields = ["id", "title", "category", "subcategory", "description", 
                          "status", "priority", "location", "created_at"]
        
        for field in required_fields:
            assert field in issue, f"Missing required field: {field}"
        
        # Check location structure
        location = issue["location"]
        assert "address" in location
        if location.get("latitude") is not None:
            assert "longitude" in location
        
        # Check if image URL is valid (if present)
        if issue.get("image_url"):
            print(f"🖼️  Image URL: {issue['image_url'][:100]}...")
            # You could add actual image validation here
        
        # Check if voice note URL is valid (if present)
        if issue.get("voice_note_url"):
            print(f"🎵 Voice Note URL: {issue['voice_note_url'][:100]}...")
        
        print("\n✅ All validation checks passed!")
        
    elif response.status_code == 404:
        print("❌ Issue not found")
        print(f"Response: {response.text}")
        
    elif response.status_code == 401:
        print("❌ Unauthorized - Invalid token")
        print(f"Response: {response.text}")
        
    elif response.status_code == 400:
        print("❌ Bad Request - Invalid issue ID format")
        print(f"Response: {response.text}")
        
    else:
        print(f"❌ Unexpected error: {response.status_code}")
        print(f"Response: {response.text}")
    
    return response.status_code == 200

def test_multiple_issue_formats(access_token: str):
    """Test with different issue ID formats"""
    
    print("\n🧪 Testing different issue ID formats...")
    print("=" * 60)
    
    # Get list of issues first
    headers = {"Authorization": f"Bearer {access_token}"}
    
    print("📋 Getting user's issues first...")
    response = requests.get(f"{BASE_URL}/users/my-issues?limit=5", headers=headers)
    
    if response.status_code != 200:
        print("❌ Failed to get issues list")
        return
    
    issues_data = response.json()
    issues = issues_data["data"]["issues"]
    
    if not issues:
        print("📝 No issues found. Create some issues first.")
        return
    
    print(f"📊 Found {len(issues)} issues to test with")
    
    for i, issue in enumerate(issues[:3]):  # Test first 3 issues
        issue_id = issue["id"]
        print(f"\n🔹 Test {i+1}: Testing with issue ID: {issue_id}")
        
        success = test_issue_detail_endpoint(access_token, issue_id)
        
        if success:
            print(f"✅ Test {i+1} passed")
        else:
            print(f"❌ Test {i+1} failed")

def main():
    """Main test function"""
    print("🚀 Issue Detail Endpoint Test Suite")
    print("=" * 60)
    
    # Get access token
    access_token = input("🔑 Enter your access token: ").strip()
    
    if not access_token:
        print("❌ Access token is required")
        return
    
    # Test with multiple issue formats
    test_multiple_issue_formats(access_token)
    
    # Manual test
    print("\n🔧 Manual Test")
    print("=" * 60)
    
    while True:
        issue_id = input("\n🔍 Enter issue ID to test (or 'quit' to exit): ").strip()
        
        if issue_id.lower() == 'quit':
            break
        
        if issue_id:
            test_issue_detail_endpoint(access_token, issue_id)

if __name__ == "__main__":
    main()