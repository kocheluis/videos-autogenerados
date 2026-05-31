"""s09_render — ensambla clips + audio + captions + overlays con Remotion.

Llama a la CLI de Remotion (`npx remotion render`) pasando un JSON de props con las
rutas de clips, audio, captions y bible. Produce el master 9:16 y un thumbnail.

Salida:    assets/{slug}/render/master_9x16.mp4 + thumbnail.png
GPU:       Chromium (poca VRAM; nunca solapado con ComfyUI/Ollama).
Compuerta: G4 (Final).
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from core.pipeline.context import ProjectContext
from core.schemas import Script


def _build_props(ctx: ProjectContext, script: Script) -> dict:
    captions = json.loads((ctx.subtitles_dir / "captions.json").read_text(encoding="utf-8"))
    scenes = []
    for s in script.scenes:
        sd = ctx.scene_dir(s.idx)
        clip = sd / "clip_1080.mp4"
        scenes.append({"idx": s.idx, "clip": str(clip), "duration_s": s.duration_s})
    return {
        "title": script.title,
        "audio": str(ctx.audio_dir / "narration.wav"),
        "captions": captions,
        "scenes": scenes,
        "width": ctx.cfg.settings["video"]["master"]["width"],
        "height": ctx.cfg.settings["video"]["master"]["height"],
        "fps": ctx.cfg.settings["video"]["master"]["fps"],
    }


def run(ctx: ProjectContext, *, dry_run: bool = False) -> dict:
    script = Script(**json.loads((ctx.script_dir / "script.json").read_text(encoding="utf-8")))
    ctx.render_dir.mkdir(parents=True, exist_ok=True)
    props = _build_props(ctx, script)
    props_path = ctx.render_dir / "props.json"
    props_path.write_text(json.dumps(props, ensure_ascii=False, indent=2), encoding="utf-8")

    out = ctx.render_dir / "master_9x16.mp4"
    if dry_run:
        return {"stage": "s09_render", "props": str(props_path), "dry_run": True}

    remotion_dir = ctx.cfg.path("remotion_dir")
    cmd = [
        "npx", "remotion", "render", "VerticalVideo", str(out),
        f"--props={props_path}",
    ]
    subprocess.run(cmd, cwd=str(remotion_dir), check=True)

    state = ctx.load_state()
    state.update({"stage": "s09_render", "master": str(out)})
    ctx.save_state(state)
    return {"stage": "s09_render", "master": str(out)}
