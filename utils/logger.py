import logging
import os
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("L1CopilotLogger")
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    file_handler = logging.FileHandler(
        os.path.join(LOG_DIR, f"l1_copilot_{datetime.now().strftime('%Y%m%d')}.log")
    )
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def log_investigation(order_id, agent_name, message):
    logger.info(f"[{order_id}] [{agent_name}] {message}")


def log_resolution(order_id, action, result):
    logger.info(f"[{order_id}] [Resolution] Action: {action} | Result: {result}")


def log_error(order_id, agent_name, error):
    logger.error(f"[{order_id}] [{agent_name}] Error: {error}")
