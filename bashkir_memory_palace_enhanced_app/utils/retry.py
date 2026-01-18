"""
Retry Logic with Exponential Backoff
=====================================
Provides robust retry mechanisms for network operations including
gTTS, Google Translate, and model downloads.
"""

import time
import logging
import functools
from typing import Callable, Optional, TypeVar, Any, Tuple, Type, Union
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_retries: int = 4
    base_delay: float = 2.0  # seconds
    max_delay: float = 60.0  # seconds
    exponential_base: float = 2.0
    retryable_exceptions: Tuple[Type[Exception], ...] = field(
        default_factory=lambda: (
            ConnectionError,
            TimeoutError,
            OSError,
        )
    )
    # Add specific exception messages to retry on
    retryable_messages: Tuple[str, ...] = field(
        default_factory=lambda: (
            'connection',
            'timeout',
            'network',
            'rate limit',
            '429',
            '503',
            '502',
            'temporary',
            'unavailable',
        )
    )

    def should_retry(self, exception: Exception) -> bool:
        """Determine if an exception should trigger a retry."""
        # Check if it's a known retryable exception type
        if isinstance(exception, self.retryable_exceptions):
            return True

        # Check exception message for retryable patterns
        error_msg = str(exception).lower()
        for pattern in self.retryable_messages:
            if pattern.lower() in error_msg:
                return True

        return False


def calculate_delay(attempt: int, config: RetryConfig) -> float:
    """Calculate delay for the given attempt using exponential backoff."""
    delay = config.base_delay * (config.exponential_base ** attempt)
    return min(delay, config.max_delay)


def retry_with_backoff(
    func: Optional[Callable[..., T]] = None,
    *,
    config: Optional[RetryConfig] = None,
    max_retries: Optional[int] = None,
    base_delay: Optional[float] = None,
    on_retry: Optional[Callable[[Exception, int, float], None]] = None,
) -> Union[Callable[..., T], Callable[[Callable[..., T]], Callable[..., T]]]:
    """
    Decorator that retries a function with exponential backoff.

    Can be used as:
        @retry_with_backoff
        def my_function(): ...

        @retry_with_backoff(max_retries=5, base_delay=1.0)
        def my_function(): ...

        @retry_with_backoff(config=RetryConfig(...))
        def my_function(): ...

    Args:
        func: The function to wrap (when used without parentheses)
        config: RetryConfig instance for full customization
        max_retries: Override for max retry attempts
        base_delay: Override for base delay in seconds
        on_retry: Callback function called on each retry with (exception, attempt, delay)

    Returns:
        Decorated function with retry logic
    """
    # Create effective config
    effective_config = config or RetryConfig()
    if max_retries is not None:
        effective_config.max_retries = max_retries
    if base_delay is not None:
        effective_config.base_delay = base_delay

    def decorator(f: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Optional[Exception] = None

            for attempt in range(effective_config.max_retries + 1):
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    # Check if we should retry
                    if attempt >= effective_config.max_retries:
                        logger.error(
                            f"Max retries ({effective_config.max_retries}) exceeded for {f.__name__}: {e}"
                        )
                        raise

                    if not effective_config.should_retry(e):
                        logger.error(f"Non-retryable error in {f.__name__}: {e}")
                        raise

                    # Calculate delay and wait
                    delay = calculate_delay(attempt, effective_config)
                    logger.warning(
                        f"Attempt {attempt + 1}/{effective_config.max_retries + 1} failed for "
                        f"{f.__name__}: {e}. Retrying in {delay:.1f}s..."
                    )

                    # Call retry callback if provided
                    if on_retry:
                        on_retry(e, attempt, delay)

                    time.sleep(delay)

            # Should not reach here, but just in case
            if last_exception:
                raise last_exception
            raise RuntimeError(f"Unexpected state in retry logic for {f.__name__}")

        return wrapper

    # Handle both @retry_with_backoff and @retry_with_backoff(...)
    if func is not None:
        return decorator(func)
    return decorator


class RetryableOperation:
    """
    Context manager for retryable operations.

    Usage:
        with RetryableOperation(max_retries=4) as op:
            for attempt in op.attempts():
                try:
                    result = do_network_call()
                    break
                except NetworkError as e:
                    op.handle_error(e)
    """

    def __init__(
        self,
        config: Optional[RetryConfig] = None,
        max_retries: Optional[int] = None,
        base_delay: Optional[float] = None,
    ):
        self.config = config or RetryConfig()
        if max_retries is not None:
            self.config.max_retries = max_retries
        if base_delay is not None:
            self.config.base_delay = base_delay

        self._current_attempt = 0
        self._last_exception: Optional[Exception] = None

    def __enter__(self) -> 'RetryableOperation':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def attempts(self):
        """Generator yielding attempt numbers."""
        for attempt in range(self.config.max_retries + 1):
            self._current_attempt = attempt
            yield attempt

    def handle_error(self, exception: Exception) -> None:
        """Handle an error, potentially sleeping before retry."""
        self._last_exception = exception

        if self._current_attempt >= self.config.max_retries:
            raise exception

        if not self.config.should_retry(exception):
            raise exception

        delay = calculate_delay(self._current_attempt, self.config)
        logger.warning(
            f"Attempt {self._current_attempt + 1}/{self.config.max_retries + 1} failed: "
            f"{exception}. Retrying in {delay:.1f}s..."
        )
        time.sleep(delay)


# Specialized retry decorators for common operations

def retry_gtts(func: Callable[..., T]) -> Callable[..., T]:
    """Retry decorator specifically configured for gTTS operations."""
    config = RetryConfig(
        max_retries=4,
        base_delay=2.0,
        retryable_exceptions=(
            ConnectionError,
            TimeoutError,
            OSError,
            Exception,  # gTTS can raise generic exceptions
        ),
        retryable_messages=(
            'connection',
            'timeout',
            'network',
            'rate limit',
            '429',
            '503',
            '502',
            'temporary',
            'unavailable',
            'gtts',
            'tts',
            'failed to connect',
        ),
    )
    return retry_with_backoff(func, config=config)


def retry_translation(func: Callable[..., T]) -> Callable[..., T]:
    """Retry decorator specifically configured for translation operations."""
    config = RetryConfig(
        max_retries=4,
        base_delay=2.0,
        retryable_exceptions=(
            ConnectionError,
            TimeoutError,
            OSError,
            Exception,
        ),
        retryable_messages=(
            'connection',
            'timeout',
            'network',
            'rate limit',
            '429',
            '503',
            '502',
            'temporary',
            'unavailable',
            'translate',
            'translation',
            'quota',
        ),
    )
    return retry_with_backoff(func, config=config)


def retry_model_download(func: Callable[..., T]) -> Callable[..., T]:
    """Retry decorator specifically configured for model downloads."""
    config = RetryConfig(
        max_retries=4,
        base_delay=4.0,  # Longer base delay for model downloads
        max_delay=120.0,
        retryable_exceptions=(
            ConnectionError,
            TimeoutError,
            OSError,
            Exception,
        ),
        retryable_messages=(
            'connection',
            'timeout',
            'network',
            'rate limit',
            '429',
            '503',
            '502',
            'temporary',
            'unavailable',
            'download',
            'huggingface',
            'model',
            'eof',
        ),
    )
    return retry_with_backoff(func, config=config)
