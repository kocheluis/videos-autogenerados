"""Interfaz web (FastAPI) — revisar/editar guion con IA, monitor por bloques, logs, estilo.

Reutiliza el núcleo WAT: lanza los mismos tools (`python -m tools.*`) como subprocesos,
captura su salida a logs/<stage>.log y refleja el estado (state.json + procesos vivos).

Arranque:  python -m apps.api.main   (o uvicorn apps.api.main:app --port 8800)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from core import ROOT
from core.config import load_config
from core.pipeline.context import ProjectContext, slugify
from core.pipeline.runner import approve as approve_gate
from core.pipeline.runner import blocked_gate
from core.pipeline.state_machine import STAGES, gate_for_stage
from core.providers.registry import get_provider
from core.schemas import Brief, Script

cfg = load_config()
ASSETS = cfg.path("assets_dir")
STATIC = Path(__file__).parent / "static"
STYLES_DIR = ROOT / "config" / "styles"

# stage_key -> módulo de tool que lo ejecuta
STAGE_TOOL = {
    "s02_script": "tools.generate_script",
    "s03_bible": "tools.build_bible",
    "s04_images": "tools.generate_keyframes",
    "s05_i2v": "tools.animate_clips",
    "s06_upscale": "tools.upscale_clips",
    "s07_tts": "tools.synthesize_voice",
    "s08_align": "tools.align_captions",
    "s09_render": "tools.render_video",
    "s10_publish": "tools.publish",
}

# Registro en memoria de procesos en ejecución: (slug, stage) -> Popen
_running: dict[tuple[str, str], subprocess.Popen] = {}

app = FastAPI(title="Generador de Reels — Panel")
ASSETS.mkdir(parents=True, exist_ok=True)
app.mount("/assets", StaticFiles(directory=str(ASSETS)), name="assets")


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _styles() -> list[dict]:
    out = []
    for p in sorted(STYLES_DIR.glob("*.yaml")):
        d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        out.append({"name": d.get("name", p.stem), "label": d.get("label", p.stem),
                    "description": d.get("description", ""), "textures": d.get("textures", [])})
    return out


def _proc_alive(slug: str, stage: str) -> bool:
    p = _running.get((slug, stage))
    return p is not None and p.poll() is None


def _stage_status(ctx: ProjectContext) -> list[dict]:
    state = ctx.load_state()
    approvals = state.get("approvals", {})
    cur = state.get("stage")
    keys = [s.key for s in STAGES]
    cur_i = keys.index(cur) if cur in keys else -1
    blocked = blocked_gate(ctx)
    res = []
    for i, s in enumerate(STAGES):
        if _proc_alive(ctx.slug, s.key):
            st = "running"
        elif s.gate_after and blocked == s.gate_after:
            st = "blocked"
        elif i <= cur_i:
            st = "done"
        else:
            st = "pending"
        res.append({"key": s.key, "title": s.title, "gate": s.gate_after,
                    "approved": bool(s.gate_after and approvals.get(s.gate_after)), "status": st})
    return res


def _ctx(slug: str) -> ProjectContext:
    ctx = ProjectContext(slug=slug)
    if not ctx.state_path.exists():
        raise HTTPException(404, f"Proyecto '{slug}' no existe")
    return ctx


# --------------------------------------------------------------------------- #
# Modelos de request
# --------------------------------------------------------------------------- #
class NewProject(BaseModel):
    topic: str
    platforms: list[str] = ["youtube"]
    style: str = "crochet_con_matices"
    duration: int = 150


class ScriptIn(BaseModel):
    script: dict


# --------------------------------------------------------------------------- #
# Rutas
# --------------------------------------------------------------------------- #
@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return (STATIC / "index.html").read_text(encoding="utf-8")


@app.get("/api/styles")
def styles() -> Any:
    return _styles()


@app.get("/api/projects")
def projects() -> Any:
    out = []
    for d in sorted(ASSETS.glob("*/state.json")):
        ctx = ProjectContext(slug=d.parent.name)
        st = ctx.load_state()
        out.append({"slug": ctx.slug, "stage": st.get("stage"),
                    "topic": (st.get("brief") or {}).get("topic", "")})
    return out


@app.post("/api/projects")
def create_project(body: NewProject) -> Any:
    brief = Brief(topic=body.topic, platforms=body.platforms,  # type: ignore[arg-type]
                  style_preset=body.style, target_duration_s=body.duration)
    ctx = ProjectContext(slug=slugify(body.topic))
    from core.pipeline.stages import get_runner
    get_runner("s01_brief")(ctx, brief=brief)
    return {"slug": ctx.slug}


@app.get("/api/projects/{slug}")
def project(slug: str) -> Any:
    ctx = _ctx(slug)
    state = ctx.load_state()
    script_p = ctx.script_dir / "script.json"
    script = yaml.safe_load(script_p.read_text(encoding="utf-8")) if script_p.exists() else None
    return {
        "slug": slug,
        "topic": (state.get("brief") or {}).get("topic", ""),
        "style": (state.get("brief") or {}).get("style_preset", ""),
        "stage": state.get("stage"),
        "blocked_on": blocked_gate(ctx),
        "stages": _stage_status(ctx),
        "script": script,
        "has_character_sheet": (ctx.bible_dir / "character_sheet.png").exists(),
        "n_keyframes": len(list(ctx.scenes_dir.glob("*/keyframe.png"))),
        "has_audio": (ctx.audio_dir / "narration.wav").exists(),
        "has_video": (ctx.render_dir / "master_9x16.mp4").exists(),
    }


@app.get("/api/projects/{slug}/status")
def status(slug: str) -> Any:
    ctx = _ctx(slug)
    return {"stages": _stage_status(ctx), "blocked_on": blocked_gate(ctx)}


@app.put("/api/projects/{slug}/script")
def save_script(slug: str, body: ScriptIn) -> Any:
    ctx = _ctx(slug)
    script = Script(**body.script)  # valida
    (ctx.script_dir).mkdir(parents=True, exist_ok=True)
    (ctx.script_dir / "script.json").write_text(script.model_dump_json(indent=2), encoding="utf-8")
    (ctx.script_dir / "narration_full.txt").write_text(script.full_narration, encoding="utf-8")
    return {"ok": True}


@app.post("/api/projects/{slug}/script/rewrite")
def rewrite_script(slug: str) -> Any:
    """Reescribe la narración con la IA para que suene más cálida/amigable."""
    ctx = _ctx(slug)
    script = Script(**yaml.safe_load((ctx.script_dir / "script.json").read_text(encoding="utf-8")))
    llm = get_provider("llm", cfg=ctx.cfg)
    system = ("Eres editor de guiones para padres. Reescribe la narración para que suene MÁS "
              "CÁLIDA, CERCANA y AMIGABLE en es-LA, sin cambiar la estructura ni el número de "
              "escenas, conservando idx, image_prompt, motion_preset y duration_s.")
    prompt = ("Reescribe SOLO el campo narration_text de cada escena, más amigable y empático. "
              "Devuelve el MISMO JSON con esta forma:\n" + script.model_dump_json())
    data = llm.generate_json(prompt, system=system, schema=Script.model_json_schema())
    new = Script(**data)
    (ctx.script_dir / "script.json").write_text(new.model_dump_json(indent=2), encoding="utf-8")
    (ctx.script_dir / "narration_full.txt").write_text(new.full_narration, encoding="utf-8")
    return {"ok": True, "script": new.model_dump()}


@app.post("/api/projects/{slug}/approve/{gate}")
def approve(slug: str, gate: str) -> Any:
    ctx = _ctx(slug)
    approve_gate(ctx, gate)
    return {"ok": True}


@app.post("/api/projects/{slug}/run/{stage}")
def run_stage(slug: str, stage: str) -> Any:
    ctx = _ctx(slug)
    if stage not in STAGE_TOOL:
        raise HTTPException(400, f"Etapa no ejecutable: {stage}")
    if _proc_alive(slug, stage):
        return {"ok": True, "already_running": True}
    # Bloqueo por compuerta de una etapa anterior
    if blocked_gate(ctx):
        raise HTTPException(409, f"Bloqueado por compuerta: {blocked_gate(ctx)}")
    ctx.logs_dir.mkdir(parents=True, exist_ok=True)
    logf = open(ctx.logs_dir / f"{stage}.log", "w", encoding="utf-8")
    p = subprocess.Popen([sys.executable, "-m", STAGE_TOOL[stage], "--slug", slug],
                         cwd=str(ROOT), stdout=logf, stderr=subprocess.STDOUT)
    _running[(slug, stage)] = p
    return {"ok": True, "pid": p.pid}


@app.get("/api/projects/{slug}/logs")
def logs(slug: str, stage: str, tail: int = 200) -> Any:
    ctx = _ctx(slug)
    f = ctx.logs_dir / f"{stage}.log"
    if not f.exists():
        return {"log": ""}
    lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
    return {"log": "\n".join(lines[-tail:]), "running": _proc_alive(slug, stage)}


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8800)


if __name__ == "__main__":
    main()
