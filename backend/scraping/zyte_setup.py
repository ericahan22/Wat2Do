import os
import boto3
from botocore.exceptions import ClientError
from pathlib import Path
from backend.scraping.logging_config import logger


def setup_zyte():
    """
    Downloads Zyte CA certificate from S3,
    sets environment variables for requests, returns cert path
    """
    bucket = os.getenv("AWS_S3_BUCKET_NAME")
    key = "zyte-ca.crt"

    cert_dir = Path(__file__).parent / "zyte"
    cert_dir.mkdir(exist_ok=True)
    cert_path = cert_dir / key

    # Download certificate from S3
    if not cert_path.exists():
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_DEFAULT_REGION"),
        )
        try:
            s3.download_file(bucket, key, str(cert_path))
            logger.info(f"Zyte certificate downloaded to {cert_path}")
        except ClientError as e:
            logger.error(f"Failed to download Zyte cert from S3: {e}")

    # Set environment variables
    os.environ["REQUESTS_CA_BUNDLE"] = str(cert_path)
    os.environ["CURL_CA_BUNDLE"] = str(cert_path)
    return cert_path
