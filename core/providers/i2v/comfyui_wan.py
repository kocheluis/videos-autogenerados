"""Image-to-video con ComfyUI + Wan 2.2 TI2V-5B (PRIMARIO — Apache 2.0, mejor movimiento).

Sube el keyframe a ComfyUI, ejecuta el workflow Wan TI2V (704x1280, ~81 frames @24fps)
y descarga el clip. Movimiento sutil controlado por el prompt de movimiento de la escena.
"""

from __future__ import annotations

import zlib
from pathlib import Path
from typing import Any

from core import ROOT
from core.config import Config
from core.providers.base import I2VProvider
from core.services.comfy_client import ComfyClient

_NEG = ("static, still, no motion, blurry, distorted, deformed, flicker, text, watermark, "
        "ugly, low quality, human hands, real person, fingers reaching into frame, "
        "human skin, people entering, hand grabbing")


class ComfyUIWanProvider(I2VProvider):
    def __init__(self, *, options: dict[str, Any], cfg: Config):
        self.cfg = cfg
        self.options = options
        self.model = options.get("model", "wan2.2_ti2v_5B_fp16.safetensors")
        self.frames = int(options.get("frames", 81))          # 4n+1, ~3.4 s @ 24 fps
        self.width = int(options.get("width", 704))
        self.height = int(options.get("height", 1280))         # 9:16 nativo de Wan TI2V
        wf = options.get("workflow", "tools/comfy_graphs/scene_i2v_wan.json")
        self.workflow = (ROOT / wf) if not Path(wf).is_absolute() else Path(wf)
        self.client = ComfyClient(cfg)

    def animate(self, keyframe: Path, motion_prompt: str, *, seconds: float, out_path: Path) -> Path:
        img_name = self.client.upload_image(keyframe)
        wf = self.client.load_workflow(self.workflow)
        seed = zlib.crc32(str(keyframe).encode()) & 0xFFFFFFFF

        overrides = {
            "unet": {"unet_name": self.model},
            "load_image": {"image": img_name},
            "pos": {"text": motion_prompt or "subtle gentle motion, slow camera push-in"},
            "neg": {"text": _NEG},
            "latent": {"width": self.width, "height": self.height, "length": self.frames},
            "sampler": {"seed": seed},
        }
        for nid, kv in overrides.items():
            for k, v in kv.items():
                self.client.set_input(wf, nid, k, v)

        out_path.parent.mkdir(parents=True, exist_ok=True)
        entry = self.client.wait(self.client.submit(wf), timeout=2400)
        self.client.download_outputs(entry, out_path)
        self.client.free()
        return out_path
