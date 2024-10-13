import logging
import os

# Setup logger configuration
logs_dir = 'logs'
os.makedirs(logs_dir, exist_ok=True)  # Create logs directory if it doesn't exist

logger = logging.getLogger('file_extractor')
filename=os.path.join(logs_dir, 'app.log')
handler = logging.FileHandler(filename)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Helper function to log messages
def log_message(message, level="info"):
    if level == "info":
        logger.info(message)
    elif level == "error":
        logger.error(message)
    elif level == "warning":
        logger.warning(message)
