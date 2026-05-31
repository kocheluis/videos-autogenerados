"""Tool WAT: crea un proyecto e intake del brief (s01_brief).

Uso: python -m tools.new_project --topic "..." --platforms youtube,instagram
"""

from __future__ import annotations

import argparse

from core.pipeline.context import ProjectContext, slugify
from core.schemas import Brief
from tools._common import emit, execute_stage


def main() -> None:
    ap = argparse.ArgumentParser(description="Crea un proyecto y ejecuta el intake (s01_brief).")
    ap.add_argument("--topic", required=True, help="Tema del video.")
    ap.add_argument("--platforms", default="youtube", help="Lista separada por comas.")
    ap.add_argument("--style-preset", default="parenting_primerizos")
    ap.add_argument("--duration", type=int, default=150, help="Duración objetivo (s).")
    args = ap.parse_args()

    brief = Brief(
        topic=args.topic,
        platforms=[p.strip() for p in args.platforms.split(",") if p.strip()],  # type: ignore[arg-type]
        style_preset=args.style_preset,
        target_duration_s=args.duration,
    )
    ctx = ProjectContext(slug=slugify(args.topic))
    emit({"slug": ctx.slug})
    execute_stage("s01_brief", ctx, brief=brief)


if __name__ == "__main__":
    main()
