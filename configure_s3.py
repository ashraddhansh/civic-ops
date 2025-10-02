#!/usr/bin/env python3
"""
Configure S3 bucket for public access
"""
import sys
sys.path.append('.')

def configure_s3_bucket():
    """Configure the S3 bucket for public access"""
    try:
        from app.services.s3_service import s3_service
        
        print("🔧 Configuring S3 bucket for public access...")
        
        # Check if bucket exists
        if not s3_service.check_bucket_exists():
            print(f"❌ Bucket '{s3_service.bucket_name}' does not exist or is not accessible")
            return False
        
        print(f"✅ Bucket '{s3_service.bucket_name}' exists")
        
        # Configure bucket policy
        success = s3_service.configure_bucket_for_public_access()
        
        if success:
            print("✅ Bucket configured for public access")
            print("🎉 S3 bucket is ready for file uploads!")
            return True
        else:
            print("❌ Failed to configure bucket policy")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_upload():
    """Test file upload after configuration"""
    try:
        from app.services.s3_service import s3_service
        from fastapi import UploadFile
        import io
        
        print("\n🧪 Testing file upload...")
        
        # Create a simple test file
        test_content = b"This is a test file for S3 upload"
        test_file = io.BytesIO(test_content)
        
        # Create a mock UploadFile
        class MockUploadFile:
            def __init__(self, filename, content, content_type):
                self.filename = filename
                self.content_type = content_type
                self._content = content
                self._position = 0
            
            async def read(self):
                return self._content
            
            async def seek(self, position):
                self._position = position
        
        mock_file = MockUploadFile("test.txt", test_content, "text/plain")
        
        # This won't work without async, but shows the structure
        print("📝 Mock upload test prepared")
        print("   Use the curl command to test actual uploads")
        
        return True
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 S3 Bucket Configuration\n")
    
    success = configure_s3_bucket()
    
    if success:
        test_upload()
        print("\n📋 Now try the curl command again:")
        print('curl -X POST "http://localhost:8000/users/issues/create" \\')
        print('  -H "Authorization: Bearer YOUR_TOKEN" \\')
        print('  -F "category=Road & Transport" \\')
        print('  -F "subcategory=Potholes" \\')
        print('  -F "description=Test upload" \\')
        print('  -F "latitude=28.6139" \\')
        print('  -F "longitude=77.2090" \\')
        print('  -F "address=Test Location" \\')
        print('  -F "image=@/path/to/image.jpg"')
    else:
        print("\n⚠️ Manual bucket configuration required")
        print("Please configure your S3 bucket manually:")
        print("1. Go to AWS S3 console")
        print("2. Select your bucket 'civic-ops'")
        print("3. Go to Permissions tab")
        print("4. Edit Bucket Policy and add:")
        print("""
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::civic-ops/*"
    }
  ]
}
        """)