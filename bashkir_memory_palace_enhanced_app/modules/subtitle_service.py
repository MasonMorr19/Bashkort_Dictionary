"""
Subtitle Service for Bashkir Video Content
==========================================
Real-time and batch subtitle generation using Whisper models.

Features:
- Local subtitle generation with faster-whisper
- Real-time streaming transcription
- VTT/SRT subtitle file generation
- Bashkir/Russian/English language support
- Audio extraction from video files
"""

import os
import io
import re
import tempfile
import threading
import queue
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Callable, Generator, Any
from dataclasses import dataclass, field
from datetime import timedelta
from enum import Enum

# Optional imports with graceful fallback
try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False
    WhisperModel = None

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False
    sf = None

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    AudioSegment = None


class SubtitleFormat(Enum):
    """Supported subtitle formats."""
    SRT = "srt"
    VTT = "vtt"
    JSON = "json"
    TEXT = "txt"


@dataclass
class SubtitleSegment:
    """A single subtitle segment."""
    index: int
    start: float  # seconds
    end: float    # seconds
    text: str
    confidence: float = 1.0
    language: str = ""

    def to_srt(self) -> str:
        """Convert to SRT format."""
        start_time = self._format_timestamp(self.start, srt=True)
        end_time = self._format_timestamp(self.end, srt=True)
        return f"{self.index}\n{start_time} --> {end_time}\n{self.text}\n"

    def to_vtt(self) -> str:
        """Convert to VTT format."""
        start_time = self._format_timestamp(self.start, srt=False)
        end_time = self._format_timestamp(self.end, srt=False)
        return f"{start_time} --> {end_time}\n{self.text}\n"

    def _format_timestamp(self, seconds: float, srt: bool = True) -> str:
        """Format timestamp for SRT or VTT."""
        td = timedelta(seconds=seconds)
        hours, remainder = divmod(td.total_seconds(), 3600)
        minutes, secs = divmod(remainder, 60)
        milliseconds = int((secs - int(secs)) * 1000)

        if srt:
            return f"{int(hours):02d}:{int(minutes):02d}:{int(secs):02d},{milliseconds:03d}"
        else:
            return f"{int(hours):02d}:{int(minutes):02d}:{int(secs):02d}.{milliseconds:03d}"

    def to_dict(self) -> Dict:
        return {
            'index': self.index,
            'start': self.start,
            'end': self.end,
            'text': self.text,
            'confidence': self.confidence,
            'language': self.language
        }


@dataclass
class TranscriptionResult:
    """Result of a transcription."""
    segments: List[SubtitleSegment]
    language: str
    duration: float
    text: str = ""

    def __post_init__(self):
        if not self.text:
            self.text = " ".join(seg.text for seg in self.segments)

    def to_srt(self) -> str:
        """Export as SRT format."""
        return "\n".join(seg.to_srt() for seg in self.segments)

    def to_vtt(self) -> str:
        """Export as VTT format."""
        header = "WEBVTT\n\n"
        body = "\n".join(seg.to_vtt() for seg in self.segments)
        return header + body

    def to_json(self) -> List[Dict]:
        """Export as JSON."""
        return [seg.to_dict() for seg in self.segments]


