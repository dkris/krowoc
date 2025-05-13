import time
from flask import request, g
from .logging import get_contextual_logger, request_id_contextualizer

logger = get_contextual_logger()

class RequestLoggingMiddleware:
    """Middleware to log requests and responses with timing information"""
    
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        # Get the request path and method for logging
        path = environ.get('PATH_INFO', '')
        method = environ.get('REQUEST_METHOD', '')
        
        # Skip logging for certain paths (e.g. health checks, if they happen frequently)
        if path == '/health' and method == 'GET':
            return self.app(environ, start_response)
        
        # Start timer
        start_time = time.time()
        
        # Process the request
        def custom_start_response(status, headers, exc_info=None):
            # Log the request once we have the status code
            status_code = int(status.split(' ')[0])
            duration_ms = int((time.time() - start_time) * 1000)
            
            log_data = {
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration_ms": duration_ms
            }
            
            if status_code >= 500:
                logger.error("Request failed: {}", log_data)
            elif status_code >= 400:
                logger.warning("Request error: {}", log_data)
            else:
                logger.info("Request completed: {}", log_data)
            
            return start_response(status, headers, exc_info)
        
        # Log the incoming request
        logger.info("Request started: {} {}", method, path)
        
        # Pass to the rest of the application
        return self.app(environ, custom_start_response)


def setup_request_context():
    """Setup request context before processing request"""
    g.start_time = time.time()
    g.request_id = request_id_contextualizer()["request_id"]
    request.request_id = g.request_id  # Make easily accessible on request
    
    # Log the request
    logger.info(
        "Received request: {} {}",
        request.method,
        request.path,
        extra={
            "ip": request.remote_addr,
            "user_agent": request.user_agent.string if request.user_agent else "Unknown",
            "query_params": dict(request.args)
        }
    )


def teardown_request_context(response):
    """Log the response after request is processed"""
    duration_ms = int((time.time() - g.start_time) * 1000)
    
    logger.info(
        "Completed request: {} {} - {} in {}ms",
        request.method,
        request.path,
        response.status_code,
        duration_ms,
        extra={
            "status_code": response.status_code,
            "duration_ms": duration_ms
        }
    )
    
    # Add request ID to response headers for debugging/tracing
    response.headers['X-Request-ID'] = g.request_id
    return response 