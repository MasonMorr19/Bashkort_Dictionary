"""
Audio Service: Text-to-Speech for Bashkir
==========================================
Provides audio generation for Bashkir vocabulary and sentences.
Uses gTTS with Russian voice as approximation (until native Bashkir TTS available).
Includes retry logic with exponential backoff for network resilience.
"""

import hashlib
import os
import sys
import time
from pathlib import Path
from typing import Optional, Dict, List, Callable
import logging

# Add parent directory to path to import shared utilities
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.retry import retry_with_backoff, RetryConfig, retry_gtts

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import gTTS
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    logger.warning("gTTS not available. Audio generation will be disabled.")


class AudioService:
    """Service for generating and managing audio files."""
    
    def __init__(self, cache_dir: str = "audio_cache"):
        """
        Initialize the audio service.
        
        Args:
            cache_dir: Directory to store generated audio files
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Subdirectories for different audio types
        (self.cache_dir / "words").mkdir(exist_ok=True)
        (self.cache_dir / "sentences").mkdir(exist_ok=True)
        (self.cache_dir / "phrases").mkdir(exist_ok=True)
    
    def _get_cache_key(self, text: str) -> str:
        """Generate a cache key for the text."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _get_cache_path(self, text: str, audio_type: str = "words") -> Path:
        """Get the cache file path for a text."""
        key = self._get_cache_key(text)
        return self.cache_dir / audio_type / f"{key}.mp3"
    
    def generate_audio(self, text: str, audio_type: str = "words",
                       slow: bool = False, force: bool = False) -> Optional[str]:
        """
        Generate audio for text with retry logic.

        Args:
            text: The text to convert to speech
            audio_type: Type of audio (words, sentences, phrases)
            slow: Whether to generate slow speech
            force: Force regeneration even if cached

        Returns:
            Path to the audio file, or None if generation failed
        """
        if not GTTS_AVAILABLE:
            logger.warning("gTTS not available")
            return None

        cache_path = self._get_cache_path(text, audio_type)

        # Return cached version if available
        if cache_path.exists() and not force:
            return str(cache_path)

        # Use retry logic for network call
        return self._generate_with_retry(text, cache_path, slow)

    def _generate_with_retry(self, text: str, cache_path: Path, slow: bool) -> Optional[str]:
        """
        Internal method to generate audio with retry logic.

        Uses exponential backoff: 2s, 4s, 8s, 16s delays between retries.
        """
        config = RetryConfig(
            max_retries=4,
            base_delay=2.0,
            exponential_base=2.0,
        )

        for attempt in range(config.max_retries + 1):
            try:
                # Use Russian as approximation for Bashkir
                # Bashkir shares many phonological features with Russian
                tts = gTTS(text=text, lang='ru', slow=slow)
                tts.save(str(cache_path))
                logger.info(f"Generated audio for: {text[:30]}...")
                return str(cache_path)

            except Exception as e:
                if attempt >= config.max_retries:
                    logger.error(f"Failed to generate audio after {config.max_retries + 1} attempts: {e}")
                    return None

                delay = config.base_delay * (config.exponential_base ** attempt)
                logger.warning(
                    f"Audio generation attempt {attempt + 1}/{config.max_retries + 1} failed for "
                    f"'{text[:20]}...': {e}. Retrying in {delay:.1f}s..."
                )
                time.sleep(delay)

        return None
    
    def generate_word_audio(self, word: str, slow: bool = True) -> Optional[str]:
        """Generate audio for a single word (slower for learning)."""
        return self.generate_audio(word, audio_type="words", slow=slow)
    
    def generate_sentence_audio(self, sentence: str, slow: bool = False) -> Optional[str]:
        """Generate audio for a sentence."""
        return self.generate_audio(sentence, audio_type="sentences", slow=slow)
    
    def generate_phrase_audio(self, phrase: str) -> Optional[str]:
        """Generate audio for a phrase."""
        return self.generate_audio(phrase, audio_type="phrases", slow=False)
    
    def batch_generate(self, texts: list, audio_type: str = "words") -> Dict[str, Optional[str]]:
        """
        Generate audio for multiple texts.

        Args:
            texts: List of texts to convert
            audio_type: Type of audio

        Returns:
            Dict mapping text to audio file path
        """
        results = {}
        for text in texts:
            results[text] = self.generate_audio(text, audio_type)
        return results

    def precache_vocabulary(
        self,
        words: List[Dict],
        audio_type: str = "words",
        slow: bool = True,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        priority_limit: Optional[int] = None,
    ) -> Dict[str, Optional[str]]:
        """
        Precache audio for a vocabulary list.

        Args:
            words: List of word dictionaries with 'bashkir' key
            audio_type: Type of audio to generate
            slow: Whether to use slow speech
            progress_callback: Optional callback(completed, total) for progress
            priority_limit: Optional limit to cache only top N words by frequency

        Returns:
            Dict mapping text to audio file path
        """
        # Sort by frequency rank if available
        sorted_words = sorted(words, key=lambda w: w.get('frequency_rank', 999))

        if priority_limit:
            sorted_words = sorted_words[:priority_limit]

        results = {}
        total = len(sorted_words)

        logger.info(f"Starting precache of {total} vocabulary items...")

        for i, word_data in enumerate(sorted_words):
            text = word_data.get('bashkir', '')
            if not text:
                continue

            # Check if already cached
            cache_path = self._get_cache_path(text, audio_type)
            if cache_path.exists():
                results[text] = str(cache_path)
            else:
                result = self.generate_audio(text, audio_type, slow=slow)
                if result:
                    results[text] = result

            if progress_callback:
                progress_callback(i + 1, total)

        cached_count = len([r for r in results.values() if r])
        logger.info(f"Precached {cached_count}/{total} vocabulary items")

        return results

    def get_uncached_words(self, words: List[Dict], audio_type: str = "words") -> List[Dict]:
        """
        Get list of words that don't have cached audio.

        Args:
            words: List of word dictionaries with 'bashkir' key
            audio_type: Type of audio to check

        Returns:
            List of words that need audio generation
        """
        uncached = []
        for word_data in words:
            text = word_data.get('bashkir', '')
            if text:
                cache_path = self._get_cache_path(text, audio_type)
                if not cache_path.exists():
                    uncached.append(word_data)
        return uncached
    
    def get_audio_path(self, text: str, audio_type: str = "words") -> Optional[str]:
        """Get the audio file path if it exists."""
        cache_path = self._get_cache_path(text, audio_type)
        if cache_path.exists():
            return str(cache_path)
        return None
    
    def clear_cache(self, audio_type: Optional[str] = None):
        """
        Clear cached audio files.
        
        Args:
            audio_type: Specific type to clear, or None for all
        """
        if audio_type:
            cache_subdir = self.cache_dir / audio_type
            if cache_subdir.exists():
                for file in cache_subdir.glob("*.mp3"):
                    file.unlink()
                logger.info(f"Cleared {audio_type} cache")
        else:
            for subdir in ["words", "sentences", "phrases"]:
                self.clear_cache(subdir)
            logger.info("Cleared all audio cache")
    
    def get_cache_stats(self) -> Dict:
        """Get statistics about the audio cache."""
        stats = {
            'total_files': 0,
            'total_size_mb': 0,
            'by_type': {}
        }
        
        for audio_type in ["words", "sentences", "phrases"]:
            type_dir = self.cache_dir / audio_type
            if type_dir.exists():
                files = list(type_dir.glob("*.mp3"))
                size = sum(f.stat().st_size for f in files)
                stats['by_type'][audio_type] = {
                    'files': len(files),
                    'size_mb': round(size / (1024 * 1024), 2)
                }
                stats['total_files'] += len(files)
                stats['total_size_mb'] += size
        
        stats['total_size_mb'] = round(stats['total_size_mb'] / (1024 * 1024), 2)
        return stats


class AudioPlayer:
    """Simple audio player interface for Streamlit."""
    
    def __init__(self, audio_service: AudioService):
        """Initialize with an audio service."""
        self.audio_service = audio_service
    
    def get_audio_html(self, text: str, audio_type: str = "words") -> Optional[str]:
        """
        Get HTML audio element for text.
        
        Returns HTML string that can be rendered with st.markdown(unsafe_allow_html=True)
        """
        audio_path = self.audio_service.get_audio_path(text, audio_type)
        
        if not audio_path:
            # Try to generate
            audio_path = self.audio_service.generate_audio(text, audio_type)
        
        if audio_path and Path(audio_path).exists():
            # Read file and encode as base64 for inline audio
            import base64
            with open(audio_path, 'rb') as f:
                audio_bytes = f.read()
            audio_b64 = base64.b64encode(audio_bytes).decode()
            
            return f'''
            <audio controls style="height: 30px;">
                <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
                Your browser does not support the audio element.
            </audio>
            '''
        
        return None
    
    def get_audio_bytes(self, text: str, audio_type: str = "words") -> Optional[bytes]:
        """Get audio as bytes for Streamlit st.audio()."""
        audio_path = self.audio_service.get_audio_path(text, audio_type)
        
        if not audio_path:
            audio_path = self.audio_service.generate_audio(text, audio_type)
        
        if audio_path and Path(audio_path).exists():
            with open(audio_path, 'rb') as f:
                return f.read()
        
        return None


# Singleton instance
_audio_service = None

def get_audio_service(cache_dir: str = "audio_cache") -> AudioService:
    """Get or create the singleton audio service."""
    global _audio_service
    if _audio_service is None:
        _audio_service = AudioService(cache_dir)
    return _audio_service


if __name__ == "__main__":
    # Test the module
    if GTTS_AVAILABLE:
        service = AudioService("test_audio_cache")
        
        # Test word generation
        print("Testing word audio generation...")
        result = service.generate_word_audio("бал")
        print(f"Generated: {result}")
        
        # Test sentence generation
        print("\nTesting sentence audio generation...")
        result = service.generate_sentence_audio("Мин Башҡортостан яратам")
        print(f"Generated: {result}")
        
        # Get stats
        print("\nCache stats:")
        print(service.get_cache_stats())
    else:
        print("gTTS not available. Install with: pip install gTTS")
