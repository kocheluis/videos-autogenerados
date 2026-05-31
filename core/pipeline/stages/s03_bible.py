"""s03_bible — define el Style/Character Bible y genera el character sheet.

Entrada:  script + preset (paleta, style_lock)
Salida:   assets/{slug}/bible/bible.json + character_sheet_{name}.png
GPU:      sí (Ollama para estructurar el bible; ComfyUI para la sheet)
Compuerta: G2 (Diseño) al terminar — aprobar ANTES de gastar GPU en todas las escenas.
"""

from __future__ import annotations

from core.pipeline.context import ProjectContext
from core.providers.registry import get_provider
from core.schemas import Bible, StyleLock
from core.services.gpu_lock import gpu_lock


def run(ctx: ProjectContext) -> dict:
    state = ctx.load_state()
    preset = state.get("style_preset", {})
    palette = preset.get("palette", [])
    style_desc = (preset.get("style_lock", {}) or {}).get("description", StyleLock().description)

    # 1) Estructurar personajes/anchors con el LLM a partir del guion (pendiente: prompt rico).
    #    Por ahora se arma un bible base con paleta y style_lock del preset.
    bible = Bible(
        project_slug=ctx.slug,
        palette=palette,
        style_lock=StyleLock(description=style_desc),
    )
    ctx.bible_dir.mkdir(parents=True, exist_ok=True)
    (ctx.bible_dir / "bible.json").write_text(bible.model_dump_json(indent=2), encoding="utf-8")

    # 2) Character sheet (ancla de consistencia) con ComfyUI/Flux+PuLID.
    image = get_provider("image", cfg=ctx.cfg)
    with gpu_lock():
        sheet = image.generate_character_sheet(bible, ctx.bible_dir / "character_sheet.png")

    state.update({"stage": "s03_bible", "bible_path": str(ctx.bible_dir / "bible.json")})
    ctx.save_state(state)
    return {"stage": "s03_bible", "sheet": str(sheet)}
