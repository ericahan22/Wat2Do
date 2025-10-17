import os
from pathlib import Path
from logging_config import logger


def setup_zyte():
    """
    Sets up Zyte CA certificate, sets environment variables for requests,
    returns cert path
    """
    cert_path = Path(__file__).parent / "certs" / "zyte-ca.crt"
    try:
        os.environ["REQUESTS_CA_BUNDLE"] = str(cert_path)
        os.environ["CURL_CA_BUNDLE"] = str(cert_path)
        os.environ["SSL_CERT_FILE"] = str(cert_path)
    except Exception as e:
        logger.error(f"Failed to set Zyte cert env vars: {e}")
    return cert_path
