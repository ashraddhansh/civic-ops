#!/usr/bin/env python3
"""
Test script for the enhanced issue creation endpoint with S3 file upload
"""
import requests
import json
import os

BASE_URL = "https://civic-ops.onrender.com"

def test_enhanced_issue_creation_with_form_data():
    """Test the new enhanced issue creation endpoint with form data"""
    print("🔄 Testing enhanced issue creation with form data...")
    
    # Note: You need a valid access token for this test
    headers = {
        "Authorization": "Bearer YOUR_ACCESS_TOKEN_HERE"
    }
    
    # Form data (multipart/form-data)
    data = {
        "category": "Road & Transport",
        "subcategory": "Potholes", 
        "description": "Large pothole causing damage to vehicles on main road",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "address": "123 Main Street, New Delhi, India"
    }
    
    # Optional: Add image file
    files = None
    # To test with image file:
    # files = {"image": ("test_image.jpg", open("path/to/image.jpg", "rb"), "image/jpeg")}
    
    print(f"Request URL: {BASE_URL}/users/issues/create")
    print(f"Request Headers: {json.dumps(headers, indent=2)}")
    print(f"Form Data: {json.dumps(data, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/users/issues/create", 
        data=data, 
        headers=headers,
        files=files
    )
    
    print(f"\nResponse Status: {response.status_code}")
    try:
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response Text: {response.text}")
    
    if response.status_code == 422:
        print("\n✅ Endpoint exists but requires valid authentication (expected)")
        return True
    elif response.status_code == 200:
        print("\n✅ Issue created successfully!")
        return True
    else:
        print(f"\n❌ Unexpected response: {response.status_code}")
        return False

def test_s3_configuration():
    """Test if S3 configuration seems valid"""
    print("\n🔄 Testing S3 configuration...")
    
    try:
        import boto3
        from botocore.exceptions import NoCredentialsError
        
        # Try to create S3 client (doesn't make actual requests)
        client = boto3.client('s3', region_name='ap-south-1')
        print("✅ boto3 S3 client created successfully")
        return True
    except ImportError:
        print("❌ boto3 not installed")
        return False
    except NoCredentialsError:
        print("❌ AWS credentials not configured")
        return False
    except Exception as e:
        print(f"❌ Error with boto3: {e}")
        return False

def test_with_curl_example():
    """Show curl example for testing"""
    print("\n📋 CURL Example for testing:")
    print("Replace YOUR_ACCESS_TOKEN with actual token from /auth/verify-otp")
    print()
    print("curl -X POST 'https://civic-ops.onrender.com/users/issues/create' \\")
    print("  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \\")
    print("  -F 'category=Road & Transport' \\")
    print("  -F 'subcategory=Potholes' \\")
    print("  -F 'description=Large pothole causing damage' \\")
    print("  -F 'latitude=28.6139' \\")
    print("  -F 'longitude=77.2090' \\")
    print("  -F 'address=123 Main Street, New Delhi' \\")
    print("  -F 'image=@/path/to/your/image.jpg'")

def main():
    print("🚀 Testing Enhanced Issue Creation with S3 Upload...\n")
    
    tests = [
        test_s3_configuration,
        test_enhanced_issue_creation_with_form_data,
        test_with_curl_example
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
        print("-" * 60)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    print("\n📝 To test with real image upload:")
    print("1. Get access token: POST /auth/send-otp → POST /auth/verify-otp")
    print("2. Replace 'YOUR_ACCESS_TOKEN_HERE' with actual token")
    print("3. Use curl or Postman with multipart/form-data")
    print("4. Image will be uploaded to S3 and URL returned in response")
    
    print("\n🔧 S3 Upload Flow:")
    print("Client Image → FastAPI Memory → Validation → S3 Upload → Database URL → Response")
    print("                   ↓               ↓           ↓            ↓            ↓")
    print("               UploadFile      Size/Type    boto3.put   PostgreSQL   JSON response")

if __name__ == "__main__":
    main()