import os
import boto3
import logging
from botocore.exceptions import ClientError, NoCredentialsError
from urllib.parse import urlparse
import requests
from io import BytesIO
from PIL import Image
import uuid

logger = logging.getLogger(__name__)

class S3ImageUploader:
    def __init__(self):
        self.s3_client = None
        self.bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
        self.region = os.getenv('AWS_DEFAULT_REGION', 'us-east-2')
        print(f"S3 client initialized with bucket name: {self.bucket_name} and region: {self.region}")
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=self.region
            )
            logger.info("S3 client initialized successfully")
        except NoCredentialsError:
            logger.warning("AWS credentials not found. S3 image upload will be disabled.")
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
    
    def _validate_image(self, image_data):

        try:
            img = Image.open(BytesIO(image_data))
            
            if img.format not in ['JPEG', 'PNG', 'WEBP']:
                logger.warning(f"Unsupported image format: {img.format}")
                return False
            
            if len(image_data) > 10 * 1024 * 1024:
                logger.warning(f"Image too large: {len(image_data)} bytes")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Image validation failed: {e}")
            return False
    
    def _download_image_from_url(self, image_url):

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(image_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            return response.content
        except Exception as e:
            logger.error(f"Failed to download image from {image_url}: {e}")
            return None
    
    def upload_image(self, image_url, filename=None):

        if not self.s3_client or not self.bucket_name:
            logger.warning("S3 client not configured. Skipping image upload.")
            return None
        
        try:
            image_data = self._download_image_from_url(image_url)
            if not image_data:
                return None
            
            if not self._validate_image(image_data):
                return None
            
            if not filename:
                file_ext = 'jpg'  # default
                try:
                    img = Image.open(BytesIO(image_data))
                    if img.format == 'PNG':
                        file_ext = 'png'
                    elif img.format == 'WEBP':
                        file_ext = 'webp'
                except:
                    pass
                    
                filename = f"events/{uuid.uuid4()}.{file_ext}"
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=filename,
                Body=image_data,
                ContentType=f'image/{filename.split(".")[-1]}',
                CacheControl='max-age=31536000',
                ACL='public-read'  # Make the object publicly accessible
            )
            
            # Generate permanent public URL instead of presigned URL
            public_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{filename}"
            logger.info(f"Successfully uploaded image: {filename}")
            
            return public_url
            
        except ClientError as e:
            logger.error(f"AWS S3 error uploading image: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error uploading image: {e}")
            return None
    