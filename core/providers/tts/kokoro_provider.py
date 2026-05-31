"""Voz en off con Kokoro (Apache 2.0, COMERCIAL) — ligero (82M), voces en español.

Buena opción por defecto para narración en es: rápido, licencia permisiva, calidad alta
para su tamaño. Para clonar una voz propia, usar Chatterbox (ver chatterbox_provider).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.config import Config
from core.providers.base import TTSProvider

_TODO = (
    "KokoroProvider no cableado todavía. Fase 1: instalar kokoro (pip), elegir voz es, "
    "sintetizar narración a WAV. Liberar VRAM tras usar (o correr en CPU)."
)


class KokoroProvider(TTSProvider):
    def __init__(self, *, options: dict[str, Any], cfg: Config):
        self.cfg = cfg
        self.options = options
        self.voice = options.get("voice", "ef_dora")  # voz española de Kokoro

    def synthesize(self, text: str, *, out_path: Path, speaker_wav: Path | None = None) -> Path:
        raise NotImplementedError(_TODO)
