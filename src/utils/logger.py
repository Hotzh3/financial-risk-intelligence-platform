"""
Structured logger for the Financial Risk Intelligence Platform.
All modules should use this logger instead of print statements.
"""

import logging
import sys
from pathlib import Path


def get_logger(name: str, log_file: str | None = None) -> logging.Logger:
    """
    Create and configure a logger instance.

    Args:
        name: Logger name (use __name__ from calling module)
        log_file: Optional path to write logs to file

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger