"""Runner secuencial con compuertas (Fase 1, manual por CLI).

`advance(ctx)` ejecuta la SIGUIENTE etapa, pero se DETIENE si la etapa actual tiene una
compuerta sin aprobar. En Fase 2 esta misma lógica la consume el worker desde la cola.
"""

from __future__ import annotations

from typing import Any

from core.pipeline.context import ProjectContext
from core.pipeline.stages import get_runner
from core.pipeline.state_machine import gate_for_stage, next_stage


def blocked_gate(ctx: ProjectContext) -> str | None:
    """Devuelve la compuerta pendiente que bloquea el avance, o None."""
    state = ctx.load_state()
    current = state.get("stage")
    if not current:
        return None
    gate = gate_for_stage(current)
    if gate and not state.get("approvals", {}).get(gate):
        return gate
    return None


def approve(ctx: ProjectContext, gate: str) -> None:
    state = ctx.load_state()
    state.setdefault("approvals", {})[gate] = True
    ctx.save_state(state)


def advance(ctx: ProjectContext, **stage_kwargs: Any) -> dict:
    """Ejecuta la siguiente etapa si no hay compuerta pendiente."""
    gate = blocked_gate(ctx)
    if gate:
        return {"blocked_on": gate}

    state = ctx.load_state()
    nxt = next_stage(state.get("stage"))
    if nxt is None:
        return {"done": True}

    runner = get_runner(nxt.key)
    result = runner(ctx, **stage_kwargs)
    return {"ran": nxt.key, "title": nxt.title, "result": result}
