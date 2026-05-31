"""Tool WAT: aprueba una compuerta de revisión humana (script|design|images|final)."""

from __future__ import annotations

import argparse

from core.pipeline.context import ProjectContext
from core.pipeline.runner import approve
from core.pipeline.state_machine import GATES
from tools._common import EXIT_ERROR, emit


def main() -> None:
    ap = argparse.ArgumentParser(description="Aprueba una compuerta.")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--gate", required=True, choices=sorted(set(GATES)))
    args = ap.parse_args()

    ctx = ProjectContext(slug=args.slug)
    if not ctx.state_path.exists():
        emit({"ok": False, "error": "not_found", "slug": args.slug})
        raise SystemExit(EXIT_ERROR)

    approve(ctx, args.gate)
    emit({"ok": True, "slug": args.slug, "approved_gate": args.gate})


if __name__ == "__main__":
    main()
