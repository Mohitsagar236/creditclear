"""
Logging configuration and utilities.

This module provides centralized logging configuration for the credit risk model,
including structured logging, log rotation, and different output formats.
"""

import logging
import logging.config
import logging.handlers
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
import json
from datetime import datetime
import traceback


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs structured JSON logs.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as structured JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON formatted log string
        """
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'process_id': os.getpid(),
            'thread_id': record.thread
        }
        
        # Add exception information if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data, default=str)


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds colors to console output.
    """
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record with colors.
        
        Args:
            record: Log record to format
            
        Returns:
            Colored log string
        """
        # Add color to level name
        level_color = self.COLORS.get(record.levelname, '')
        reset_color = self.COLORS['RESET']
        
        # Create colored level name
        colored_level = f"{level_color}{record.levelname}{reset_color}"
        
        # Format the message
        log_format = f"%(asctime)s - {colored_level} - %(name)s - %(message)s"
        formatter = logging.Formatter(log_format)
        
        return formatter.format(record)


class CreditRiskLogger:
    """
    Credit risk model specific logger with enhanced functionality.
    """
    
    def __init__(self, name: str):
        """
        Initialize the credit risk logger.
        
        Args:
            name: Logger name
        """
        self.logger = logging.getLogger(name)
        self.name = name
    
    def log_model_training(self, model_name: str, **kwargs):
        """
        Log model training information.
        
        Args:
            model_name: Name of the model being trained
            **kwargs: Additional training parameters
        """
        extra_fields = {
            'event_type': 'model_training',
            'model_name': model_name,
            'training_params': kwargs
        }
        
        self.logger.info(
            f"Starting training for model: {model_name}",
            extra={'extra_fields': extra_fields}
        )
    
    def log_model_prediction(self, model_name: str, prediction_count: int, **kwargs):
        """
        Log model prediction information.
        
        Args:
            model_name: Name of the model making predictions
            prediction_count: Number of predictions made
            **kwargs: Additional prediction metadata
        """
        extra_fields = {
            'event_type': 'model_prediction',
            'model_name': model_name,
            'prediction_count': prediction_count,
            'prediction_metadata': kwargs
        }
        
        self.logger.info(
            f"Model {model_name} made {prediction_count} predictions",
            extra={'extra_fields': extra_fields}
        )
    
    def log_data_collection(self, source_type: str, record_count: int, **kwargs):
        """
        Log data collection information.
        
        Args:
            source_type: Type of data source
            record_count: Number of records collected
            **kwargs: Additional collection metadata
        """
        extra_fields = {
            'event_type': 'data_collection',
            'source_type': source_type,
            'record_count': record_count,
            'collection_metadata': kwargs
        }
        
        self.logger.info(
            f"Collected {record_count} records from {source_type}",
            extra={'extra_fields': extra_fields}
        )
    
    def log_api_request(self, endpoint: str, method: str, status_code: int, **kwargs):
        """
        Log API request information.
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            status_code: Response status code
            **kwargs: Additional request metadata
        """
        extra_fields = {
            'event_type': 'api_request',
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'request_metadata': kwargs
        }
        
        level = logging.INFO if 200 <= status_code < 400 else logging.WARNING
        self.logger.log(
            level,
            f"{method} {endpoint} - {status_code}",
            extra={'extra_fields': extra_fields}
        )


def setup_logging(
    log_level: str = "INFO",
    log_format: str = "standard",
    log_file: Optional[str] = None,
    log_dir: Optional[str] = None,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    enable_console: bool = True
) -> None:
    """
    Set up centralized logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format ("standard", "structured", "colored")
        log_file: Optional log file name
        log_dir: Optional log directory path
        max_file_size: Maximum log file size in bytes
        backup_count: Number of backup files to keep
        enable_console: Whether to enable console logging
    """
    # Convert log level string to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create log directory if specified
    if log_dir:
        log_dir_path = Path(log_dir)
        log_dir_path.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Set up formatters
    formatters = {
        'standard': logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ),
        'structured': StructuredFormatter(),
        'colored': ColoredFormatter()
    }
    
    formatter = formatters.get(log_format, formatters['standard'])
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        
        # Use colored formatter for console if available
        if log_format == "colored" and sys.stdout.isatty():
            console_handler.setFormatter(formatters['colored'])
        else:
            console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        if log_dir:
            log_file_path = Path(log_dir) / log_file
        else:
            log_file_path = Path(log_file)
        
        # Create rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file_path,
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger('uvicorn').setLevel(logging.WARNING)
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)


def get_logger(name: str) -> CreditRiskLogger:
    """
    Get a credit risk specific logger.
    
    Args:
        name: Logger name
        
    Returns:
        CreditRiskLogger instance
    """
    return CreditRiskLogger(name)


def configure_default_logging():
    """
    Configure default logging for the credit risk model.
    """
    # Get log directory from config or use default
    try:
        from .config import get_config
        config = get_config()
        log_dir = str(config.logs_dir)
    except ImportError:
        log_dir = "logs"
    
    setup_logging(
        log_level="INFO",
        log_format="standard",
        log_file="credit_risk_model.log",
        log_dir=log_dir,
        enable_console=True
    )


# Configure default logging when module is imported
if not logging.getLogger().handlers:
    configure_default_logging()
