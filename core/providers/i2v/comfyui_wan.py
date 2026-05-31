"""Image-to-video con ComfyUI + Wan 2.2 TI2V-5B (fallback local de mayor calidad)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.config import Config
from core.providers.base import I2VProvider

_TODO = "ComfyUIWanProvider (fallback) no cableado todavía. Ver Fase 1/Fase 4."


class ComfyUIWanProvider(I2VProvider):
    def __init__(self, *, options: dict[str, Any], cfg: Config):
        self.cfg = cfg
        self.options = options

    def animate(self, keyframe: Path, motion_prompt: str, *, seconds: float, out_path: Path) -> Path:
        raise NotImplementedError(_TODO)
