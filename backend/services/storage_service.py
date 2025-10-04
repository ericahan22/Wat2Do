"""
Cloud storage service for file uploads and management.

This module provides methods for uploading and managing files in cloud storage,
specifically AWS S3. It handles image validation, optimization, and upload.
"""

import logging
import os
import uuid
from io import BytesIO

import boto3
import requests
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from PIL import Image

load_dotenv()
logger = logging.getLogger(__name__)

bucket_name = os.getenv("AWS_S3_BUCKET_NAME")
region = os.getenv("AWS_DEFAULT_REGION", "us-east-2")


def get_s3_client():
    try:
        s3_client = boto3.client("s3")
        return s3_client
    except Exception:
        logger.exception("Failed to initialize S3 client")
        return None


s3_client = get_s3_client()


def _validate_image(image_data: bytes) -> bool:
    try:
        img = Image.open(BytesIO(image_data))

        if img.format not in ["JPEG", "PNG", "WEBP"]:
            logger.warning(f"Unsupported image format: {img.format}")
            return False

        if len(image_data) > 10 * 1024 * 1024:  # 10MB limit
            logger.warning(f"Image too large: {len(image_data)} bytes")
            return False

        return True
    except Exception:
        logger.exception("Image validation failed")
        return False


def _download_image_from_url(image_url: str) -> bytes | None:
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
        }
        response = requests.get(image_url, headers=headers, timeout=30)
        response.raise_for_status()

        return response.content
    except Exception:
        logger.exception(f"Failed to download image from {image_url}")
        return None


def upload_image_from_url(image_url: str, filename: str | None = None) -> str | None:
    try:
        image_data = _download_image_from_url(image_url)
        if not image_data:
            return None

        if not _validate_image(image_data):
            return None

        if not filename:
            file_ext = "jpg"
            try:
                img = Image.open(BytesIO(image_data))
                if img.format == "PNG":
                    file_ext = "png"
                elif img.format == "WEBP":
                    file_ext = "webp"
            except Exception as e:
                logger.warning(f"Could not detect image format: {e}, defaulting to jpg")
                pass

            filename = f"events/{uuid.uuid4()}.{file_ext}"

        logger.info(f"Uploading image to S3: {filename}")

        s3_client.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=image_data,
            ContentType=f'image/{filename.split(".")[-1]}',
            CacheControl="max-age=31536000",
            ACL="public-read",
        )

        public_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{filename}"
        logger.info(f"Successfully uploaded image: {filename}")

        return public_url

    except ClientError:
        logger.exception("AWS S3 error uploading image")
        return None
    except Exception:
        logger.exception("Unexpected error uploading image")
        return None


def upload_image_data(image_data: bytes, filename: str) -> str | None:
    try:
        if not _validate_image(image_data):
            return None

        logger.info(f"Uploading image data to S3: {filename}")

        s3_client.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=image_data,
            ContentType=f'image/{filename.split(".")[-1]}',
            CacheControl="max-age=31536000",
            ACL="public-read",
        )

        public_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{filename}"
        logger.info(f"Successfully uploaded image data: {filename}")

        return public_url

    except ClientError:
        logger.exception("AWS S3 error uploading image data")
        return None
    except Exception:
        logger.exception("Unexpected error uploading image data")
        return None


def delete_images(filenames: list[str]) -> int:
    logger.info(f"Deleting {len(filenames)} images from S3...")
    try:
        delete_objects = [{"Key": key} for key in filenames]

        response = s3_client.delete_objects(
            Bucket=bucket_name, Delete={"Objects": delete_objects, "Quiet": False}
        )

        deleted_count = len(response.get("Deleted", []))

        logger.info(f"Successfully deleted {deleted_count} images")
        return deleted_count

    except ClientError:
        logger.exception("AWS S3 error deleting images")
        return 0
    except Exception:
        logger.exception("Unexpected error deleting images")
        return 0


def list_all_s3_objects() -> list[str]:
    logger.info("Listing all objects in S3 bucket...")
    try:
        all_keys = []
        paginator = s3_client.get_paginator("list_objects_v2")

        for page in paginator.paginate(Bucket=bucket_name):
            if "Contents" in page:
                all_keys.extend(obj["Key"] for obj in page["Contents"])

        logger.info(f"Found {len(all_keys)} total objects in S3 bucket")
        return all_keys

    except ClientError:
        logger.exception("Error listing S3 objects")
        raise
    except Exception:
        logger.exception("Unexpected error listing S3 objects")
        raise
