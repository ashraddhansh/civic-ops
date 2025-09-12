import boto3
import uuid
import mimetypes
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
        # Check file size
        if file.size and file.size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE / (1024*1024):.1f}MB"
            )
        
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

    def generate_file_key(self, file: UploadFile, prefix: str = "uploads") -> str:
        """Generate unique file key for S3"""
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
        unique_id = str(uuid.uuid4())
        return f"{prefix}/{unique_id}.{file_extension}"

    async def upload_file(self, file: UploadFile, file_type: str = "image") -> str:
        """Upload file to S3 and return public URL"""
        try:
            # Validate file
            self.validate_file(file, file_type)
            
            # Generate unique key
            if file_type == "image":
                key = self.generate_file_key(file, "images")
            elif file_type == "audio":
                key = self.generate_file_key(file, "audio")
            else:
                key = self.generate_file_key(file, "files")
            
            # Read file content
            file_content = await file.read()
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_content,
                ContentType=file.content_type
                # ACL removed - bucket should be configured for public access via bucket policy
            )
            
            # Return public URL
            file_url = f"{self.base_url}/{key}"
            logger.info(f"File uploaded successfully: {file_url}")
            return file_url
            
        except HTTPException:
            raise
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            raise HTTPException(status_code=500, detail="AWS credentials not configured")
        except ClientError as e:
            logger.error(f"AWS S3 error: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload file to S3")
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

# Create global instance
s3_service = S3Service()
