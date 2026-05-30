import functools
import time

from log import warn


def retry(max_attempts=3, backoff_factor=2, initial_delay=1, exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts:
                        warn(
                            f"{func.__name__} failed after {max_attempts} attempts: {e}"
                        )
                        raise

                    warn(
                        f"{func.__name__} failed (attempt {attempt}/{max_attempts}): {e}. Retrying in {delay}s..."
                    )
                    time.sleep(delay)
                    delay *= backoff_factor

            raise last_exception

        return wrapper

    return decorator
