"""
SpecSentinel Centralized Logging Configuration

Provides a unified logging setup with:
- Multiple output formats (console, file, JSON)
- Log rotation
- Structured logging
- Performance tracking
- Request/response logging
- Environment-based configuration
"""

import logging
import logging.handlers
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import traceback


# ── Configuration ─────────────────────────────────────────────────────────────

LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Environment-based log level
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Enable JSON logging for production
JSON_LOGGING = os.getenv("JSON_LOGGING", "false").lower() == "true"

# Enable file logging
FILE_LOGGING = os.getenv("FILE_LOGGING", "true").lower() == "true"

# Log rotation settings
MAX_BYTES = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT = 5

# Log format - Enhanced for better readability
CONSOLE_FORMAT = "%(asctime)s [%(levelname)-8s] [%(name)-25s] %(message)s"
FILE_FORMAT = "%(asctime)s [%(levelname)-8s] [%(name)-25s] [%(filename)s:%(lineno)d] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# ── Custom Formatters ─────────────────────────────────────────────────────────

class ColoredFormatter(logging.Formatter):
    """Colored console output formatter"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


class JSONFormatter(logging.Formatter):
    """JSON structured logging formatter"""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info and record.exc_info[0]:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields
        if hasattr(record, 'extra_data'):
            log_data.update(getattr(record, 'extra_data'))
        
        return json.dumps(log_data)


# ── Logger Setup ──────────────────────────────────────────────────────────────

def setup_logging(
    name: str = "specsentinel",
    level: Optional[str] = None,
    enable_console: bool = True,
    enable_file: Optional[bool] = None,
    enable_json: Optional[bool] = None,
) -> logging.Logger:
    """
    Configure and return a logger with all handlers.
    
    Args:
        name: Logger name (typically module name)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_console: Enable console output
        enable_file: Enable file output (defaults to FILE_LOGGING env)
        enable_json: Enable JSON formatting (defaults to JSON_LOGGING env)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Set level
    log_level = getattr(logging, (level or LOG_LEVEL).upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(log_level)
        
        if enable_json if enable_json is not None else JSON_LOGGING:
            console_handler.setFormatter(JSONFormatter())
        else:
            console_handler.setFormatter(ColoredFormatter(CONSOLE_FORMAT, DATE_FORMAT))
        
        logger.addHandler(console_handler)
    
    # File handler with rotation
    if enable_file if enable_file is not None else FILE_LOGGING:
        log_file = LOG_DIR / f"{name}.log"
        try:
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=MAX_BYTES,
                backupCount=BACKUP_COUNT,
                encoding='utf-8',
                delay=True  # Delay file opening until first write
            )
            file_handler.setLevel(log_level)
            
            if enable_json if enable_json is not None else JSON_LOGGING:
                file_handler.setFormatter(JSONFormatter())
            else:
                file_handler.setFormatter(logging.Formatter(FILE_FORMAT, DATE_FORMAT))
            
            logger.addHandler(file_handler)
        except Exception as e:
            # If file handler fails, continue with console logging only
            print(f"Warning: Could not create file handler for {log_file}: {e}", file=sys.stderr)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger with standard configuration.
    
    Args:
        name: Logger name (use __name__ from calling module)
    
    Returns:
        Configured logger instance
    """
    return setup_logging(name)


# ── Structured Logging Helpers ────────────────────────────────────────────────

class StructuredLogger:
    """
    Wrapper for structured logging with extra context.
    
    Usage:
        logger = StructuredLogger("mymodule")
        logger.info("User action", user_id=123, action="login")
    """
    
    def __init__(self, name: str):
        self.logger = get_logger(name)
    
    def _log(self, level: int, message: str, **kwargs):
        """Log with extra structured data"""
        extra = {"extra_data": kwargs} if kwargs else {}
        self.logger.log(level, message, extra=extra)
    
    def debug(self, message: str, **kwargs):
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        self._log(logging.CRITICAL, message, **kwargs)
    
    def exception(self, message: str, **kwargs):
        """Log exception with traceback"""
        self.logger.exception(message, extra={"extra_data": kwargs} if kwargs else {})


# ── Performance Logging ───────────────────────────────────────────────────────

import time
from functools import wraps
from contextlib import contextmanager


def log_performance(logger: Optional[logging.Logger] = None):
    """
    Decorator to log function execution time.
    
    Usage:
        @log_performance()
        def my_function():
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            log = logger or get_logger(func.__module__)
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                log.info(
                    f"[PERF] {func.__name__} completed in {execution_time:.3f}s"
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                log.error(
                    f"[PERF] {func.__name__} failed after {execution_time:.3f}s: {e}"
                )
                raise
        
        return wrapper
    return decorator


@contextmanager
def log_execution_time(operation: str, logger: Optional[logging.Logger] = None):
    """
    Context manager to log execution time of a code block.
    
    Usage:
        with log_execution_time("database query"):
            # your code here
            pass
    """
    log = logger or get_logger(__name__)
    start_time = time.time()
    
    try:
        yield
    finally:
        execution_time = time.time() - start_time
        log.info(f"[PERF] {operation} took {execution_time:.3f}s")


# ── Request/Response Logging ──────────────────────────────────────────────────

class RequestLogger:
    """Logger for HTTP requests and responses"""
    
    def __init__(self, name: str = "specsentinel.requests"):
        self.logger = StructuredLogger(name)
    
    def log_request(
        self,
        method: str,
        path: str,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        **extra
    ):
        """Log incoming HTTP request"""
        self.logger.info(
            f"Request: {method} {path}",
            method=method,
            path=path,
            client_ip=client_ip,
            user_agent=user_agent,
            **extra
        )
    
    def log_response(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        **extra
    ):
        """Log HTTP response"""
        level = "info" if status_code < 400 else "warning" if status_code < 500 else "error"
        
        getattr(self.logger, level)(
            f"Response: {method} {path} -> {status_code} ({duration_ms:.0f}ms)",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms,
            **extra
        )
    
    def log_error(
        self,
        method: str,
        path: str,
        error: Exception,
        **extra
    ):
        """Log request error"""
        self.logger.exception(
            f"Request error: {method} {path}",
            method=method,
            path=path,
            error_type=type(error).__name__,
            error_message=str(error),
            **extra
        )


# ── Pipeline Stage Logging ────────────────────────────────────────────────────

class PipelineLogger:
    """Logger for analysis pipeline stages"""
    
    def __init__(self, name: str = "specsentinel.pipeline"):
        self.logger = StructuredLogger(name)
        self.stage_times: Dict[str, float] = {}
    
    def start_stage(self, stage: str, **context):
        """Log pipeline stage start"""
        self.stage_times[stage] = time.time()
        self.logger.info(f"[{stage}] Starting...", stage=stage, **context)
    
    def end_stage(self, stage: str, **results):
        """Log pipeline stage completion"""
        if stage in self.stage_times:
            duration = time.time() - self.stage_times[stage]
            self.logger.info(
                f"[{stage}] Completed in {duration:.3f}s",
                stage=stage,
                duration=duration,
                **results
            )
            del self.stage_times[stage]
    
    def stage_error(self, stage: str, error: Exception):
        """Log pipeline stage error"""
        if stage in self.stage_times:
            duration = time.time() - self.stage_times[stage]
            self.logger.error(
                f"[{stage}] Failed after {duration:.3f}s",
                stage=stage,
                duration=duration,
                error_type=type(error).__name__,
                error_message=str(error)
            )
            del self.stage_times[stage]


# ── Agent Logging ─────────────────────────────────────────────────────────────

class AgentLogger:
    """Logger for AI agent operations"""
    
    def __init__(self, agent_name: str):
        self.logger = StructuredLogger(f"specsentinel.agent.{agent_name}")
        self.agent_name = agent_name
    
    def log_analysis_start(self, spec_name: str, **context):
        """Log agent analysis start"""
        self.logger.info(
            f"[{self.agent_name}] Starting analysis",
            agent=self.agent_name,
            spec=spec_name,
            **context
        )
    
    def log_analysis_complete(self, findings_count: int, duration: float, **results):
        """Log agent analysis completion"""
        self.logger.info(
            f"[{self.agent_name}] Analysis complete: {findings_count} findings in {duration:.2f}s",
            agent=self.agent_name,
            findings_count=findings_count,
            duration=duration,
            **results
        )
    
    def log_llm_call(self, model: str, tokens: Optional[int] = None, cost: Optional[float] = None):
        """Log LLM API call"""
        self.logger.info(
            f"[{self.agent_name}] LLM call",
            agent=self.agent_name,
            model=model,
            tokens=tokens,
            cost=cost
        )
    
    def log_error(self, error: Exception, **context):
        """Log agent error"""
        self.logger.exception(
            f"[{self.agent_name}] Error",
            agent=self.agent_name,
            error_type=type(error).__name__,
            **context
        )


# ── Initialization ────────────────────────────────────────────────────────────

# Create default logger
default_logger = setup_logging()

# Log startup
default_logger.info(f"SpecSentinel logging initialized (level={LOG_LEVEL}, json={JSON_LOGGING})")


# ── Exports ───────────────────────────────────────────────────────────────────

__all__ = [
    'setup_logging',
    'get_logger',
    'StructuredLogger',
    'RequestLogger',
    'PipelineLogger',
    'AgentLogger',
    'log_performance',
    'log_execution_time',
]

# Made with Bob
