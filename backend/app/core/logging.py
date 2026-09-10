"""
Structured Hardware-Domain Logging Module for KrishiDrishti Edge.
Includes credential sanitization and hardware subsystem domain tags.
"""
import logging
import sys
import re
from datetime import datetime

# Regex pattern to redact sensitive keys from log output
SENSITIVE_PATTERN = re.compile(r"(password|secret|token|api[_-]?key|auth)=([^\s,]+)", re.IGNORECASE)

class DomainFormatter(logging.Formatter):
    """Custom formatter providing hardware/subsystem domain tags."""
    def format(self, record):
        domain = getattr(record, "domain", "SYSTEM")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        levelname = record.levelname
        msg = record.getMessage()
        # Redact sensitive parameters
        sanitized_msg = SENSITIVE_PATTERN.sub(r"\1=********", msg)
        return f"[{timestamp}] [{domain.upper():<8}] [{levelname:<5}] {sanitized_msg}"

def setup_logger(name: str = "krishidrishti", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(DomainFormatter())
        logger.addHandler(handler)
        
    return logger

logger = setup_logger()

def log_event(domain: str, level: str, message: str, **kwargs):
    """
    Convenience helper to emit domain-tagged logs.
    Subsystems: [AI], [CAMERA], [SOIL], [API], [DATABASE], [DEVICE], [SYSTEM]
    """
    extra = {"domain": domain, **kwargs}
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(message, extra=extra)
