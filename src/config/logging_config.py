"""
Logging Configuration Module

Configures logging for the MoneyFlow application with appropriate levels,
formats, and handlers for both development and production environments.
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
import sys
import os

def setup_logging(log_level: str = "INFO", log_to_file: bool = True, log_to_console: bool = True):
    """
    Setup logging configuration for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to file
        log_to_console: Whether to log to console
    """
    # Import here to avoid circular imports
    from config.paths import get_logs_directory
    
    # Use proper user data directory for logs
    log_dir = get_logs_directory()
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_to_file:
        log_file = log_dir / f"moneyflow_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # Always log DEBUG to file
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    configure_logger_levels()
    
    logging.info("Logging configuration initialized")
    logging.info(f"Log level: {log_level}, File logging: {log_to_file}, Console logging: {log_to_console}")

def configure_logger_levels():
    """Configure specific logger levels for different modules."""
    
    # Reduce noise from external libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('pymongo').setLevel(logging.WARNING)
    logging.getLogger('pandas').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.INFO)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    
    # Set application-specific logger levels
    logging.getLogger('src.core').setLevel(logging.INFO)
    logging.getLogger('src.ui').setLevel(logging.INFO)
    logging.getLogger('src.config').setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)

def log_function_call(func):
    """
    Decorator to log function calls with parameters and execution time.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        func_name = func.__qualname__
        
        # Log function entry
        logger.debug(f"Entering {func_name}")
        
        start_time = datetime.now()
        try:
            result = func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            logger.debug(f"Completed {func_name} in {execution_time:.1f}ms")
            return result
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            logger.error(f"Error in {func_name} after {execution_time:.1f}ms: {e}")
            raise
    
    return wrapper

def log_performance(operation: str):
    """
    Context manager to log performance of operations.
    
    Args:
        operation: Description of the operation being timed
    """
    class PerformanceLogger:
        def __init__(self, operation: str):
            self.operation = operation
            self.logger = get_logger('performance')
            self.start_time = None
        
        def __enter__(self):
            self.start_time = datetime.now()
            self.logger.debug(f"Starting {self.operation}")
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.start_time:
                execution_time = (datetime.now() - self.start_time).total_seconds() * 1000
                if exc_type:
                    self.logger.error(f"Failed {self.operation} after {execution_time:.1f}ms: {exc_val}")
                else:
                    self.logger.info(f"Completed {self.operation} in {execution_time:.1f}ms")
    
    return PerformanceLogger(operation)

def setup_development_logging():
    """Setup logging for development environment."""
    setup_logging(
        log_level="DEBUG",
        log_to_file=True,
        log_to_console=True
    )

def setup_production_logging():
    """Setup logging for production environment."""
    setup_logging(
        log_level="INFO",
        log_to_file=True,
        log_to_console=False
    )

# Initialize logging on module import
if __name__ != "__main__":
    # Auto-detect environment
    if os.getenv("ENVIRONMENT", "development").lower() == "production":
        setup_production_logging()
    else:
        setup_development_logging()
