"""
Logging configuration for monitoring.
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


def setup_monitoring_logger(
    name: str = "wheres_my_taxi_monitoring",
    log_file: str = "monitoring/logs/monitoring.log"
) -> logging.Logger:
    """
    Setup a logger for monitoring with both file and console output.
    
    Args:
        name: Logger name
        log_file: Path to log file
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)
    
    # Console handler  
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


class StructuredLogger:
    """Structured logging for monitoring events."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_event(self, event_type: str, data: Dict[str, Any], level: str = "INFO"):
        """
        Log a structured monitoring event.
        
        Args:
            event_type: Type of event (e.g., 'model_training', 'data_quality_check')
            data: Event data dictionary
            level: Log level (INFO, WARNING, ERROR)
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "data": data
        }
        
        log_message = json.dumps(event, default=str)
        
        if level.upper() == "INFO":
            self.logger.info(log_message)
        elif level.upper() == "WARNING":
            self.logger.warning(log_message)
        elif level.upper() == "ERROR":
            self.logger.error(log_message)
        else:
            self.logger.info(log_message)