import functools
import time

from .log import logger


def retry(
    max_retries=3,
    delay=1,
    exception=Exception,
):
    """retry decorator to retry a function multiple times if an exception is raised

    Args:
        max_retries (int, optional): The maximum number of retries. Defaults to 3.
        delay (int, optional): The delay in seconds between retries. Defaults to 1.
        exception (Exception, optional): The exception to catch and retry. Defaults to Exception.
    """

    def decorator_retry(func):
        @functools.wraps(func)
        def wrapper_retry(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except exception as e:
                    logger.warn(
                        f"Retry {retries+1}/{max_retries} due to {type(e).__name__}: {e}"
                    )
                    retries += 1
                    time.sleep(delay)
            logger.error(f"All {max_retries} retries failed")  # log an error message
            raise RuntimeError(
                f"All {max_retries} retries failed"
            )  # raise an exception if all retries fail

        return wrapper_retry

    return decorator_retry
