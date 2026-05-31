"""s01_brief — intake del brief y preparación del proyecto.

Entrada:  topic, platforms, style_preset
Salida:   assets/{slug}/brief.md  +  estado inicial
GPU:      no
"""

from __future__ import annotations

from pathlib import Path

import yaml

from core.pipeline.context import ProjectContext
from core.schemas import Brief


def run(ctx: ProjectContext, *, brief: Brief) -> dict:
    ctx.ensure_dirs()

    # Cargar el preset de estilo si existe (lo genera scripts/analyze_reference.py).
    preset_path = ctx.cfg.style_preset_path(brief.style_preset)
    preset = {}
    if preset_path.exists():
        preset = yaml.safe_load(preset_path.read_text(encoding="utf-8")) or {}

    brief_md = ctx.root / "brief.md"
    brief_md.write_text(
        "\n".join(
            [
                f"# Brief — {ctx.slug}",
                "",
                f"- **Tema:** {brief.topic}",
                f"- **Audiencia:** {brief.audience}",
                f"- **Plataformas:** {', '.join(brief.platforms)}",
                f"- **Idioma:** {brief.language}",
                f"- **Duración objetivo:** {brief.target_duration_s}s",
                f"- **Preset de estilo:** {brief.style_preset}"
                + ("" if preset else "  ⚠️ (preset no encontrado; correr analyze_reference.py)"),
                "",
            ]
        ),
        encoding="utf-8",
    )

    (ctx.root / "brief.json").write_text(brief.model_dump_json(indent=2), encoding="utf-8")

    state = ctx.load_state()
    state.update({"stage": "s01_brief", "brief": brief.model_dump(), "style_preset": preset})
    ctx.save_state(state)
    return {"stage": "s01_brief", "brief_path": str(brief_md), "preset_found": bool(preset)}
