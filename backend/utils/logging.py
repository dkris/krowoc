import sys
import os
import uuid
from datetime import datetime
from flask import request, has_request_context
from loguru import logger

def setup_logging():
    """Configure loguru for structured logging"""
    
    # Remove default handlers
    logger.remove()
    
    # Determine log level from environment (default to INFO)
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
    
    # Configure JSON structured logging format
    logger.add(
        sys.stderr,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {extra[request_id]} | {message}",
        level=LOG_LEVEL,
        serialize=False,  # Set to True for JSON format in production
    )
    
    # Add file logging in production
    if os.environ.get("FLASK_ENV") == "production":
        log_path = os.environ.get("LOG_PATH", "/var/log/krowoc")
        os.makedirs(log_path, exist_ok=True)
        logger.add(
            f"{log_path}/krowoc.log",
            rotation="100 MB",
            retention="14 days",
            level=LOG_LEVEL,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {extra[request_id]} | {message}",
            serialize=True,  # JSON format for file logs
        )
    
    logger.info("Logging configured with level {}", LOG_LEVEL)

def request_id_contextualizer():
    """Generate or retrieve a unique request ID for correlation"""
    if has_request_context():
        # Try to get request ID from headers if available
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())
    else:
        request_id = "no-request-id"
    
    return {"request_id": request_id}

def get_contextual_logger():
    """Get a logger instance with context information"""
    return logger.bind(**request_id_contextualizer()) 