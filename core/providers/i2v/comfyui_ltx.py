"""Image-to-video con ComfyUI + LTX-Video (primario, pensado para GPU de consumo).

Anima un keyframe a un clip corto (3-6 s) con movimiento sutil (push-in, respiración,
shimmer). Genera a 480-720p; el upscale a 1080 va en s06.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.config import Config
from core.providers.base import I2VProvider

_TODO = (
    "ComfyUILTXProvider no cableado todavía. Fase 1: instalar LTX-Video "
    "(scripts/setup_models.ps1) y completar la llamada al workflow scene_i2v_ltx.json."
)


class ComfyUILTXProvider(I2VProvider):
    def __init__(self, *, options: dict[str, Any], cfg: Config):
        self.cfg = cfg
        self.options = options

    def animate(self, keyframe: Path, motion_prompt: str, *, seconds: float, out_path: Path) -> Path:
        raise NotImplementedError(_TODO)
