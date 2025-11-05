import logging
import sys
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "scraping.log"


def setup_logging():
    root_logger = logging.getLogger()
    if getattr(root_logger, "_wat2do_configured", False):
        return
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.INFO)

    fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ]
    logging.basicConfig(level=logging.DEBUG, format=fmt, handlers=handlers)
    root_logger._wat2do_configured = True


setup_logging()
logger = logging.getLogger(__name__)
