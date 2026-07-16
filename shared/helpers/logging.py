import os
import sys
import logging
from logging.handlers import RotatingFileHandler

def setup_production_logging() -> None:
    """Setup file-based and console logging for production."""
    log_dir = os.path.expanduser("~/.gymos/logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "gymos.log")
    
    # Get the root logger
    root_logger = logging.getLogger()
    # Avoid duplicate handlers if already called
    if not root_logger.handlers:
        root_logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # Rotating File handler
        try:
            file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except Exception as e:
            # Fallback to sys.stderr if file cannot be created/written
            sys.stderr.write(f"Failed to initialize file logging: {e}\n")
