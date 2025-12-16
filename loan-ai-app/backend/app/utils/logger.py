import logging
import sys
from pathlib import Path
from app.config import settings

def setup_logger():
    """Setup application logger"""
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Set log level based on environment
    log_level = logging.DEBUG if settings.debug else logging.INFO
    
    # Configure handlers
    handlers = [
        logging.StreamHandler(sys.stdout)
    ]
    
    # Add file handler in production
    if settings.environment == "production":
        file_handler = logging.FileHandler('logs/app.log')
        file_handler.setFormatter(logging.Formatter(log_format, date_format))
        handlers.append(file_handler)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=handlers
    )
    
    logger = logging.getLogger("loan_ai_app")
    logger.info(f"Logger initialized - Environment: {settings.environment}")
    
    return logger

# Initialize logger
logger = setup_logger()


