"""Voz en off con Piper (rápido, CPU) — fallback con voz española predefinida."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.config import Config
from core.providers.base import TTSProvider

_TODO = "PiperProvider no cableado todavía. Fase 1: instalar piper y la voz es_ES."


class PiperProvider(TTSProvider):
    def __init__(self, *, options: dict[str, Any], cfg: Config):
        self.cfg = cfg
        self.options = options
        self.voice = options.get("voice", "es_ES-davefx-medium")

    def synthesize(self, text: str, *, out_path: Path, speaker_wav: Path | None = None) -> Path:
        raise NotImplementedError(_TODO)
