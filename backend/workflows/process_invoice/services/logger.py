
import logging

# Create a custom logger
logger = logging.getLogger("my_app_logger")
logger.setLevel(logging.DEBUG)  # You can change this to INFO or WARNING as needed

# Avoid adding handlers multiple times if this module is imported repeatedly
if not logger.handlers:
    # Create handlers
    file_handler = logging.FileHandler("invoice_log.log")
    file_handler.setLevel(logging.DEBUG)

    # Create formatters and add them to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)