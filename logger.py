import logging
from logging.handlers import TimedRotatingFileHandler
import os

# Directory for log files
LOG_DIR = "LOGS"
os.makedirs(LOG_DIR, exist_ok=True)

# Singleton logger
_logger = None

def get_logger():
    global _logger
    if _logger is None:
        _logger = logging.getLogger("BotLogger")
        _logger.setLevel(logging.INFO)

        # File handler with daily rotation
        handler = TimedRotatingFileHandler(
            filename=os.path.join(LOG_DIR, "bot.log"),
            when="midnight",
            interval=1,
            backupCount=30,
            encoding="utf-8"
        )
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        _logger.addHandler(handler)

        # Avoid duplicate logs by preventing propagation
        _logger.propagate = False

    return _logger
