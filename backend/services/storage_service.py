"""
Cloud storage service for file uploads and management.

This module provides methods for uploading and managing files in cloud storage,
specifically AWS S3. It handles image validation, optimization, and upload.
"""

import os
import boto3
import logging
from botocore.exceptions import ClientError, NoCredentialsError
import requests
from io import BytesIO
from PIL import Image
import uuid
from dotenv import load_dotenv
from typing import Optional


load_dotenv()
logger = logging.getLogger(__name__)

bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
region = os.getenv('AWS_DEFAULT_REGION', 'us-east-2')


def get_s3_client():
    try:
        s3_client = boto3.client('s3')
        return s3_client
    except Exception as e:
        logger.error(f"Failed to initialize S3 client: {e}")
        return None

s3_client = get_s3_client()

def _validate_image(image_data: bytes) -> bool:
    try:
        img = Image.open(BytesIO(image_data))
        
        if img.format not in ['JPEG', 'PNG', 'WEBP']:
            logger.warning(f"Unsupported image format: {img.format}")
            return False
        
        if len(image_data) > 10 * 1024 * 1024:  # 10MB limit
            logger.warning(f"Image too large: {len(image_data)} bytes")
            return False
            
        return True
    except Exception as e:
        logger.error(f"Image validation failed: {e}")
        return False


def _download_image_from_url(image_url: str) -> Optional[bytes]:
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


def upload_image_from_url(image_url: str, filename: Optional[str] = None) -> Optional[str]:
    try:
        image_data = _download_image_from_url(image_url)
        if not image_data:
            return None
        
        if not _validate_image(image_data):
            return None
        
        if not filename:
            file_ext = 'jpg'   
            try:
                img = Image.open(BytesIO(image_data))
                if img.format == 'PNG':
                    file_ext = 'png'
                elif img.format == 'WEBP':
                    file_ext = 'webp'
            except:
                pass
                
            filename = f"events/{uuid.uuid4()}.{file_ext}"
        
        logger.info(f"Uploading image to S3: {filename}")
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=image_data,
            ContentType=f'image/{filename.split(".")[-1]}',
            CacheControl='max-age=31536000',
            ACL='public-read'  
        
        public_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{filename}"
        logger.info(f"Successfully uploaded image: {filename}")
        
        return public_url
        
    except ClientError as e:
        logger.error(f"AWS S3 error uploading image: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error uploading image: {e}")
        return None


def upload_image_data(image_data: bytes, filename: str) -> Optional[str]:
    """
    Upload raw image data directly to S3.
    
    Args:
        image_data: Raw image bytes
        filename: Filename/key for the uploaded object
        
    Returns:
        Public URL of uploaded image if successful, None otherwise
    """
    try:
        if not _validate_image(image_data):
            return None
        
        logger.info(f"Uploading image data to S3: {filename}")
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=image_data,
            ContentType=f'image/{filename.split(".")[-1]}',
            CacheControl='max-age=31536000',
            ACL='public-read'
        )
        
        public_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{filename}"
        logger.info(f"Successfully uploaded image data: {filename}")
        
        return public_url
        
    except ClientError as e:
        logger.error(f"AWS S3 error uploading image data: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error uploading image data: {e}")
        return None


def delete_image(filename: str) -> bool:
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=filename)
        logger.info(f"Successfully deleted image: {filename}")
        return True
    except Exception as e:
        logger.error(f"Error deleting image {filename}: {e}")
        return False


