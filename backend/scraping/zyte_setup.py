import os
import ssl
from pathlib import Path

from scraping.logging_config import logger


def setup_zyte():
    """
    Sets up Zyte CA certificate, sets environment variables for requests,
    returns cert path
    """
    cert_dir = Path(__file__).parent / "certs"
    zyte_cert = cert_dir / "zyte-ca.crt"
    zyte_bundle = cert_dir / "zyte-ca-bundle.crt"

    sys_cafile = (
        ssl.get_default_verify_paths().cafile or "/etc/ssl/certs/ca-certificates.crt"
    )
    cert_path = Path(sys_cafile)

    if zyte_cert.exists():
        try:
            with open(zyte_bundle, "wb") as out:
                with open(sys_cafile, "rb") as s:
                    out.write(s.read())
                out.write(b"\n")
                with open(zyte_cert, "rb") as z:
                    out.write(z.read())
            cert_path = zyte_bundle
            logger.info(f"Created CA bundle with Zyte CA at {cert_path}")
        except Exception as e:
            logger.error(
                f"Failed to create Zyte CA bundle: {e}, falling back to zyte-ca.crt"
            )
            cert_path = zyte_cert

    if cert_path.exists():
        os.environ["REQUESTS_CA_BUNDLE"] = str(cert_path)
        os.environ["CURL_CA_BUNDLE"] = str(cert_path)
        os.environ["SSL_CERT_FILE"] = str(cert_path)
        logger.info(f"Exported CA bundle for TLS verification: {cert_path}")
    else:
        logger.warning("No CA bundle available, TLS verification may fail")

    return cert_path
