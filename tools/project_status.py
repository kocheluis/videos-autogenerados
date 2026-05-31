"""Tool WAT: estado del proyecto y compuerta pendiente (sin GPU)."""

from __future__ import annotations

import argparse

from core.pipeline.context import ProjectContext
from core.pipeline.runner import blocked_gate
from core.pipeline.state_machine import STAGES
from tools._common import EXIT_ERROR, emit


def main() -> None:
    ap = argparse.ArgumentParser(description="Muestra el estado del proyecto.")
    ap.add_argument("--slug", required=True)
    args = ap.parse_args()

    ctx = ProjectContext(slug=args.slug)
    if not ctx.state_path.exists():
        emit({"ok": False, "error": "not_found", "slug": args.slug})
        raise SystemExit(EXIT_ERROR)

    state = ctx.load_state()
    approvals = state.get("approvals", {})
    emit(
        {
            "ok": True,
            "slug": args.slug,
            "stage": state.get("stage"),
            "blocked_on": blocked_gate(ctx),
            "approvals": approvals,
            "stages": [
                {"key": s.key, "gate": s.gate_after, "approved": bool(s.gate_after and approvals.get(s.gate_after))}
                for s in STAGES
            ],
        }
    )


if __name__ == "__main__":
    main()
