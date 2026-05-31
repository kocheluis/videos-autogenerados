"""Tool WAT: runner desatendido (consumidor B del state-machine).

Avanza etapa a etapa hasta toparse con una compuerta no aprobada (exit 3), terminar
(exit 0), o fallar (1=error, 2=no cableado). `--auto-approve` salta compuertas concretas
(solo para pruebas; por defecto respeta las 4). Misma fuente de verdad que el agente.

Uso: python -m tools.run_batch --slug <slug> [--auto-approve script,design] [--max-steps 20]
"""

from __future__ import annotations

import argparse

from core.pipeline.context import ProjectContext
from core.pipeline.runner import advance, approve
from tools._common import EXIT_BLOCKED, EXIT_ERROR, EXIT_NOT_WIRED, EXIT_OK, emit


def main() -> None:
    ap = argparse.ArgumentParser(description="Corre el pipeline hasta la próxima compuerta.")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--auto-approve", default="", help="Compuertas a auto-aprobar (coma).")
    ap.add_argument("--max-steps", type=int, default=20)
    args = ap.parse_args()

    ctx = ProjectContext(slug=args.slug)
    auto = {g.strip() for g in args.auto_approve.split(",") if g.strip()}
    steps: list[dict] = []

    for _ in range(args.max_steps):
        try:
            result = advance(ctx)
        except NotImplementedError as exc:
            emit({"ok": False, "error": "not_wired", "detail": str(exc), "steps": steps})
            raise SystemExit(EXIT_NOT_WIRED)
        except Exception as exc:
            emit({"ok": False, "error": type(exc).__name__, "detail": str(exc), "steps": steps})
            raise SystemExit(EXIT_ERROR)

        if result.get("done"):
            emit({"ok": True, "done": True, "steps": steps})
            raise SystemExit(EXIT_OK)

        gate = result.get("blocked_on")
        if gate:
            if gate in auto:
                approve(ctx, gate)
                steps.append({"approved": gate})
                continue
            emit({"ok": True, "blocked_on": gate, "steps": steps})
            raise SystemExit(EXIT_BLOCKED)

        steps.append({"ran": result.get("ran")})

    emit({"ok": True, "steps": steps, "note": "max_steps alcanzado"})


if __name__ == "__main__":
    main()
