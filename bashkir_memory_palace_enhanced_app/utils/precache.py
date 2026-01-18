"""
Precaching System for Audio and Models
=======================================
Provides background precaching for audio files and ML models
to improve application responsiveness.
"""

import os
import json
import logging
import threading
import time
from pathlib import Path
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue

logger = logging.getLogger(__name__)


@dataclass
class PrecacheConfig:
    """Configuration for precaching behavior."""
    max_workers: int = 4
    batch_size: int = 10
    priority_count: int = 50  # Number of high-priority items to cache first
    cache_dir: str = "cache"
    enabled: bool = True


@dataclass
class PrecacheTask:
    """A single precaching task."""
    key: str
    data: Any
    priority: int = 0  # Lower = higher priority
    callback: Optional[Callable[[str, bool], None]] = None


class PrecacheManager:
    """
    Manages precaching of resources (audio, models) in the background.

    Usage:
        manager = PrecacheManager(config=PrecacheConfig())
        manager.start()

        # Add items to precache
        manager.add_audio_task("бал", language="ru")
        manager.add_model_task("whisper", model_name="base")

        # Check status
        print(manager.get_status())

        # Stop when done
        manager.stop()
    """

    def __init__(self, config: Optional[PrecacheConfig] = None):
        self.config = config or PrecacheConfig()
        self._task_queue: Queue = Queue()
        self._executor: Optional[ThreadPoolExecutor] = None
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        self._stats = {
            'queued': 0,
            'completed': 0,
            'failed': 0,
            'in_progress': 0,
        }
        self._lock = threading.Lock()

        # Audio generation function (to be set by the application)
        self._audio_generator: Optional[Callable[[str, str], Optional[str]]] = None
        self._model_loader: Optional[Callable[[str, str], Any]] = None

    def set_audio_generator(self, func: Callable[[str, str], Optional[str]]) -> None:
        """Set the function used to generate audio."""
        self._audio_generator = func

    def set_model_loader(self, func: Callable[[str, str], Any]) -> None:
        """Set the function used to load models."""
        self._model_loader = func

    def start(self) -> None:
        """Start the precache manager."""
        if self._running:
            logger.warning("PrecacheManager is already running")
            return

        self._running = True
        self._executor = ThreadPoolExecutor(max_workers=self.config.max_workers)
        self._worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self._worker_thread.start()
        logger.info(f"PrecacheManager started with {self.config.max_workers} workers")

    def stop(self, wait: bool = True) -> None:
        """Stop the precache manager."""
        self._running = False
        if self._executor:
            self._executor.shutdown(wait=wait)
            self._executor = None
        if self._worker_thread and wait:
            self._worker_thread.join(timeout=5.0)
        logger.info("PrecacheManager stopped")

    def _process_queue(self) -> None:
        """Process tasks from the queue."""
        while self._running:
            try:
                # Get batch of tasks
                tasks = []
                while len(tasks) < self.config.batch_size and not self._task_queue.empty():
                    try:
                        task = self._task_queue.get_nowait()
                        tasks.append(task)
                    except:
                        break

                if not tasks:
                    time.sleep(0.5)
                    continue

                # Sort by priority
                tasks.sort(key=lambda t: t.priority)

                # Process tasks
                futures = []
                for task in tasks:
                    if not self._running:
                        break

                    with self._lock:
                        self._stats['in_progress'] += 1

                    future = self._executor.submit(self._execute_task, task)
                    futures.append((future, task))

                # Wait for completion
                for future, task in futures:
                    try:
                        success = future.result(timeout=60)
                        with self._lock:
                            self._stats['in_progress'] -= 1
                            if success:
                                self._stats['completed'] += 1
                            else:
                                self._stats['failed'] += 1

                        if task.callback:
                            task.callback(task.key, success)
                    except Exception as e:
                        with self._lock:
                            self._stats['in_progress'] -= 1
                            self._stats['failed'] += 1
                        logger.error(f"Precache task failed for {task.key}: {e}")

            except Exception as e:
                logger.error(f"Error in precache queue processing: {e}")
                time.sleep(1)

    def _execute_task(self, task: PrecacheTask) -> bool:
        """Execute a single precache task."""
        try:
            task_type = task.data.get('type', 'audio')

            if task_type == 'audio':
                if not self._audio_generator:
                    logger.warning("No audio generator configured")
                    return False

                text = task.data.get('text', task.key)
                language = task.data.get('language', 'ru')
                result = self._audio_generator(text, language)
                return result is not None

            elif task_type == 'model':
                if not self._model_loader:
                    logger.warning("No model loader configured")
                    return False

                model_type = task.data.get('model_type', 'whisper')
                model_name = task.data.get('model_name', 'base')
                result = self._model_loader(model_type, model_name)
                return result is not None

            else:
                logger.warning(f"Unknown task type: {task_type}")
                return False

        except Exception as e:
            logger.error(f"Error executing precache task {task.key}: {e}")
            return False

    def add_audio_task(
        self,
        text: str,
        language: str = 'ru',
        priority: int = 5,
        callback: Optional[Callable[[str, bool], None]] = None
    ) -> None:
        """Add an audio precaching task."""
        if not self.config.enabled:
            return

        task = PrecacheTask(
            key=f"audio:{text}:{language}",
            data={'type': 'audio', 'text': text, 'language': language},
            priority=priority,
            callback=callback,
        )
        self._task_queue.put(task)
        with self._lock:
            self._stats['queued'] += 1

    def add_model_task(
        self,
        model_type: str,
        model_name: str = 'base',
        priority: int = 0,  # Models are high priority
        callback: Optional[Callable[[str, bool], None]] = None
    ) -> None:
        """Add a model precaching task."""
        if not self.config.enabled:
            return

        task = PrecacheTask(
            key=f"model:{model_type}:{model_name}",
            data={'type': 'model', 'model_type': model_type, 'model_name': model_name},
            priority=priority,
            callback=callback,
        )
        self._task_queue.put(task)
        with self._lock:
            self._stats['queued'] += 1

    def add_batch_audio_tasks(
        self,
        texts: List[str],
        language: str = 'ru',
        base_priority: int = 5
    ) -> None:
        """Add multiple audio precaching tasks."""
        for i, text in enumerate(texts):
            # Increase priority (lower number) for earlier items
            priority = base_priority + (i // 10)
            self.add_audio_task(text, language, priority)

    def get_status(self) -> Dict[str, int]:
        """Get current precaching status."""
        with self._lock:
            return {
                'running': self._running,
                'queue_size': self._task_queue.qsize(),
                **self._stats
            }

    def clear_queue(self) -> None:
        """Clear all pending tasks."""
        while not self._task_queue.empty():
            try:
                self._task_queue.get_nowait()
            except:
                break
        with self._lock:
            self._stats['queued'] = 0


def precache_audio(
    words: List[Dict],
    audio_generator: Callable[[str, str, bool], Optional[str]],
    cache_dir: str = "audio_cache",
    max_workers: int = 4,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> Dict[str, str]:
    """
    Precache audio for a list of words.

    Args:
        words: List of word dictionaries with 'bashkir' key
        audio_generator: Function(text, audio_type, slow) -> path
        cache_dir: Directory to store cached audio
        max_workers: Number of parallel workers
        progress_callback: Called with (completed, total) for progress updates

    Returns:
        Dictionary mapping text to audio file paths
    """
    from .retry import retry_with_backoff, RetryConfig

    results = {}
    total = len(words)
    completed = 0

    # Create retry-wrapped generator
    retry_config = RetryConfig(max_retries=4, base_delay=2.0)

    def generate_with_retry(text: str) -> Optional[str]:
        for attempt in range(retry_config.max_retries + 1):
            try:
                return audio_generator(text, "words", True)
            except Exception as e:
                if attempt >= retry_config.max_retries:
                    logger.error(f"Failed to generate audio for '{text}' after {retry_config.max_retries + 1} attempts: {e}")
                    return None
                delay = retry_config.base_delay * (2 ** attempt)
                logger.warning(f"Audio generation failed for '{text}', retrying in {delay}s: {e}")
                time.sleep(delay)
        return None

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_word = {}
        for word_data in words:
            text = word_data.get('bashkir', '')
            if text:
                future = executor.submit(generate_with_retry, text)
                future_to_word[future] = text

        # Collect results
        for future in as_completed(future_to_word):
            text = future_to_word[future]
            try:
                result = future.result()
                if result:
                    results[text] = result
            except Exception as e:
                logger.error(f"Unexpected error precaching '{text}': {e}")

            completed += 1
            if progress_callback:
                progress_callback(completed, total)

    logger.info(f"Precached {len(results)}/{total} audio files")
    return results


def precache_models(
    model_configs: List[Dict[str, str]],
    progress_callback: Optional[Callable[[str, bool], None]] = None,
) -> Dict[str, Any]:
    """
    Precache ML models.

    Args:
        model_configs: List of dicts with 'type' and 'name' keys
            e.g., [{'type': 'whisper', 'name': 'base'}, {'type': 'bert', 'name': 'bert-base-multilingual-cased'}]
        progress_callback: Called with (model_name, success) for each model

    Returns:
        Dictionary mapping model keys to loaded models
    """
    from .retry import retry_model_download

    results = {}

    for config in model_configs:
        model_type = config.get('type', '')
        model_name = config.get('name', '')
        key = f"{model_type}:{model_name}"

        try:
            if model_type == 'whisper':
                result = _load_whisper_model(model_name)
            elif model_type == 'bert' or model_type == 'tokenizer':
                result = _load_tokenizer(model_name)
            else:
                logger.warning(f"Unknown model type: {model_type}")
                result = None

            if result is not None:
                results[key] = result
                if progress_callback:
                    progress_callback(key, True)
            else:
                if progress_callback:
                    progress_callback(key, False)

        except Exception as e:
            logger.error(f"Failed to precache model {key}: {e}")
            if progress_callback:
                progress_callback(key, False)

    logger.info(f"Precached {len(results)}/{len(model_configs)} models")
    return results


def _load_whisper_model(model_name: str):
    """Load a Whisper model with retry logic."""
    from .retry import RetryConfig

    try:
        import whisper
    except ImportError:
        logger.warning("Whisper not available")
        return None

    config = RetryConfig(max_retries=4, base_delay=4.0)

    for attempt in range(config.max_retries + 1):
        try:
            logger.info(f"Loading Whisper model '{model_name}'...")
            model = whisper.load_model(model_name)
            logger.info(f"Whisper model '{model_name}' loaded successfully")
            return model
        except Exception as e:
            if attempt >= config.max_retries:
                logger.error(f"Failed to load Whisper model after {config.max_retries + 1} attempts: {e}")
                return None
            delay = config.base_delay * (2 ** attempt)
            logger.warning(f"Whisper model load failed, retrying in {delay}s: {e}")
            time.sleep(delay)

    return None


def _load_tokenizer(model_name: str):
    """Load a tokenizer with retry logic."""
    from .retry import RetryConfig

    try:
        from transformers import AutoTokenizer
    except ImportError:
        logger.warning("Transformers not available")
        return None

    config = RetryConfig(max_retries=4, base_delay=4.0)

    for attempt in range(config.max_retries + 1):
        try:
            logger.info(f"Loading tokenizer '{model_name}'...")
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            logger.info(f"Tokenizer '{model_name}' loaded successfully")
            return tokenizer
        except Exception as e:
            if attempt >= config.max_retries:
                logger.error(f"Failed to load tokenizer after {config.max_retries + 1} attempts: {e}")
                return None
            delay = config.base_delay * (2 ** attempt)
            logger.warning(f"Tokenizer load failed, retrying in {delay}s: {e}")
            time.sleep(delay)

    return None


def load_words_for_precaching(words_file: str, limit: Optional[int] = None) -> List[Dict]:
    """
    Load words from JSON file for precaching.

    Args:
        words_file: Path to words.json
        limit: Optional limit on number of words to load

    Returns:
        List of word dictionaries sorted by frequency
    """
    try:
        with open(words_file, 'r', encoding='utf-8') as f:
            words = json.load(f)

        # Sort by frequency rank if available
        words.sort(key=lambda w: w.get('frequency_rank', 999))

        if limit:
            words = words[:limit]

        logger.info(f"Loaded {len(words)} words for precaching from {words_file}")
        return words

    except Exception as e:
        logger.error(f"Failed to load words for precaching: {e}")
        return []
