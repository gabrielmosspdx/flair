"""Logging system for the game."""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class GameLogger:
    """Custom logger for game events."""

    _instance: Optional["GameLogger"] = None

    def __new__(cls) -> "GameLogger":
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the logger."""
        if not hasattr(self, "logger"):
            self.setup_logger()

    def setup_logger(
        self,
        name: str = "FlairGame",
        log_level: str = "INFO",
        log_to_file: bool = True,
        log_dir: str = "logs",
    ) -> None:
        """Setup the logging configuration.

        Args:
            name: Logger name
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_to_file: Whether to log to file
            log_dir: Directory for log files
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))

        # Remove existing handlers
        self.logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)

        # File handler
        if log_to_file:
            log_path = Path(log_dir)
            log_path.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = log_path / f"flair_{timestamp}.log"

            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_format = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
            )
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)

            self.logger.info(f"Logging to file: {log_file}")

    def debug(self, message: str, *args, **kwargs) -> None:
        """Log debug message.

        Args:
            message: Message to log
        """
        self.logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        """Log info message.

        Args:
            message: Message to log
        """
        self.logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        """Log warning message.

        Args:
            message: Message to log
        """
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        """Log error message.

        Args:
            message: Message to log
        """
        self.logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        """Log critical message.

        Args:
            message: Message to log
        """
        self.logger.critical(message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs) -> None:
        """Log exception with traceback.

        Args:
            message: Message to log
        """
        self.logger.exception(message, *args, **kwargs)

    def set_level(self, level: str) -> None:
        """Change logging level.

        Args:
            level: New logging level
        """
        self.logger.setLevel(getattr(logging, level.upper()))
        self.info(f"Logging level changed to: {level}")

    def performance(self, operation: str, time_ms: float) -> None:
        """Log performance metrics.

        Args:
            operation: Operation name
            time_ms: Time in milliseconds
        """
        if time_ms > 16.67:  # Longer than one frame at 60 FPS
            self.warning(f"Performance: {operation} took {time_ms:.2f}ms")
        else:
            self.debug(f"Performance: {operation} took {time_ms:.2f}ms")


# Global logger instance
game_logger = GameLogger()
