import logging
import sys
from pathlib import Path

LOG_DIR = Path(".")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "scraping.log"


def setup_logging():
    root_logger = logging.getLogger()
    if getattr(root_logger, "_wat2do_configured", False):
        return
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)
    apify_logger = logging.getLogger("apify_client")
    apify_logger.setLevel(logging.CRITICAL)
    apify_logger.propagate = False
    for h in list(apify_logger.handlers):
        apify_logger.removeHandler(h)
        
    logging.getLogger("apify").setLevel(logging.CRITICAL)
    logging.getLogger("cheerio").setLevel(logging.CRITICAL)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("s3transfer").setLevel(logging.WARNING)
    fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    handlers = [
        logging.StreamHandler(sys.stderr),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ]
    logging.basicConfig(level=logging.DEBUG, format=fmt, handlers=handlers)
    root_logger._wat2do_configured = True
    root_logger.propagate = False


setup_logging()
logger = logging.getLogger(__name__)
