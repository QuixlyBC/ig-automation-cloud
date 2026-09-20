"""
Background worker that processes the queue in a loop.
Runs in a separate thread, checking for pending items every N seconds.
"""

import threading
import time
import logging

import config
import ig_tasks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def worker_loop():
    """Infinite loop: check queue every WORKER_INTERVAL seconds, post if found."""
    logger.info("Worker started")
    while True:
        try:
            result = ig_tasks.process_queue()
            if result:
                if result["ok"]:
                    logger.info(f"Posted reel {result['id']}: {result['url']}")
                else:
                    logger.error(f"Failed to post reel {result['id']}: {result['error']}")
        except Exception as e:
            logger.error(f"Worker error: {e}")
        
        time.sleep(config.WORKER_INTERVAL)


def start_worker():
    """Start the background worker in a daemon thread."""
    thread = threading.Thread(target=worker_loop, daemon=True)
    thread.start()
    logger.info("Worker thread started")
    return thread
