"""Imagen con ComfyUI + SDXL + InstantID (PRIMARIO comercial — OpenRAIL++, LoRA más maduro)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.config import Config
from core.providers.base import Bible, ImageProvider, Scene

_TODO = (
    "ComfyUISDXLProvider (primario) no cableado todavía. Fase 1: instalar SDXL + InstantID "
    "+ LoRA de afieltrado (scripts/setup_models.ps1) y completar el workflow "
    "tools/comfy_graphs/scene_image_sdxl_instantid.json."
)


class ComfyUISDXLProvider(ImageProvider):
    def __init__(self, *, options: dict[str, Any], cfg: Config):
        self.cfg = cfg
        self.options = options

    def generate_character_sheet(self, bible: Bible, out_path: Path) -> Path:
        raise NotImplementedError(_TODO)

    def generate_keyframe(self, scene: Scene, bible: Bible, out_path: Path) -> Path:
        raise NotImplementedError(_TODO)
