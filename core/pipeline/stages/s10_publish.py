"""s10_publish — deriva variantes (1:1, 16:9), genera metadata/SEO y publica/exporta.

Por plataforma (config/platforms.yaml): YouTube auto (cuando esté cableado), el resto
exporta paquete para subida manual (ManualExportProvider) hasta tener auditorías.

Salida: assets/{slug}/publish/{platform}/{video, metadata.json, caption.txt}
GPU:    no.
"""

from __future__ import annotations

import json

from core.pipeline.context import ProjectContext
from core.providers.registry import get_provider
from core.schemas import Script


def run(ctx: ProjectContext) -> dict:
    script = Script(**json.loads((ctx.script_dir / "script.json").read_text(encoding="utf-8")))
    master = ctx.render_dir / "master_9x16.mp4"
    platforms_cfg = ctx.cfg.platforms
    publish_cfg = ctx.cfg.providers["publish"]

    results = []
    for platform, pconf in publish_cfg.items():
        if not pconf.get("enabled", False) and pconf.get("provider") != "manual_export":
            continue
        provider = get_provider("publish", name=pconf["provider"], cfg=ctx.cfg)
        metadata = {
            "platform": platform,
            "title": script.title,
            "description": script.hook,
            "caption": script.hook,
            "export_dir": str(ctx.publish_dir),
            "rules": platforms_cfg.get(platform, {}),
        }
        results.append(provider.publish(master, metadata))

    state = ctx.load_state()
    state.update({"stage": "s10_publish", "results": results})
    ctx.save_state(state)
    return {"stage": "s10_publish", "results": results}
