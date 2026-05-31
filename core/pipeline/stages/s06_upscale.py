"""s06_upscale — sube cada clip i2v a 1080x1920 (RealESRGAN).

Salida: assets/{slug}/scenes/NN/clip_1080.mp4
GPU:    sí.
"""

from __future__ import annotations

import json

from core.pipeline.context import ProjectContext
from core.providers.registry import get_provider
from core.schemas import Script
from core.services.gpu_lock import gpu_lock


def run(ctx: ProjectContext) -> dict:
    script = Script(**json.loads((ctx.script_dir / "script.json").read_text(encoding="utf-8")))
    up = get_provider("upscale", cfg=ctx.cfg)
    target = ctx.cfg.settings["video"]["master"]["height"]

    out_clips = []
    for scene in script.scenes:
        sd = ctx.scene_dir(scene.idx)
        with gpu_lock():
            out = up.upscale(sd / "clip.mp4", target_long_side=target, out_path=sd / "clip_1080.mp4")
        out_clips.append(str(out))

    state = ctx.load_state()
    state.update({"stage": "s06_upscale", "clips_1080": out_clips})
    ctx.save_state(state)
    return {"stage": "s06_upscale", "count": len(out_clips)}
