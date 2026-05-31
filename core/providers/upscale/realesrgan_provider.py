"""Upscale de clips i2v (480-720p -> 1080x1920) con RealESRGAN en ComfyUI/CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.config import Config
from core.providers.base import UpscaleProvider

_TODO = "RealESRGANProvider no cableado todavía. Ver Fase 1."


class RealESRGANProvider(UpscaleProvider):
    def __init__(self, *, options: dict[str, Any], cfg: Config):
        self.cfg = cfg
        self.options = options

    def upscale(self, media: Path, *, target_long_side: int, out_path: Path) -> Path:
        raise NotImplementedError(_TODO)
