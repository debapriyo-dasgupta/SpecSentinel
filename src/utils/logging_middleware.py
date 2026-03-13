"""
SpecSentinel Logging Middleware
Request/Response logging for FastAPI and Flask
"""

import time
import logging
from typing import Callable, Optional
from functools import wraps

from .logging_config import RequestLogger

# ── FastAPI Middleware ────────────────────────────────────────────────────────

try:
    from fastapi import Request, Response
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.types import ASGIApp
    
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


if FASTAPI_AVAILABLE:
    class FastAPILoggingMiddleware(BaseHTTPMiddleware):
        """
        FastAPI middleware for request/response logging.
        
        Usage:
            from src.utils.logging_middleware import FastAPILoggingMiddleware
            app.add_middleware(FastAPILoggingMiddleware)
        """
        
        def __init__(self, app: ASGIApp, logger_name: str = "specsentinel.api"):
            super().__init__(app)
            self.request_logger = RequestLogger(logger_name)
        
        async def dispatch(self, request: Request, call_next: Callable):
            # Start timing
            start_time = time.time()
            
            # Extract request info
            method = request.method
            path = request.url.path
            client_ip = request.client.host if request.client else "unknown"
            user_agent = request.headers.get("user-agent", "unknown")
            
            # Log request
            self.request_logger.log_request(
                method=method,
                path=path,
                client_ip=client_ip,
                user_agent=user_agent,
                query_params=str(request.query_params) if request.query_params else None
            )
            
            try:
                # Process request
                response = await call_next(request)
                
                # Calculate duration
                duration_ms = (time.time() - start_time) * 1000
                
                # Log response
                self.request_logger.log_response(
                    method=method,
                    path=path,
                    status_code=response.status_code,
                    duration_ms=duration_ms
                )
                
                return response
                
            except Exception as e:
                # Log error
                duration_ms = (time.time() - start_time) * 1000
                self.request_logger.log_error(
                    method=method,
                    path=path,
                    error=e,
                    duration_ms=duration_ms
                )
                raise


# ── Flask Middleware ──────────────────────────────────────────────────────────

try:
    from flask import Flask, request, g
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False


if FLASK_AVAILABLE:
    class FlaskLoggingMiddleware:
        """
        Flask middleware for request/response logging.
        
        Usage:
            from src.utils.logging_middleware import FlaskLoggingMiddleware
            FlaskLoggingMiddleware(app)
        """
        
        def __init__(self, app: Flask, logger_name: str = "specsentinel.frontend"):
            self.app = app
            self.request_logger = RequestLogger(logger_name)
            self._setup_hooks()
        
        def _setup_hooks(self):
            """Setup Flask before/after request hooks"""
            
            @self.app.before_request
            def before_request():
                # Store start time
                g.start_time = time.time()
                
                # Log request
                self.request_logger.log_request(
                    method=request.method,
                    path=request.path,
                    client_ip=request.remote_addr,
                    user_agent=request.headers.get("User-Agent"),
                    query_params=str(request.args) if request.args else None
                )
            
            @self.app.after_request
            def after_request(response):
                # Calculate duration
                if hasattr(g, 'start_time'):
                    duration_ms = (time.time() - g.start_time) * 1000
                else:
                    duration_ms = 0
                
                # Log response
                self.request_logger.log_response(
                    method=request.method,
                    path=request.path,
                    status_code=response.status_code,
                    duration_ms=duration_ms
                )
                
                return response
            
            @self.app.errorhandler(Exception)
            def handle_exception(e):
                # Calculate duration
                if hasattr(g, 'start_time'):
                    duration_ms = (time.time() - g.start_time) * 1000
                else:
                    duration_ms = 0
                
                # Log error
                self.request_logger.log_error(
                    method=request.method,
                    path=request.path,
                    error=e,
                    duration_ms=duration_ms
                )
                
                # Re-raise to let Flask handle it
                raise


# ── Decorator for Function Logging ────────────────────────────────────────────

def log_function_call(logger: Optional[logging.Logger] = None):
    """
    Decorator to log function calls with arguments and results.
    
    Usage:
        @log_function_call()
        def my_function(arg1, arg2):
            return result
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from .logging_config import get_logger
            log = logger or get_logger(func.__module__)
            
            # Log function call
            log.debug(
                f"Calling {func.__name__}",
                extra={
                    "extra_data": {
                        "function": func.__name__,
                        "args_count": len(args),
                        "kwargs_keys": list(kwargs.keys())
                    }
                }
            )
            
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                log.debug(
                    f"{func.__name__} completed in {duration:.3f}s",
                    extra={
                        "extra_data": {
                            "function": func.__name__,
                            "duration": duration,
                            "success": True
                        }
                    }
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                log.error(
                    f"{func.__name__} failed after {duration:.3f}s: {e}",
                    extra={
                        "extra_data": {
                            "function": func.__name__,
                            "duration": duration,
                            "error": str(e),
                            "error_type": type(e).__name__
                        }
                    }
                )
                raise
        
        return wrapper
    return decorator


# ── Exports ───────────────────────────────────────────────────────────────────

__all__ = [
    'FastAPILoggingMiddleware',
    'FlaskLoggingMiddleware',
    'log_function_call',
]

# Made with Bob
