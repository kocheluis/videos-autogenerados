"""Imagen con ComfyUI + Flux.1-schnell (Apache 2.0, COMERCIAL) — alternativa a SDXL.

Flux.1-schnell es la ÚNICA variante Flux con licencia comercial (Apache 2.0). NO usar
Flux.1-dev (licencia no comercial). Corre en 12 GB y es rápido; consistencia vía
PuLID/IPAdapter + LoRA de afieltrado.

Fase 1: cargar el workflow JSON (tools/comfy_graphs/scene_image_flux_schnell.json),
inyectar prompt/seed/lora/paleta, encolar en ComfyUI (/prompt) y copiar la salida.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.config import Config
from core.providers.base import Bible, ImageProvider, Scene

_TODO = (
    "ComfyUIFluxSchnellProvider no cableado todavía. Fase 1: instalar Flux.1-schnell (Apache) "
    "+ LoRA de afieltrado (scripts/setup_models.ps1) y completar la llamada al workflow ComfyUI."
)


class ComfyUIFluxSchnellProvider(ImageProvider):
    def __init__(self, *, options: dict[str, Any], cfg: Config):
        self.cfg = cfg
        self.options = options

    def generate_character_sheet(self, bible: Bible, out_path: Path) -> Path:
        raise NotImplementedError(_TODO)

    def generate_keyframe(self, scene: Scene, bible: Bible, out_path: Path) -> Path:
        raise NotImplementedError(_TODO)
