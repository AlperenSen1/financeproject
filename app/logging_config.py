import logging
from logging.handlers import RotatingFileHandler
import os

# Create logs/ folder if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Create logger
logger = logging.getLogger("finance_logger")
logger.setLevel(logging.INFO)

# Rotating file handler: 1MB max, 5 backups
file_handler = RotatingFileHandler("logs/app.log", maxBytes=1_000_000, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(file_handler)
