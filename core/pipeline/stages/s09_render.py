"""s09_render — ensambla clips/keyframes + audio + subtítulos con Remotion.

Para el MVP usa los keyframes con Ken Burns (si no hay clip i2v). Copia los assets a
render/public/{slug}/ (para que Remotion los cargue vía staticFile) y sincroniza la
duración de las escenas con la del audio.

Salida:    assets/{slug}/render/master_9x16.mp4
GPU:       Chromium (poca VRAM).
Compuerta: G4 (Final).
"""

from __future__ import annotations

import contextlib
import json
import shutil
import subprocess
import wave
from pathlib import Path

from core.pipeline.context import ProjectContext
from core.schemas import Script


def _audio_duration_s(wav: Path) -> float:
    if not wav.exists():
        return 0.0
    with contextlib.closing(wave.open(str(wav), "r")) as w:
        return w.getnframes() / float(w.getframerate() or 1)


def _stage(src: Path, public_dir: Path, rel: str) -> str:
    """Copia src a public_dir/rel y devuelve el path relativo (posix) para staticFile."""
    dst = public_dir / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return rel.replace("\\", "/")


def _build_props(ctx: ProjectContext, script: Script) -> dict:
    fps = ctx.cfg.settings["video"]["master"]["fps"]
    w = ctx.cfg.settings["video"]["master"]["width"]
    h = ctx.cfg.settings["video"]["master"]["height"]

    public_root = ctx.cfg.path("remotion_dir") / "public"
    proj_dir = public_root / ctx.slug
    if proj_dir.exists():
        shutil.rmtree(proj_dir, ignore_errors=True)
    proj_dir.mkdir(parents=True, exist_ok=True)

    # Audio
    wav = ctx.audio_dir / "narration.wav"
    audio_rel = _stage(wav, public_root, f"{ctx.slug}/audio/narration.wav") if wav.exists() else ""
    audio_dur = _audio_duration_s(wav)

    # Escala las duraciones del guion para que sumen la duración del audio.
    total_script = sum(max(s.duration_s, 0.1) for s in script.scenes) or 1.0
    target = audio_dur if audio_dur > 0 else total_script
    scale = target / total_script

    scenes: list[dict] = []
    for s in script.scenes:
        sd = ctx.scene_dir(s.idx)
        clip = sd / "clip_1080.mp4"
        key = sd / "keyframe.png"
        if clip.exists():
            rel = _stage(clip, public_root, f"{ctx.slug}/scenes/{s.idx:02d}/clip.mp4")
            is_video = True
        elif key.exists():
            rel = _stage(key, public_root, f"{ctx.slug}/scenes/{s.idx:02d}/keyframe.png")
            is_video = False
        else:
            continue
        frames = max(int(round(s.duration_s * scale * fps)), fps)  # mínimo 1 s
        scenes.append({"src": rel, "durationInFrames": frames, "isVideo": is_video})

    captions = json.loads((ctx.subtitles_dir / "captions.json").read_text(encoding="utf-8")) if (
        ctx.subtitles_dir / "captions.json"
    ).exists() else {"words": []}

    return {
        "title": script.title,
        "audio": audio_rel,
        "fps": fps,
        "width": w,
        "height": h,
        "scenes": scenes,
        "captions": captions,
    }


def run(ctx: ProjectContext, *, dry_run: bool = False) -> dict:
    script = Script(**json.loads((ctx.script_dir / "script.json").read_text(encoding="utf-8")))

    # Guard de frescura: nunca renderizar con subtítulos más viejos que el audio
    # (si se regeneró la voz, hay que re-alinear primero). Evita el desfase de captions.
    wav = ctx.audio_dir / "narration.wav"
    caps = ctx.subtitles_dir / "captions.json"
    if wav.exists() and caps.exists() and caps.stat().st_mtime < wav.stat().st_mtime - 1:
        raise RuntimeError(
            "captions.json es más viejo que narration.wav: re-ejecuta align_captions (s08) "
            "antes del render para que los subtítulos coincidan con la voz."
        )

    ctx.render_dir.mkdir(parents=True, exist_ok=True)
    props = _build_props(ctx, script)
    props_path = ctx.render_dir / "props.json"
    props_path.write_text(json.dumps(props, ensure_ascii=False, indent=2), encoding="utf-8")

    out = ctx.render_dir / "master_9x16.mp4"
    if dry_run:
        return {"stage": "s09_render", "props": str(props_path), "scenes": len(props["scenes"]), "dry_run": True}

    remotion_dir = ctx.cfg.path("remotion_dir")
    cmd = ["npx", "remotion", "render", "VerticalVideo", str(out), f"--props={props_path}"]
    subprocess.run(cmd, cwd=str(remotion_dir), check=True, shell=True)

    state = ctx.load_state()
    state.update({"stage": "s09_render", "master": str(out)})
    ctx.save_state(state)
    return {"stage": "s09_render", "master": str(out), "scenes": len(props["scenes"])}
