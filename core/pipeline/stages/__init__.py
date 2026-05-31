"""Etapas del pipeline. Cada módulo s0X expone `run(ctx, **kwargs) -> dict`.

`get_runner(stage_key)` devuelve la función de ejecución de una etapa por su clave.
"""

from __future__ import annotations

import importlib
from typing import Callable

from core.pipeline.context import ProjectContext

_STAGE_MODULES = {
    "s01_brief": "core.pipeline.stages.s01_brief",
    "s02_script": "core.pipeline.stages.s02_script",
    "s03_bible": "core.pipeline.stages.s03_bible",
    "s04_images": "core.pipeline.stages.s04_images",
    "s05_i2v": "core.pipeline.stages.s05_i2v",
    "s06_upscale": "core.pipeline.stages.s06_upscale",
    "s07_tts": "core.pipeline.stages.s07_tts",
    "s08_align": "core.pipeline.stages.s08_align",
    "s09_render": "core.pipeline.stages.s09_render",
    "s10_publish": "core.pipeline.stages.s10_publish",
}


def get_runner(stage_key: str) -> Callable[..., dict]:
    if stage_key not in _STAGE_MODULES:
        raise KeyError(f"Etapa desconocida: {stage_key}")
    module = importlib.import_module(_STAGE_MODULES[stage_key])
    return getattr(module, "run")


__all__ = ["get_runner", "ProjectContext"]
