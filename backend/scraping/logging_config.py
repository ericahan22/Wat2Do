import logging
import sys
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "scraping.log"

root_logger = logging.getLogger()
if not root_logger.handlers:
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    fmt = "%(asctime)s - pid=%(process)d - thread=%(threadName)s - %(name)s - %(levelname)s - %(message)s"
    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ]
    logging.basicConfig(level=logging.DEBUG, format=fmt, handlers=handlers)
else:
    root_logger.setLevel(root_logger.level or logging.DEBUG)

logger = logging.getLogger(__name__)
