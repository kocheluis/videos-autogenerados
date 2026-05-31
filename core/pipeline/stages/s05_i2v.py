"""s05_i2v — anima cada keyframe a un clip corto (LTX-Video), a 480-720p.

Salida: assets/{slug}/scenes/NN/clip.mp4
GPU:    sí (ComfyUI/LTX). Etapa más cara en tiempo (~min por clip).
"""

from __future__ import annotations

import json

from core.pipeline.context import ProjectContext
from core.providers.registry import get_provider
from core.schemas import Bible, Script
from core.services.gpu_lock import gpu_lock


def run(ctx: ProjectContext) -> dict:
    script = Script(**json.loads((ctx.script_dir / "script.json").read_text(encoding="utf-8")))
    bible = Bible(**json.loads((ctx.bible_dir / "bible.json").read_text(encoding="utf-8")))
    i2v = get_provider("i2v", cfg=ctx.cfg)

    clips = []
    for scene in script.scenes:
        sd = ctx.scene_dir(scene.idx)
        motion = bible.motion_presets.get(scene.motion_preset, scene.motion_preset)
        with gpu_lock():
            out = i2v.animate(
                sd / "keyframe.png", motion, seconds=scene.duration_s, out_path=sd / "clip.mp4"
            )
        clips.append(str(out))

    state = ctx.load_state()
    state.update({"stage": "s05_i2v", "clips": clips})
    ctx.save_state(state)
    return {"stage": "s05_i2v", "count": len(clips)}
