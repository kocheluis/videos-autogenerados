"""Definición declarativa del flujo: etapas, orden y compuertas de revisión humana.

El runner (worker en Fase 2; CLI en Fase 1) consulta estas estructuras para saber
qué etapa sigue y cuándo detenerse esperando aprobación.
"""

from __future__ import annotations

from dataclasses import dataclass

# Identificadores de las 4 compuertas de revisión humana.
GATE_SCRIPT = "script"
GATE_DESIGN = "design"
GATE_IMAGES = "images"
GATE_FINAL = "final"


@dataclass(frozen=True)
class StageDef:
    key: str
    title: str
    uses_gpu: bool
    # Compuerta que se ABRE al terminar esta etapa (None si no hay).
    gate_after: str | None = None


# Orden canónico del pipeline (coincide con el plan aprobado).
STAGES: list[StageDef] = [
    StageDef("s01_brief", "Brief", uses_gpu=False),
    StageDef("s02_script", "Guion (LLM)", uses_gpu=True, gate_after=GATE_SCRIPT),
    StageDef("s03_bible", "Bible + character sheet", uses_gpu=True, gate_after=GATE_DESIGN),
    StageDef("s04_images", "Keyframes por escena", uses_gpu=True, gate_after=GATE_IMAGES),
    StageDef("s05_i2v", "Animación image-to-video", uses_gpu=True),
    StageDef("s06_upscale", "Upscale de clips", uses_gpu=True),
    StageDef("s07_tts", "Voz en off (TTS)", uses_gpu=True),
    StageDef("s08_align", "Subtítulos (ASR)", uses_gpu=True),
    StageDef("s09_render", "Render final (Remotion)", uses_gpu=False, gate_after=GATE_FINAL),
    StageDef("s10_publish", "Publicación", uses_gpu=False),
]

STAGE_BY_KEY = {s.key: s for s in STAGES}
GATES = [s.gate_after for s in STAGES if s.gate_after]


def next_stage(current_key: str | None) -> StageDef | None:
    """Devuelve la etapa siguiente a `current_key` (o la primera si es None)."""
    if current_key is None:
        return STAGES[0]
    keys = [s.key for s in STAGES]
    try:
        i = keys.index(current_key)
    except ValueError:
        raise KeyError(f"Etapa desconocida: {current_key}")
    return STAGES[i + 1] if i + 1 < len(STAGES) else None


def gate_for_stage(stage_key: str) -> str | None:
    return STAGE_BY_KEY[stage_key].gate_after
