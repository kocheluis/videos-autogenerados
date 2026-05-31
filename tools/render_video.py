"""Tool WAT: ensambla el master 9:16 con Remotion (s09_render).
Tras este tool se abre la COMPUERTA G4 (final). SOP: workflows/render_final.md.

--dry-run construye props.json sin invocar Remotion (útil sin Node/modelos)."""

from __future__ import annotations

import argparse

from core.pipeline.context import ProjectContext
from tools._common import execute_stage


def main() -> None:
    ap = argparse.ArgumentParser(description="Render final con Remotion (abre compuerta G4).")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--dry-run", action="store_true", help="Solo genera props.json.")
    args = ap.parse_args()
    execute_stage("s09_render", ProjectContext(slug=args.slug), dry_run=args.dry_run)


if __name__ == "__main__":
    main()