class SubtitleService:
    """
    Service for generating subtitles from audio/video content.

    Uses faster-whisper for efficient local transcription with
    support for Bashkir, Russian, and other languages.
    """

    # Model sizes and their characteristics
    MODEL_INFO = {
        'tiny': {'size': '~75MB', 'speed': 'fastest', 'accuracy': 'low'},
        'base': {'size': '~150MB', 'speed': 'fast', 'accuracy': 'medium'},
        'small': {'size': '~500MB', 'speed': 'medium', 'accuracy': 'good'},
        'medium': {'size': '~1.5GB', 'speed': 'slow', 'accuracy': 'high'},
        'large-v3': {'size': '~3GB', 'speed': 'slowest', 'accuracy': 'best'}
    }

    # Language codes supported
    LANGUAGE_CODES = {
        'bashkir': 'ba',  # Note: Whisper may not have full Bashkir support
        'russian': 'ru',
        'english': 'en',
        'tatar': 'tt',    # Related Turkic language
        'turkish': 'tr',  # Related Turkic language
        'auto': None      # Auto-detect
    }

    def __init__(
        self,
        model_size: str = "base",
        device: str = "auto",
        compute_type: str = "auto"
    ):
        """
        Initialize subtitle service.

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large-v3)
            device: Device to use (auto, cpu, cuda)
            compute_type: Compute type (auto, int8, float16, float32)
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self._model: Optional[WhisperModel] = None
        self._initialized = False
        self._init_error: Optional[str] = None
        self._is_loading = False

        # Streaming state
        self._stream_queue: Optional[queue.Queue] = None
        self._stream_thread: Optional[threading.Thread] = None
        self._stream_running = False

    @property
    def is_available(self) -> bool:
        """Check if faster-whisper is available."""
        return FASTER_WHISPER_AVAILABLE

    @property
    def is_initialized(self) -> bool:
        """Check if model is loaded."""
        return self._initialized

    @property
    def init_error(self) -> Optional[str]:
        """Get initialization error if any."""
        return self._init_error

    def initialize(self, progress_callback: Optional[Callable[[str], None]] = None) -> bool:
        """
        Initialize and load the Whisper model.

        Args:
            progress_callback: Optional callback for progress updates

        Returns:
            bool: True if initialization successful
        """
        if not FASTER_WHISPER_AVAILABLE:
            self._init_error = "faster-whisper not installed. Install with: pip install faster-whisper"
            return False

        if self._initialized:
            return True

        if self._is_loading:
            return False

        self._is_loading = True

        try:
            if progress_callback:
                progress_callback(f"Loading Whisper {self.model_size} model...")

            # Determine device
            device = self.device
            if device == "auto":
                try:
                    import torch
                    device = "cuda" if torch.cuda.is_available() else "cpu"
                except ImportError:
                    device = "cpu"

            # Determine compute type
            compute_type = self.compute_type
            if compute_type == "auto":
                compute_type = "float16" if device == "cuda" else "int8"

            if progress_callback:
                progress_callback(f"Using device: {device}, compute: {compute_type}")

            # Load model
            self._model = WhisperModel(
                self.model_size,
                device=device,
                compute_type=compute_type
            )

            self._initialized = True
            self._init_error = None

            if progress_callback:
                progress_callback("Model loaded successfully!")

            return True

        except Exception as e:
            self._init_error = f"Failed to load model: {str(e)}"
            return False

        finally:
            self._is_loading = False

    def transcribe_audio(
        self,
        audio_source: Any,
        language: str = "auto",
        task: str = "transcribe",
        word_timestamps: bool = False,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> Optional[TranscriptionResult]:
        """
        Transcribe audio to text with timestamps.

        Args:
            audio_source: Audio file path, bytes, or numpy array
            language: Language code or 'auto' for detection
            task: 'transcribe' or 'translate' (to English)
            word_timestamps: Include word-level timestamps
            progress_callback: Callback with progress (0-1)

        Returns:
            TranscriptionResult or None if failed
        """
        if not self._initialized:
            if not self.initialize():
                return None

        try:
            # Handle different input types
            if isinstance(audio_source, (str, Path)):
                audio_path = str(audio_source)
            elif isinstance(audio_source, bytes):
                # Save to temp file
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                    f.write(audio_source)
                    audio_path = f.name
            elif hasattr(audio_source, 'read'):
                # File-like object
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                    f.write(audio_source.read())
                    audio_path = f.name
            else:
                # Assume numpy array
                if SOUNDFILE_AVAILABLE:
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                        sf.write(f.name, audio_source, 16000)
                        audio_path = f.name
                else:
                    self._init_error = "Cannot process numpy array without soundfile"
                    return None

            # Get language code
            lang_code = self.LANGUAGE_CODES.get(language.lower(), language if language != "auto" else None)

            # Run transcription
            segments_gen, info = self._model.transcribe(
                audio_path,
                language=lang_code,
                task=task,
                word_timestamps=word_timestamps,
                vad_filter=True,  # Voice activity detection
                vad_parameters=dict(min_silence_duration_ms=500)
            )

            # Collect segments
            segments = []
            total_duration = info.duration if hasattr(info, 'duration') else 0

            for i, segment in enumerate(segments_gen):
                sub_segment = SubtitleSegment(
                    index=i + 1,
                    start=segment.start,
                    end=segment.end,
                    text=segment.text.strip(),
                    confidence=segment.avg_logprob if hasattr(segment, 'avg_logprob') else 1.0,
                    language=info.language if hasattr(info, 'language') else language
                )
                segments.append(sub_segment)

                if progress_callback and total_duration > 0:
                    progress = min(segment.end / total_duration, 1.0)
                    progress_callback(progress)

            return TranscriptionResult(
                segments=segments,
                language=info.language if hasattr(info, 'language') else language,
                duration=total_duration
            )

        except Exception as e:
            self._init_error = f"Transcription failed: {str(e)}"
            return None

    def transcribe_video(
        self,
        video_path: str,
        language: str = "auto",
        task: str = "transcribe",
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> Optional[TranscriptionResult]:
        """
        Extract audio from video and transcribe.

        Args:
            video_path: Path to video file
            language: Language code or 'auto'
            task: 'transcribe' or 'translate'
            progress_callback: Callback with (status, progress)

        Returns:
            TranscriptionResult or None
        """
        if not PYDUB_AVAILABLE:
            self._init_error = "pydub required for video processing. Install with: pip install pydub"
            return None

        try:
            if progress_callback:
                progress_callback("Extracting audio from video...", 0.0)

            # Extract audio using pydub
            audio = AudioSegment.from_file(video_path)

            # Export to temporary WAV
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                audio.export(f.name, format='wav', parameters=["-ar", "16000", "-ac", "1"])
                audio_path = f.name

            if progress_callback:
                progress_callback("Transcribing audio...", 0.1)

            # Transcribe
            def inner_progress(p):
                if progress_callback:
                    progress_callback("Transcribing...", 0.1 + p * 0.9)

            result = self.transcribe_audio(
                audio_path,
                language=language,
                task=task,
                progress_callback=inner_progress
            )

            # Cleanup
            try:
                os.unlink(audio_path)
            except:
                pass

            return result

        except Exception as e:
            self._init_error = f"Video transcription failed: {str(e)}"
            return None

    def generate_subtitle_file(
        self,
        result: TranscriptionResult,
        output_path: str,
        format: SubtitleFormat = SubtitleFormat.SRT
    ) -> bool:
        """
        Save transcription result to subtitle file.

        Args:
            result: TranscriptionResult to save
            output_path: Output file path
            format: Subtitle format (SRT, VTT, JSON)

        Returns:
            bool: True if successful
        """
        try:
            if format == SubtitleFormat.SRT:
                content = result.to_srt()
            elif format == SubtitleFormat.VTT:
                content = result.to_vtt()
            elif format == SubtitleFormat.JSON:
                import json
                content = json.dumps(result.to_json(), ensure_ascii=False, indent=2)
            else:
                content = result.text

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return True

        except Exception as e:
            self._init_error = f"Failed to save subtitle file: {str(e)}"
            return False

    def start_streaming_transcription(
        self,
        audio_callback: Callable[[], Optional[bytes]],
        result_callback: Callable[[SubtitleSegment], None],
        language: str = "auto",
        chunk_duration: float = 2.0
    ):
        """
        Start streaming transcription from live audio.

        Args:
            audio_callback: Function that returns audio chunks (16kHz mono WAV)
            result_callback: Function called with each transcribed segment
            language: Language code or 'auto'
            chunk_duration: Duration of each chunk in seconds
        """
        if not self._initialized:
            if not self.initialize():
                return

        self._stream_running = True
        self._stream_queue = queue.Queue()

        def stream_worker():
            segment_index = 0
            accumulated_audio = b''
            chunk_size = int(16000 * chunk_duration * 2)  # 16-bit samples

            while self._stream_running:
                try:
                    # Get audio chunk
                    audio_chunk = audio_callback()
                    if audio_chunk is None:
                        time.sleep(0.1)
                        continue

                    accumulated_audio += audio_chunk

                    # Process when we have enough audio
                    if len(accumulated_audio) >= chunk_size:
                        # Save to temp file
                        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                            # Write WAV header
                            import struct
                            num_samples = len(accumulated_audio) // 2
                            f.write(b'RIFF')
                            f.write(struct.pack('<I', 36 + len(accumulated_audio)))
                            f.write(b'WAVE')
                            f.write(b'fmt ')
                            f.write(struct.pack('<I', 16))  # Subchunk1Size
                            f.write(struct.pack('<H', 1))   # AudioFormat (PCM)
                            f.write(struct.pack('<H', 1))   # NumChannels
                            f.write(struct.pack('<I', 16000))  # SampleRate
                            f.write(struct.pack('<I', 32000))  # ByteRate
                            f.write(struct.pack('<H', 2))   # BlockAlign
                            f.write(struct.pack('<H', 16))  # BitsPerSample
                            f.write(b'data')
                            f.write(struct.pack('<I', len(accumulated_audio)))
                            f.write(accumulated_audio)
                            temp_path = f.name

                        # Transcribe
                        lang_code = self.LANGUAGE_CODES.get(language.lower(), None)
                        segments_gen, info = self._model.transcribe(
                            temp_path,
                            language=lang_code,
                            vad_filter=True
                        )

                        for segment in segments_gen:
                            segment_index += 1
                            sub_segment = SubtitleSegment(
                                index=segment_index,
                                start=segment.start,
                                end=segment.end,
                                text=segment.text.strip(),
                                language=info.language if hasattr(info, 'language') else language
                            )
                            result_callback(sub_segment)

                        # Cleanup
                        try:
                            os.unlink(temp_path)
                        except:
                            pass

                        accumulated_audio = b''

                except Exception as e:
                    print(f"Streaming error: {e}")
                    time.sleep(0.5)

        self._stream_thread = threading.Thread(target=stream_worker, daemon=True)
        self._stream_thread.start()

    def stop_streaming_transcription(self):
        """Stop streaming transcription."""
        self._stream_running = False
        if self._stream_thread:
            self._stream_thread.join(timeout=2.0)
            self._stream_thread = None

    def get_model_info(self) -> Dict:
        """Get information about loaded model."""
        return {
            'model_size': self.model_size,
            'device': self.device,
            'compute_type': self.compute_type,
            'initialized': self._initialized,
            'info': self.MODEL_INFO.get(self.model_size, {})
        }


# Singleton instance
_subtitle_service: Optional[SubtitleService] = None


def get_subtitle_service(model_size: str = "base") -> SubtitleService:
    """Get or create the subtitle service singleton."""
    global _subtitle_service
    if _subtitle_service is None or _subtitle_service.model_size != model_size:
        _subtitle_service = SubtitleService(model_size=model_size)
    return _subtitle_service


def transcribe_to_subtitles(
    audio_or_video_path: str,
    output_format: SubtitleFormat = SubtitleFormat.VTT,
    language: str = "auto",
    model_size: str = "base"
) -> Tuple[Optional[str], Optional[str]]:
    """
    Convenience function to transcribe audio/video to subtitles.

    Args:
        audio_or_video_path: Path to audio or video file
        output_format: Desired subtitle format
        language: Language code or 'auto'
        model_size: Whisper model size

    Returns:
        Tuple of (subtitle_content, detected_language) or (None, None) if failed
    """
    service = get_subtitle_service(model_size)

    if not service.is_available:
        return None, "faster-whisper not available"

    # Determine if video or audio
    ext = Path(audio_or_video_path).suffix.lower()
    video_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv'}

    if ext in video_extensions:
        result = service.transcribe_video(audio_or_video_path, language=language)
    else:
        result = service.transcribe_audio(audio_or_video_path, language=language)

    if result is None:
        return None, service.init_error

    if output_format == SubtitleFormat.SRT:
        content = result.to_srt()
    elif output_format == SubtitleFormat.VTT:
        content = result.to_vtt()
    elif output_format == SubtitleFormat.JSON:
        import json
        content = json.dumps(result.to_json(), ensure_ascii=False)
    else:
        content = result.text

    return content, result.language
