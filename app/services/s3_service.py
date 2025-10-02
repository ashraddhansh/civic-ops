import boto3
import uuid
import mimetypes
import json
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import HTTPException, UploadFile
from app.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, S3_BUCKET_NAME, S3_BASE_URL
from app.config import MAX_FILE_SIZE, ALLOWED_IMAGE_TYPES, ALLOWED_AUDIO_TYPES
import logging

logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self):
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name=AWS_REGION
            )
            self.bucket_name = S3_BUCKET_NAME
            self.base_url = S3_BASE_URL
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            raise

    def validate_file(self, file: UploadFile, file_type: str = "image") -> bool:
        """Validate file size and type"""
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file type
        if file_type == "image":
            allowed_types = ALLOWED_IMAGE_TYPES
        elif file_type == "audio":
            allowed_types = ALLOWED_AUDIO_TYPES
        else:
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
            )
        
        return True

    async def validate_file_size(self, file: UploadFile) -> None:
        """Validate file size by reading content"""
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Reset file pointer
        await file.seek(0)

    def generate_file_key(self, file: UploadFile, folder: str = "uploads") -> str:
        """Generate unique file key for S3 with timestamp"""
        file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else 'bin'
        timestamp = int(datetime.utcnow().timestamp())
        unique_id = str(uuid.uuid4().hex)[:8]  # Short unique ID
        return f"{folder}/{timestamp}_{unique_id}.{file_extension}"

    async def upload_file(self, file: UploadFile, folder: str = "issues") -> str:
        """Upload file to S3 and return pre-signed URL"""
        try:
            # Determine file type based on content type
            if file.content_type.startswith('image/'):
                file_type = "image"
            elif file.content_type.startswith('audio/'):
                file_type = "audio"
            else:
                raise HTTPException(status_code=400, detail="Unsupported file type")
            
            # Validate file type and content
            self.validate_file(file, file_type)
            await self.validate_file_size(file)
            
            # Generate unique key
            key = self.generate_file_key(file, folder)
            
            # Read file content
            file_content = await file.read()
            
            # Reset file pointer for potential reuse
            await file.seek(0)
            
            # Upload to S3 without ACL
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_content,
                ContentType=file.content_type,
                Metadata={
                    'original-filename': file.filename,
                    'upload-timestamp': str(int(datetime.utcnow().timestamp()))
                }
            )
            
            # Generate pre-signed URL for public access (valid for 1 year)
            file_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=31536000  # 1 year in seconds
            )
            
            logger.info(f"File uploaded successfully: {key}")
            return file_url
            
        except HTTPException:
            raise
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            raise HTTPException(status_code=500, detail="AWS credentials not configured")
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(f"AWS S3 error ({error_code}): {e}")
            raise HTTPException(status_code=500, detail=f"Failed to upload file to S3: {error_code}")
        except Exception as e:
            logger.error(f"Unexpected error during file upload: {e}")
            raise HTTPException(status_code=500, detail="File upload failed")

    def delete_file(self, file_url: str) -> bool:
        """Delete file from S3 using its URL"""
        try:
            # Extract key from URL
            if self.base_url in file_url:
                key = file_url.replace(f"{self.base_url}/", "")
                
                self.s3_client.delete_object(
                    Bucket=self.bucket_name,
                    Key=key
                )
                logger.info(f"File deleted successfully: {key}")
                return True
            else:
                logger.warning(f"Invalid file URL for deletion: {file_url}")
                return False
                
        except ClientError as e:
            logger.error(f"Failed to delete file from S3: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during file deletion: {e}")
            return False

    def check_bucket_exists(self) -> bool:
        """Check if S3 bucket exists and is accessible"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError:
            return False

    def configure_bucket_for_public_access(self) -> bool:
        """Configure bucket policy for public read access"""
        try:
            # Bucket policy for public read access
            bucket_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "PublicReadGetObject",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{self.bucket_name}/*"
                    }
                ]
            }
            
            # Apply bucket policy
            self.s3_client.put_bucket_policy(
                Bucket=self.bucket_name,
                Policy=json.dumps(bucket_policy)
            )
            
            logger.info(f"Bucket policy applied for public access: {self.bucket_name}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to configure bucket policy: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error configuring bucket: {e}")
            return False

# Create global instance
s3_service = S3Service()
