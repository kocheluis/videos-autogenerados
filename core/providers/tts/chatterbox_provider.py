"""Voz en off con Chatterbox (MIT, COMERCIAL) — clonación de voz desde 5-10 s.

Úsalo cuando quieras clonar una voz propia/licenciada (speaker_wav). Variante
multilingüe para español. Licencia MIT → apto para monetización.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.config import Config
from core.providers.base import TTSProvider

_TODO = (
    "ChatterboxProvider no cableado todavía. Fase 1: instalar chatterbox (pip), cargar el "
    "modelo multilingüe, clonar desde speaker_wav y sintetizar. Liberar VRAM tras usar."
)


class ChatterboxProvider(TTSProvider):
    def __init__(self, *, options: dict[str, Any], cfg: Config):
        self.cfg = cfg
        self.options = options
        self.language = options.get("language", "es")

    def synthesize(self, text: str, *, out_path: Path, speaker_wav: Path | None = None) -> Path:
        raise NotImplementedError(_TODO)
