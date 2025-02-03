import logging
from logging.handlers import RotatingFileHandler
import sys
import os
from enum import StrEnum

class LoggerToolLevel(StrEnum):
    L1 = "assistant_only"
    L2 = "assistant_tool_use"
    L3 = "assistant_tool_use_output"
    ALL = "all"

def setup_logger(
    name: str,
    log_file: str = "",
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5,
    formatter: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    log_level: logging = logging.INFO
) -> logging.Logger:
    """
    Setup logger with:
    - File handler that captures all levels with rotation
    - Stream handler that only captures DEBUG level
    """   
    # Create logger
    logger = logging.getLogger(name)
    
    # Clear any existing handlers
    if logger.handlers:
        logger.handlers.clear()
    
    # Set level
    logger.setLevel(log_level)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    # Create formatter
    formatter = logging.Formatter(
        formatter
    )
    
    # File handler - captures everything with rotation
    if log_file:
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(log_level) 
        file_handler.setFormatter(formatter)
     
    # Stream handler - only debug messages
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(log_level)  # Only DEBUG level
    stream_handler.setFormatter(formatter)
    
    # Remove any existing handlers
    logger.handlers = []
    
    # Add handlers to logger
    if log_file:
        logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    
    return logger