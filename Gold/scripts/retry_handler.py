# scripts/retry_handler.py
import time
import functools
import random
from typing import Type
import logging

logger = logging.getLogger("RetryHandler")

def with_retry(
    exceptions: tuple[Type[Exception], ...] = (Exception,), 
    max_retries: int = 3, 
    initial_delay: float = 1.0, 
    backoff_factor: float = 2.0,
    jitter: bool = True
):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Function {func.__name__} failed after {max_retries} attempts. Last error: {e}")
                        raise
                    
                    wait_time = delay
                    if jitter:
                        wait_time = delay * random.uniform(0.5, 1.5)
                        
                    logger.warning(f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}. Retrying in {wait_time:.2f}s. Error: {e}")
                    time.sleep(wait_time)
                    delay *= backoff_factor
        return wrapper
    return decorator
