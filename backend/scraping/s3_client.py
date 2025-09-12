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
    """
    AWS S3 client for uploading Instagram images and generating presigned URLs.
    """
    
    def __init__(self):
        """
        Initialize S3 client with AWS credentials from environment variables.
        """
        self.s3_client = None
        self.bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
        self.region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        
        # Initialize S3 client only if credentials are available
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
        """
        Validate image format and size.
        
        Args:
            image_data (bytes): Image data to validate
            
        Returns:
            bool: True if image is valid, False otherwise
        """
        try:
            # Check if image data is valid
            img = Image.open(BytesIO(image_data))
            
            # Check format
            if img.format not in ['JPEG', 'PNG', 'WEBP']:
                logger.warning(f"Unsupported image format: {img.format}")
                return False
            
            # Check size (max 10MB)
            if len(image_data) > 10 * 1024 * 1024:
                logger.warning(f"Image too large: {len(image_data)} bytes")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Image validation failed: {e}")
            return False
    
    def _download_image_from_url(self, image_url):
        """
        Download image from Instagram URL.
        
        Args:
            image_url (str): URL to download image from
            
        Returns:
            bytes: Image data or None if failed
        """
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
        """
        Upload image to S3 and return presigned URL.
        
        Args:
            image_url (str): Instagram image URL to download and upload
            filename (str, optional): Custom filename for S3 object
            
        Returns:
            str: Presigned URL for uploaded image or None if failed
        """
        if not self.s3_client or not self.bucket_name:
            logger.warning("S3 client not configured. Skipping image upload.")
            return None
        
        try:
            # Download image from Instagram
            image_data = self._download_image_from_url(image_url)
            if not image_data:
                return None
            
            # Validate image
            if not self._validate_image(image_data):
                return None
            
            # Generate unique filename if not provided
            if not filename:
                # Extract file extension from content type or URL
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
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=filename,
                Body=image_data,
                ContentType=f'image/{filename.split(".")[-1]}',
                CacheControl='max-age=31536000'  # Cache for 1 year
            )
            
            # Generate presigned URL
            presigned_url = self.generate_presigned_url(filename)
            logger.info(f"Successfully uploaded image: {filename}")
            
            return presigned_url
            
        except ClientError as e:
            logger.error(f"AWS S3 error uploading image: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error uploading image: {e}")
            return None
    
    def generate_presigned_url(self, s3_key, expiration=3600*24*365):
        """
        Generate presigned URL for S3 object.
        
        Args:
            s3_key (str): S3 object key
            expiration (int): URL expiration time in seconds (default: 1 year)
            
        Returns:
            str: Presigned URL or None if failed
        """
        if not self.s3_client or not self.bucket_name:
            logger.warning("S3 client not configured. Cannot generate presigned URL.")
            return None
        
        try:
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return presigned_url
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {e}")
            return None