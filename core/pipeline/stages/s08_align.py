"""s08_align — subtítulos palabra-por-palabra con faster-whisper.

Salida: assets/{slug}/subtitles/captions.json (CaptionTrack) + captions.srt
GPU:    sí.
"""

from __future__ import annotations

import json

from core.pipeline.context import ProjectContext
from core.providers.registry import get_provider
from core.services.gpu_lock import gpu_lock


def run(ctx: ProjectContext) -> dict:
    transcript = (ctx.script_dir / "narration_full.txt").read_text(encoding="utf-8")
    asr = get_provider("asr", cfg=ctx.cfg)

    ctx.subtitles_dir.mkdir(parents=True, exist_ok=True)
    with gpu_lock():
        track = asr.align(ctx.audio_dir / "narration.wav", transcript)

    (ctx.subtitles_dir / "captions.json").write_text(
        json.dumps(track.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (ctx.subtitles_dir / "captions.srt").write_text(track.to_srt(), encoding="utf-8")

    state = ctx.load_state()
    state.update({"stage": "s08_align", "words": len(track.words)})
    ctx.save_state(state)
    return {"stage": "s08_align", "words": len(track.words)}
