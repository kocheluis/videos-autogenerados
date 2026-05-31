"""s02_script — genera el guion (LLM) a partir del brief y el preset de estilo.

Entrada:  brief + preset (de state.json)
Salida:   assets/{slug}/script/script.json (Script: title, hook, scenes[])
GPU:      sí (Ollama) -> se descarga tras responder (keep_alive:0)
Compuerta: G1 (Guion) al terminar.
"""

from __future__ import annotations

from core.pipeline.context import ProjectContext
from core.providers.registry import get_provider
from core.schemas import Brief, Script
from core.services.gpu_lock import gpu_lock

SYSTEM = (
    "Eres un guionista de Reels educativos en español (es-LA) para padres primerizos. "
    "Escribes guiones claros, cálidos y con gancho, divididos en escenas cortas. "
    "Cada escena trae la narración (voz en off) y una descripción visual neutra "
    "(sin estilo artístico; el estilo lo aplica otro módulo)."
)


def _prompt(brief: Brief, preset: dict) -> str:
    # ~2.6 palabras/segundo es un ritmo natural de narración en es-LA.
    clip_s = max((preset.get("pacing", {}) or {}).get("recommended_clip_seconds", 6), 6)
    n = max(10, min(round(brief.target_duration_s / clip_s), 18))
    wps = round(clip_s * 2.6)
    total = round(brief.target_duration_s * 2.6)
    return (
        f"Tema: {brief.topic}\n"
        f"Audiencia: {brief.audience}\n"
        f"Duración objetivo: {brief.target_duration_s} s → {n} escenas de ~{clip_s} s.\n"
        f"IMPORTANTE de longitud: cada 'narration_text' debe tener ~{wps} palabras "
        f"(1-2 frases completas y naturales en es-LA), NO frases telegráficas. "
        f"La narración TOTAL debe rondar las {total} palabras para llenar la duración.\n\n"
        "Devuelve SOLO un JSON con esta forma:\n"
        '{ "title": str, "hook": str, "scenes": [ '
        '{ "idx": int, "narration_text": str, "image_prompt": str, '
        '"motion_preset": "subtle_push_in"|"blink_gesture"|"glow_pulse", '
        '"duration_s": number, "on_screen_note": str } ] }'
    )


def run(ctx: ProjectContext) -> dict:
    state = ctx.load_state()
    brief = Brief(**state["brief"])
    preset = state.get("style_preset", {})

    llm = get_provider("llm", cfg=ctx.cfg)
    with gpu_lock():
        data = llm.generate_json(_prompt(brief, preset), system=SYSTEM, schema=Script.model_json_schema())

    script = Script(**data)
    out = ctx.script_dir / "script.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(script.model_dump_json(indent=2), encoding="utf-8")
    (ctx.script_dir / "narration_full.txt").write_text(script.full_narration, encoding="utf-8")

    state.update({"stage": "s02_script", "script_path": str(out), "n_scenes": len(script.scenes)})
    ctx.save_state(state)
    return {"stage": "s02_script", "scenes": len(script.scenes), "script_path": str(out)}
