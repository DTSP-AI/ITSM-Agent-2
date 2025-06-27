import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

def setup_logger(name: str = __name__) -> logging.Logger:
    """Set up a logger that streams to stdout with timestamped INFO level."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

logger = setup_logger() 