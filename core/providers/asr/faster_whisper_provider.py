"""Alineación de subtítulos palabra-por-palabra con faster-whisper (medium, es).

Transcribe el WAV con word_timestamps=True y devuelve un CaptionTrack que Remotion
usa para los captions tipo karaoke.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.config import Config
from core.providers.base import ASRProvider, CaptionTrack

_TODO = (
    "FasterWhisperProvider no cableado todavía. Fase 1: instalar faster-whisper, "
    "transcribir con word_timestamps=True y mapear a CaptionTrack. Liberar VRAM tras usar."
)


class FasterWhisperProvider(ASRProvider):
    def __init__(self, *, options: dict[str, Any], cfg: Config):
        self.cfg = cfg
        self.options = options
        self.model_size = options.get("model_size", "medium")

    def align(self, audio: Path, transcript: str) -> CaptionTrack:
        raise NotImplementedError(_TODO)
