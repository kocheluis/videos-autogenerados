"""s04_images — keyframe 1080x1920 por escena (Flux+PuLID, paleta y style_lock fijos).

Salida:    assets/{slug}/scenes/NN/keyframe.png
GPU:       sí (ComfyUI)
Compuerta: G3 (Imágenes) — aprobar el keyframe ANTES de animar (el i2v es caro).
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
    image = get_provider("image", cfg=ctx.cfg)

    produced = []
    for scene in script.scenes:
        sd = ctx.scene_dir(scene.idx)
        sd.mkdir(parents=True, exist_ok=True)
        with gpu_lock():
            out = image.generate_keyframe(scene, bible, sd / "keyframe.png")
        produced.append(str(out))

    state = ctx.load_state()
    state.update({"stage": "s04_images", "keyframes": produced})
    ctx.save_state(state)
    return {"stage": "s04_images", "count": len(produced)}
