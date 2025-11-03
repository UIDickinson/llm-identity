import logging
import sys
from pathlib import Path
from pythonjsonlogger import jsonlogger

from ..agent.config import settings


def get_logger(name: str) -> logging.Logger:
    """Get configured logger"""
    
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(getattr(logging, settings.log_level.upper()))
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        
        if settings.environment == "production":
            # JSON format for production
            formatter = jsonlogger.JsonFormatter(
                '%(asctime)s %(name)s %(levelname)s %(message)s'
            )
        else:
            # Human-readable for development
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler (optional)
        log_dir = Path("./logs")
        log_dir.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(log_dir / "guardian.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger