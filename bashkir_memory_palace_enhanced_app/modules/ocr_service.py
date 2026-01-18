"""
OCR Service for Bashkir Text Recognition
========================================
Optical Character Recognition for scanning Bashkir text from images.

Features:
- EasyOCR integration with Cyrillic support
- Image preprocessing for better accuracy
- Word extraction and dictionary lookup
- Support for camera capture and file upload
"""

import io
import os
import re
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from pathlib import Path

# Optional imports with graceful fallback
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    easyocr = None

try:
    from PIL import Image, ImageEnhance, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None


@dataclass
class OCRResult:
    """Result from OCR processing."""
    text: str
    confidence: float
    bbox: Optional[Tuple[int, int, int, int]] = None  # x1, y1, x2, y2

    def to_dict(self) -> Dict:
        return {
            'text': self.text,
            'confidence': self.confidence,
            'bbox': self.bbox
        }


@dataclass
class WordMatch:
    """A word extracted from OCR matched to dictionary."""
    scanned_text: str
    matched_word: Optional[str]
    english: Optional[str]
    russian: Optional[str]
    confidence: float
    in_dictionary: bool

    def to_dict(self) -> Dict:
        return {
            'scanned_text': self.scanned_text,
            'matched_word': self.matched_word,
            'english': self.english,
            'russian': self.russian,
            'confidence': self.confidence,
            'in_dictionary': self.in_dictionary
        }


class OCRService:
    """
    Service for OCR text recognition with Bashkir/Cyrillic support.

    Uses EasyOCR for text detection and recognition, with preprocessing
    optimizations for Bashkir Cyrillic text.
    """

    # Bashkir-specific characters (in addition to Russian Cyrillic)
    BASHKIR_CHARS = set('ҺһӘәҮүҠҡҒғӨөҪҫҺһЙйЎўҰұҶҷ')

    # Common Bashkir letter patterns
    BASHKIR_PATTERNS = [
        r'[ҺһӘәҮүҠҡҒғӨөҪҫ]',  # Unique Bashkir letters
        r'[аәоөуүыеи]',  # Vowels including Bashkir-specific
    ]

    def __init__(self, languages: List[str] = None, gpu: bool = False):
        """
        Initialize OCR service.

        Args:
            languages: List of language codes (default: ['ru', 'en'] for Cyrillic + Latin)
            gpu: Whether to use GPU acceleration
        """
        self.languages = languages or ['ru', 'en']
        self.gpu = gpu
        self._reader: Optional[Any] = None
        self._initialized = False
        self._init_error: Optional[str] = None

    @property
    def is_available(self) -> bool:
        """Check if EasyOCR is available."""
        return EASYOCR_AVAILABLE and PIL_AVAILABLE

    @property
    def is_initialized(self) -> bool:
        """Check if the OCR reader has been initialized."""
        return self._initialized

    @property
    def init_error(self) -> Optional[str]:
        """Get initialization error message if any."""
        return self._init_error

    def initialize(self) -> bool:
        """
        Initialize the EasyOCR reader.

        This downloads models on first use (~100MB for Cyrillic).

        Returns:
            bool: True if initialization successful
        """
        if not EASYOCR_AVAILABLE:
            self._init_error = "EasyOCR not installed. Install with: pip install easyocr"
            return False

        if not PIL_AVAILABLE:
            self._init_error = "Pillow not installed. Install with: pip install Pillow"
            return False

        try:
            self._reader = easyocr.Reader(
                self.languages,
                gpu=self.gpu,
                verbose=False
            )
            self._initialized = True
            self._init_error = None
            return True

        except Exception as e:
            self._init_error = f"Failed to initialize EasyOCR: {str(e)}"
            self._initialized = False
            return False

    def preprocess_image(self, image: 'Image.Image') -> 'Image.Image':
        """
        Preprocess image for better OCR accuracy.

        Applies:
        - Grayscale conversion
        - Contrast enhancement
        - Sharpening
        - Noise reduction

        Args:
            image: PIL Image object

        Returns:
            Preprocessed PIL Image
        """
        if not PIL_AVAILABLE:
            return image

        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Convert to grayscale for text
        gray = image.convert('L')

        # Enhance contrast
        enhancer = ImageEnhance.Contrast(gray)
        enhanced = enhancer.enhance(1.5)

        # Sharpen
        sharpened = enhanced.filter(ImageFilter.SHARPEN)

        # Optional: Apply slight blur to reduce noise then sharpen again
        # denoised = sharpened.filter(ImageFilter.MedianFilter(size=3))

        return sharpened.convert('RGB')

    def scan_image(
        self,
        image_source: Any,
        preprocess: bool = True,
        min_confidence: float = 0.3
    ) -> List[OCRResult]:
        """
        Scan an image and extract text.

        Args:
            image_source: Can be file path, PIL Image, bytes, or numpy array
            preprocess: Whether to apply preprocessing
            min_confidence: Minimum confidence threshold (0-1)

        Returns:
            List of OCRResult objects
        """
        if not self._initialized:
            if not self.initialize():
                return []

        try:
            # Convert to PIL Image if needed
            if isinstance(image_source, str):
                # File path
                image = Image.open(image_source)
            elif isinstance(image_source, bytes):
                # Bytes
                image = Image.open(io.BytesIO(image_source))
            elif hasattr(image_source, 'read'):
                # File-like object
                image = Image.open(image_source)
            elif PIL_AVAILABLE and isinstance(image_source, Image.Image):
                image = image_source
            elif NUMPY_AVAILABLE and isinstance(image_source, np.ndarray):
                image = Image.fromarray(image_source)
            else:
                image = image_source

            # Preprocess
            if preprocess and PIL_AVAILABLE:
                image = self.preprocess_image(image)

            # Convert to numpy for EasyOCR
            if NUMPY_AVAILABLE:
                image_array = np.array(image)
            else:
                # Save to temp and use path
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                    image.save(f, 'PNG')
                    image_array = f.name

            # Run OCR
            results = self._reader.readtext(image_array)

            # Parse results
            ocr_results = []
            for bbox, text, confidence in results:
                if confidence >= min_confidence and text.strip():
                    # Convert bbox to simple format
                    x_coords = [p[0] for p in bbox]
                    y_coords = [p[1] for p in bbox]
                    simple_bbox = (
                        int(min(x_coords)),
                        int(min(y_coords)),
                        int(max(x_coords)),
                        int(max(y_coords))
                    )

                    ocr_results.append(OCRResult(
                        text=text.strip(),
                        confidence=confidence,
                        bbox=simple_bbox
                    ))

            return ocr_results

        except Exception as e:
            self._init_error = f"OCR scan failed: {str(e)}"
            return []

    def extract_words(self, ocr_results: List[OCRResult]) -> List[str]:
        """
        Extract individual words from OCR results.

        Args:
            ocr_results: List of OCRResult objects

        Returns:
            List of individual words
        """
        words = []
        for result in ocr_results:
            # Split on whitespace and punctuation
            text_words = re.split(r'[\s,.:;!?\-–—()"\'\[\]{}]+', result.text)
            words.extend([w.strip() for w in text_words if w.strip()])
        return words

    def is_bashkir_text(self, text: str) -> bool:
        """
        Check if text contains Bashkir-specific characters.

        Args:
            text: Text to check

        Returns:
            True if text contains Bashkir characters
        """
        return bool(self.BASHKIR_CHARS & set(text))

    def match_to_dictionary(
        self,
        scanned_words: List[str],
        dictionary: List[Dict],
        fuzzy_threshold: float = 0.8
    ) -> List[WordMatch]:
        """
        Match scanned words to dictionary entries.

        Args:
            scanned_words: List of words from OCR
            dictionary: List of word dictionaries with 'bashkir' key
            fuzzy_threshold: Similarity threshold for fuzzy matching (0-1)

        Returns:
            List of WordMatch objects
        """
        # Build lookup dictionaries
        exact_lookup = {w['bashkir'].lower(): w for w in dictionary}

        matches = []
        for scanned in scanned_words:
            scanned_lower = scanned.lower()

            # Try exact match first
            if scanned_lower in exact_lookup:
                word = exact_lookup[scanned_lower]
                matches.append(WordMatch(
                    scanned_text=scanned,
                    matched_word=word['bashkir'],
                    english=word.get('english'),
                    russian=word.get('russian'),
                    confidence=1.0,
                    in_dictionary=True
                ))
            else:
                # Try fuzzy matching
                best_match = None
                best_score = 0

                for dict_word, word_data in exact_lookup.items():
                    score = self._similarity(scanned_lower, dict_word)
                    if score > best_score and score >= fuzzy_threshold:
                        best_score = score
                        best_match = word_data

                if best_match:
                    matches.append(WordMatch(
                        scanned_text=scanned,
                        matched_word=best_match['bashkir'],
                        english=best_match.get('english'),
                        russian=best_match.get('russian'),
                        confidence=best_score,
                        in_dictionary=True
                    ))
                else:
                    # No match found
                    matches.append(WordMatch(
                        scanned_text=scanned,
                        matched_word=None,
                        english=None,
                        russian=None,
                        confidence=0,
                        in_dictionary=False
                    ))

        return matches

    def _similarity(self, s1: str, s2: str) -> float:
        """
        Calculate similarity between two strings using Levenshtein ratio.

        Args:
            s1, s2: Strings to compare

        Returns:
            Similarity score between 0 and 1
        """
        if not s1 or not s2:
            return 0.0

        if s1 == s2:
            return 1.0

        # Simple Levenshtein distance
        len1, len2 = len(s1), len(s2)

        if len1 > len2:
            s1, s2 = s2, s1
            len1, len2 = len2, len1

        # Use only two rows for space efficiency
        prev_row = list(range(len1 + 1))
        curr_row = [0] * (len1 + 1)

        for i in range(1, len2 + 1):
            curr_row[0] = i
            for j in range(1, len1 + 1):
                cost = 0 if s1[j - 1] == s2[i - 1] else 1
                curr_row[j] = min(
                    prev_row[j] + 1,      # deletion
                    curr_row[j - 1] + 1,  # insertion
                    prev_row[j - 1] + cost  # substitution
                )
            prev_row, curr_row = curr_row, prev_row

        distance = prev_row[len1]
        max_len = max(len1, len2)
        return 1.0 - (distance / max_len)

    def scan_and_lookup(
        self,
        image_source: Any,
        dictionary: List[Dict],
        preprocess: bool = True,
        min_confidence: float = 0.3,
        fuzzy_threshold: float = 0.8
    ) -> Dict[str, Any]:
        """
        Complete pipeline: scan image, extract words, match to dictionary.

        Args:
            image_source: Image to scan
            dictionary: Word dictionary
            preprocess: Whether to preprocess image
            min_confidence: OCR confidence threshold
            fuzzy_threshold: Dictionary matching threshold

        Returns:
            Dictionary with 'raw_results', 'words', 'matches', and statistics
        """
        # Run OCR
        raw_results = self.scan_image(image_source, preprocess, min_confidence)

        # Extract words
        words = self.extract_words(raw_results)

        # Match to dictionary
        matches = self.match_to_dictionary(words, dictionary, fuzzy_threshold)

        # Calculate statistics
        found_count = sum(1 for m in matches if m.in_dictionary)
        bashkir_count = sum(1 for w in words if self.is_bashkir_text(w))

        return {
            'raw_results': [r.to_dict() for r in raw_results],
            'words': words,
            'matches': [m.to_dict() for m in matches],
            'statistics': {
                'total_regions': len(raw_results),
                'total_words': len(words),
                'dictionary_matches': found_count,
                'bashkir_words': bashkir_count,
                'match_rate': found_count / len(words) if words else 0
            }
        }


# Singleton instance
_ocr_service: Optional[OCRService] = None


def get_ocr_service() -> OCRService:
    """Get or create the OCR service singleton."""
    global _ocr_service
    if _ocr_service is None:
        _ocr_service = OCRService()
    return _ocr_service


def scan_text_from_image(
    image_source: Any,
    dictionary: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Convenience function to scan text from an image.

    Args:
        image_source: Image file path, bytes, or PIL Image
        dictionary: Optional word dictionary for matching

    Returns:
        Scan results dictionary
    """
    service = get_ocr_service()

    if not service.is_available:
        return {
            'error': 'OCR not available. Install with: pip install easyocr Pillow',
            'raw_results': [],
            'words': [],
            'matches': []
        }

    if dictionary:
        return service.scan_and_lookup(image_source, dictionary)
    else:
        results = service.scan_image(image_source)
        words = service.extract_words(results)
        return {
            'raw_results': [r.to_dict() for r in results],
            'words': words,
            'matches': [],
            'statistics': {
                'total_regions': len(results),
                'total_words': len(words)
            }
        }
