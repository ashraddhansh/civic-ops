#!/usr/bin/env python3
"""
Simple S3 connectivity test
"""
import os
import sys
sys.path.append('.')

def test_s3_connection():
    """Test basic S3 connection with current credentials"""
    try:
        from app.services.s3_service import s3_service
        
        print("🔄 Testing S3 connection...")
        
        # Test bucket access
        bucket_exists = s3_service.check_bucket_exists()
        if bucket_exists:
            print(f"✅ S3 bucket '{s3_service.bucket_name}' is accessible")
        else:
            print(f"❌ S3 bucket '{s3_service.bucket_name}' is not accessible")
            
        return bucket_exists
        
    except Exception as e:
        print(f"❌ S3 connection failed: {e}")
        return False

def test_env_variables():
    """Test if required environment variables are set"""
    print("\n🔄 Checking environment variables...")
    
    try:
        from app.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, S3_BUCKET_NAME
        
        vars_to_check = [
            ('AWS_ACCESS_KEY_ID', AWS_ACCESS_KEY_ID),
            ('AWS_SECRET_ACCESS_KEY', AWS_SECRET_ACCESS_KEY),
            ('AWS_REGION', AWS_REGION),
            ('S3_BUCKET_NAME', S3_BUCKET_NAME)
        ]
        
        missing_vars = []
        for var_name, var_value in vars_to_check:
            if var_value:
                # Mask sensitive values
                if 'SECRET' in var_name or 'KEY' in var_name:
                    display_value = '*' * (len(str(var_value)) - 4) + str(var_value)[-4:]
                else:
                    display_value = var_value
                print(f"✅ {var_name}: {display_value}")
            else:
                missing_vars.append(var_name)
                print(f"❌ {var_name}: Not set")
        
        if missing_vars:
            print(f"\n❌ Missing variables: {', '.join(missing_vars)}")
            return False
        else:
            print("\n✅ All required environment variables are set")
            return True
            
    except ImportError as e:
        print(f"❌ Error importing config: {e}")
        return False

if __name__ == "__main__":
    print("🧪 S3 Configuration Test\n")
    
    env_ok = test_env_variables()
    if env_ok:
        s3_ok = test_s3_connection()
        
        if s3_ok:
            print("\n🎉 S3 is ready for file uploads!")
        else:
            print("\n⚠️ S3 connection issues detected")
    else:
        print("\n⚠️ Environment configuration issues detected")