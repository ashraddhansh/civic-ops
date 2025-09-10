# AWS S3 Setup Instructions

## Prerequisites
- AWS Account (free tier available)
- boto3 and python-multipart installed (already done)

## Step 1: Create AWS Account
1. Go to https://aws.amazon.com/
2. Sign up for AWS account
3. Verify your account with credit card (won't be charged for free tier)

## Step 2: Create S3 Bucket
1. Login to AWS Console
2. Go to S3 service
3. Click "Create bucket"
4. **Bucket name**: Choose unique name (e.g., `civic-app-uploads-yourname123`)
5. **Region**: Choose closest to your location (e.g., us-east-1)
6. **Public access settings**: 
   - ❌ UNCHECK "Block all public access"
   - ✅ Acknowledge the warning
7. **Bucket versioning**: Disabled (for simplicity)
8. Click "Create bucket"

## Step 3: Configure Bucket for Public Access
1. Go to your bucket
2. Click "Permissions" tab
3. Edit "Bucket policy" and add this policy (replace YOUR-BUCKET-NAME):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"
        }
    ]
}
```

## Step 4: Create IAM User
1. Go to IAM service in AWS Console
2. Click "Users" → "Create user"
3. **Username**: `civic-app-s3-user`
4. **Access type**: ✅ Programmatic access
5. **Permissions**: 
   - Click "Attach policies directly"
   - Search and select "AmazonS3FullAccess"
6. Click "Create user"
7. **IMPORTANT**: Save the credentials shown:
   - Access Key ID
   - Secret Access Key

## Step 5: Update Environment Variables
Update your `.env` file with your AWS credentials:

```bash
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-actual-bucket-name

# File Upload Settings
MAX_FILE_SIZE=10485760
```

## Step 6: Test S3 Setup
After updating your credentials, test the setup:

```bash
curl http://localhost:8000/health/s3
```

Should return:
```json
{
    "status": "healthy",
    "bucket_name": "your-bucket-name",
    "bucket_accessible": true
}
```

## Security Best Practices

### For Production:
1. **Create custom IAM policy** (instead of S3FullAccess):
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::your-bucket-name/*"
        },
        {
            "Effect": "Allow",
            "Action": "s3:ListBucket",
            "Resource": "arn:aws:s3:::your-bucket-name"
        }
    ]
}
```

2. **Enable bucket versioning** for file recovery
3. **Set up lifecycle policies** to manage storage costs
4. **Use CloudFront** for faster file delivery
5. **Enable server-side encryption**

## Supported File Types

### Images:
- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- WebP (.webp)

### Audio:
- MP3 (.mp3)
- WAV (.wav)
- M4A (.m4a)
- OGG (.ogg)

### File Size Limit:
- Maximum: 10MB per file
- Configurable via MAX_FILE_SIZE environment variable

## New API Endpoints

### Create Issue with Files:
```
POST /users/issues/with-files
Content-Type: multipart/form-data

Fields:
- title (required)
- description (required)
- category (required)
- location (optional)
- latitude (optional)
- longitude (optional)
- photo (optional file)
- voice_note (optional file)
```

### Upload Photo to Existing Issue:
```
PATCH /users/issues/{issue_id}/upload-photo
Content-Type: multipart/form-data

Fields:
- photo (required file)
```

### Upload Voice Note to Existing Issue:
```
PATCH /users/issues/{issue_id}/upload-voice
Content-Type: multipart/form-data

Fields:
- voice_note (required file)
```

## Troubleshooting

### Common Issues:

1. **"AWS credentials not configured"**
   - Check your .env file has correct AWS credentials
   - Ensure credentials are not wrapped in quotes

2. **"Bucket not accessible"**
   - Verify bucket name is correct
   - Check IAM user has S3 permissions
   - Ensure bucket exists in the specified region

3. **"File too large"**
   - Check file is under 10MB
   - Adjust MAX_FILE_SIZE if needed

4. **"Invalid file type"**
   - Ensure file is supported type
   - Check MIME type is correct

## Cost Considerations

### AWS Free Tier (first 12 months):
- 5GB S3 storage
- 20,000 GET requests
- 2,000 PUT requests per month

### After free tier:
- Storage: ~$0.023 per GB per month
- Requests: ~$0.0004 per 1,000 requests

For a civic app prototype, costs should be minimal.
