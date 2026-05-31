"""Alineación de subtítulos palabra-por-palabra con faster-whisper (medium, es).

Transcribe el WAV con word_timestamps=True y devuelve un CaptionTrack con tiempos
por palabra que Remotion usa para los captions tipo karaoke. Libera VRAM al terminar.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.config import Config
from core.providers.base import ASRProvider, CaptionTrack
from core.schemas import Word


class FasterWhisperProvider(ASRProvider):
    def __init__(self, *, options: dict[str, Any], cfg: Config):
        self.cfg = cfg
        self.options = options
        self.model_size = options.get("model_size", "medium")
        self.language = options.get("language", "es")
        self.device = options.get("device", "cuda")
        self.compute_type = options.get("compute_type", "float16")

    def _load_model(self):
        from faster_whisper import WhisperModel

        try:
            return WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)
        except Exception:
            # Fallback robusto a CPU si CUDA/cuDNN no está disponible.
            return WhisperModel(self.model_size, device="cpu", compute_type="int8")

    def align(self, audio: Path, transcript: str) -> CaptionTrack:
        model = self._load_model()
        try:
            segments, _info = model.transcribe(
                str(audio),
                language=self.language,
                word_timestamps=True,
                initial_prompt=transcript[:200] if transcript else None,
            )
            words: list[Word] = []
            for seg in segments:
                for w in (seg.words or []):
                    text = w.word.strip()
                    if text:
                        words.append(Word(text=text, start=round(w.start, 3), end=round(w.end, 3)))
        finally:
            del model
            try:
                import torch

                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except ImportError:
                pass

        return CaptionTrack(words=words)
