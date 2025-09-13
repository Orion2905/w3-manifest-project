"""
Enhanced logging configuration for IMAP monitoring and debugging.
Provides structured logging with user context and detailed monitoring.
"""
import logging
import os
from datetime import datetime
from functools import wraps
from flask import request
from flask_jwt_extended import get_current_user

def setup_imap_logger(logger_name='imap_monitor', log_level=logging.INFO):
    """
    Setup enhanced logger for IMAP monitoring with file and console output.
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = logging.Formatter(
        '%(asctime)s - IMAP - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Console handler (always enabled)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if logs directory exists or can be created)
    try:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f'imap_monitor_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
        
        print(f"📁 IMAP logging to file: {log_file}")
        
    except Exception as e:
        print(f"⚠️ Could not setup file logging: {e}")
    
    return logger

def get_user_context():
    """Get current user context for logging."""
    try:
        current_user = get_current_user()
        if current_user:
            return {
                'user_id': current_user.id,
                'username': current_user.username,
                'email': getattr(current_user, 'email', 'Unknown')
            }
    except Exception:
        pass
    return {'user_id': None, 'username': 'Anonymous', 'email': 'Unknown'}

def get_request_context():
    """Get current request context for logging."""
    try:
        return {
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'Unknown'),
            'method': request.method,
            'endpoint': request.endpoint
        }
    except Exception:
        return {'ip': 'Unknown', 'user_agent': 'Unknown', 'method': 'Unknown', 'endpoint': 'Unknown'}

def log_imap_activity(logger, level, action, details=None, config_name=None, error=None):
    """
    Log IMAP activity with structured context.
    
    Args:
        logger: Logger instance
        level: Log level (INFO, WARNING, ERROR, etc.)
        action: Action being performed (e.g., 'connection_test', 'email_check')
        details: Additional details dictionary
        config_name: Name of the email configuration
        error: Error object if applicable
    """
    user_ctx = get_user_context()
    req_ctx = get_request_context()
    
    # Build log message
    icon = {
        'INFO': '📧',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'DEBUG': '🔍',
        'SUCCESS': '✅'
    }.get(level.upper(), '📧')
    
    message_parts = [
        f"{icon} IMAP {action.upper()}",
        f"User: {user_ctx['username']} (ID: {user_ctx['user_id']})",
        f"IP: {req_ctx['ip']}"
    ]
    
    if config_name:
        message_parts.append(f"Config: '{config_name}'")
    
    if details:
        for key, value in details.items():
            message_parts.append(f"{key}: {value}")
    
    if error:
        message_parts.append(f"Error: {str(error)}")
    
    message = " | ".join(message_parts)
    
    # Log with appropriate level
    log_method = getattr(logger, level.lower(), logger.info)
    log_method(message)

def imap_log_decorator(action, config_param=None):
    """
    Decorator to automatically log IMAP operations.
    
    Args:
        action: Description of the action being performed
        config_param: Parameter name that contains the config ID or name
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = setup_imap_logger()
            
            # Extract config info if available
            config_info = None
            if config_param and config_param in kwargs:
                config_info = kwargs[config_param]
            
            try:
                log_imap_activity(logger, 'INFO', f'{action}_start', config_name=config_info)
                result = func(*args, **kwargs)
                log_imap_activity(logger, 'SUCCESS', f'{action}_complete', config_name=config_info)
                return result
            except Exception as e:
                log_imap_activity(logger, 'ERROR', f'{action}_failed', config_name=config_info, error=e)
                raise
        return wrapper
    return decorator

# Pre-configured logger instance
imap_logger = setup_imap_logger()

# Convenience logging functions
def log_imap_info(action, **kwargs):
    """Log IMAP info message."""
    log_imap_activity(imap_logger, 'INFO', action, **kwargs)

def log_imap_warning(action, **kwargs):
    """Log IMAP warning message."""
    log_imap_activity(imap_logger, 'WARNING', action, **kwargs)

def log_imap_error(action, **kwargs):
    """Log IMAP error message."""
    log_imap_activity(imap_logger, 'ERROR', action, **kwargs)

def log_imap_success(action, **kwargs):
    """Log IMAP success message."""
    log_imap_activity(imap_logger, 'SUCCESS', action, **kwargs)

def log_imap_debug(action, **kwargs):
    """Log IMAP debug message."""
    log_imap_activity(imap_logger, 'DEBUG', action, **kwargs)
