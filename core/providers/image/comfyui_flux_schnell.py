"""Imagen con ComfyUI + Flux.1-schnell fp8 (Apache 2.0, COMERCIAL).

Calidad muy superior a SDXL base para personajes humanoides con textura de fieltro
detallada y anatomía coherente. Genera a 832x1472 (9:16) y reescala a 1080x1920.
Flux schnell: 4 pasos, cfg 1.0 (no usa negativo); el estilo va en el prompt positivo.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from core import ROOT
from core.config import Config
from core.providers.base import Bible, ImageProvider, Scene
from core.services.comfy_client import ComfyClient


class ComfyUIFluxSchnellProvider(ImageProvider):
    def __init__(self, *, options: dict[str, Any], cfg: Config):
        self.cfg = cfg
        self.options = options
        self.checkpoint = options.get("checkpoint", "flux1-schnell-fp8.safetensors")
        wf = options.get("workflow", "tools/comfy_graphs/scene_image_flux_schnell.json")
        self.workflow = (ROOT / wf) if not Path(wf).is_absolute() else Path(wf)
        self.client = ComfyClient(cfg)

    def _positive(self, bible: Bible, scene_prompt: str) -> str:
        sl = bible.style_lock
        parts = [sl.prompt_prefix, sl.description, scene_prompt, sl.prompt_suffix]
        if bible.palette:
            parts.append("warm cozy color palette")
        return ", ".join(p.strip() for p in parts if p and p.strip())

    def _generate(self, positive: str, seed: int, out_path: Path) -> Path:
        w = self.cfg.settings["video"]["master"]["width"]
        h = self.cfg.settings["video"]["master"]["height"]
        overrides = {
            "checkpoint": {"ckpt_name": self.checkpoint},
            "pos": {"text": positive},
            "sampler": {"seed": int(seed) % (2**32)},
        }
        from PIL import Image

        out_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as tmp:
            raw = self.client.run(self.workflow, overrides, Path(tmp) / "raw.png")
            img = Image.open(raw).convert("RGB").resize((w, h), Image.LANCZOS)
            img.save(out_path)
        self.client.free()
        return out_path

    def generate_character_sheet(self, bible: Bible, out_path: Path) -> Path:
        anchors = ", ".join(c.face_anchors for c in bible.characters)
        subject = anchors or "a friendly child doll with a warm gentle smile and freckles"
        prompt = f"full body portrait of {subject}, centered, soft plain background"
        return self._generate(self._positive(bible, prompt), bible.style_lock.seed, out_path)

    def generate_keyframe(self, scene: Scene, bible: Bible, out_path: Path) -> Path:
        positive = self._positive(bible, scene.image_prompt)
        return self._generate(positive, bible.style_lock.seed + scene.idx, out_path)
