"""Imagen con ComfyUI + SDXL (PRIMARIO comercial — OpenRAIL++, LoRA más maduro).

Versión base: text2img SDXL (prompts de estilo). InstantID + LoRA de afieltrado se
añaden encima cambiando el workflow JSON (scene_image_sdxl_instantid.json) sin tocar
esta clase. Genera a 832x1472 (9:16 nativo de SDXL) y reescala a 1080x1920.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from core import ROOT
from core.config import Config
from core.providers.base import Bible, ImageProvider, Scene
from core.services.comfy_client import ComfyClient


class ComfyUISDXLProvider(ImageProvider):
    def __init__(self, *, options: dict[str, Any], cfg: Config):
        self.cfg = cfg
        self.options = options
        self.checkpoint = options.get("checkpoint", "sd_xl_base_1.0.safetensors")
        self.steps = int(options.get("steps", 30))
        self.cfg_scale = float(options.get("cfg", 6.0))
        wf = options.get("workflow", "tools/comfy_graphs/scene_image_sdxl.json")
        self.workflow = (ROOT / wf) if not Path(wf).is_absolute() else Path(wf)
        self.client = ComfyClient(cfg)

    def _positive(self, bible: Bible, scene_prompt: str) -> str:
        sl = bible.style_lock
        # Enfatizar el estilo de material (lana/crochet) para que domine en SDXL base.
        style = f"({sl.description}:1.3)"
        parts = [sl.prompt_prefix, style, scene_prompt, sl.prompt_suffix]
        if bible.palette:
            parts.append("warm cozy color palette")
        return ", ".join(p.strip() for p in parts if p and p.strip())

    def _generate(self, positive: str, negative: str, seed: int, out_path: Path) -> Path:
        w = self.cfg.settings["video"]["master"]["width"]
        h = self.cfg.settings["video"]["master"]["height"]
        overrides = {
            "4": {"ckpt_name": self.checkpoint},
            "6": {"text": positive},
            "7": {"text": negative},
            "3": {"seed": int(seed) % (2**32), "steps": self.steps, "cfg": self.cfg_scale},
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
        subject = anchors or "a friendly pregnant mother doll with a warm gentle smile, rosy cheeks"
        prompt = f"a single cute full-body character, {subject}, centered, plain soft cream studio background"
        positive = self._positive(bible, prompt)
        return self._generate(positive, bible.style_lock.negative_prompt, bible.style_lock.seed, out_path)

    def generate_keyframe(self, scene: Scene, bible: Bible, out_path: Path) -> Path:
        positive = self._positive(bible, scene.image_prompt)
        seed = bible.style_lock.seed + scene.idx  # variación controlada por escena
        return self._generate(positive, bible.style_lock.negative_prompt, seed, out_path)
