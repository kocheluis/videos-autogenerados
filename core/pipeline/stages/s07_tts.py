"""s07_tts — narración (voz en off) con XTTS/Piper.

Salida: assets/{slug}/audio/narration.wav
GPU:    sí/CPU (XTTS en GPU; Piper en CPU).
"""

from __future__ import annotations

import json
from pathlib import Path

from core.pipeline.context import ProjectContext
from core.providers.registry import get_provider
from core.schemas import Script
from core.services.gpu_lock import gpu_lock


def run(ctx: ProjectContext) -> dict:
    script = Script(**json.loads((ctx.script_dir / "script.json").read_text(encoding="utf-8")))
    tts = get_provider("tts", cfg=ctx.cfg)

    speaker = ctx.cfg.providers["tts"].get("xtts", {}).get("speaker_wav") or None
    ctx.audio_dir.mkdir(parents=True, exist_ok=True)
    with gpu_lock():
        wav = tts.synthesize(
            script.full_narration,
            out_path=ctx.audio_dir / "narration.wav",
            speaker_wav=Path(speaker) if speaker else None,
        )

    state = ctx.load_state()
    state.update({"stage": "s07_tts", "narration_wav": str(wav)})
    ctx.save_state(state)
    return {"stage": "s07_tts", "wav": str(wav)}
