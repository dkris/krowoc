import time
from flask import request, g
from .logging import get_contextual_logger, request_id_contextualizer
from .analytics import set_correlation_id, track_api_request

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
            
            # Add X-Correlation-ID to response headers
            if hasattr(g, 'correlation_id'):
                headers = list(headers)
                headers.append(('X-Correlation-ID', g.correlation_id))
            
            if status_code >= 500:
                logger.error("Request failed: {}", log_data)
            elif status_code >= 400:
                logger.warning("Request error: {}", log_data)
            else:
                logger.info("Request completed: {}", log_data)
            
            # Track the request in PostHog (only for non-health endpoints)
            if '/health' not in path:
                try:
                    track_api_request(path, method, status_code)
                except Exception as e:
                    logger.error("Failed to track API request: {}", str(e))
            
            return start_response(status, headers, exc_info)
        
        # Log the incoming request
        logger.info("Request started: {} {}", method, path)
        
        # Pass to the rest of the application
        return self.app(environ, custom_start_response)


def setup_request_context():
    """Setup request context before processing request"""
    g.start_time = time.time()
    
    # Set request ID for logging
    g.request_id = request_id_contextualizer()["request_id"]
    request.request_id = g.request_id  # Make easily accessible on request
    
    # Set correlation ID for cross-service tracking
    g.correlation_id = set_correlation_id()
    
    # Prefer correlation_id over request_id if they differ
    if g.correlation_id != g.request_id:
        # Update the request_id to match correlation_id for consistency
        g.request_id = g.correlation_id
        request.request_id = g.correlation_id
    
    # Log the request
    logger.info(
        "Received request: {} {}",
        request.method,
        request.path,
        extra={
            "ip": request.remote_addr,
            "user_agent": request.user_agent.string if request.user_agent else "Unknown",
            "query_params": dict(request.args),
            "correlation_id": g.correlation_id
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
            "duration_ms": duration_ms,
            "correlation_id": g.correlation_id if hasattr(g, 'correlation_id') else "no-correlation-id"
        }
    )
    
    # Add correlation ID to response headers for tracking
    if hasattr(g, 'correlation_id'):
        response.headers['X-Correlation-ID'] = g.correlation_id
    
    # Add request ID to response headers for debugging/tracing
    if hasattr(g, 'request_id'):
        response.headers['X-Request-ID'] = g.request_id
    
    return response 