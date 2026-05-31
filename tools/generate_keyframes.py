"""Tool WAT: genera un keyframe por escena (s04_images, SDXL+InstantID).
Tras este tool se abre la COMPUERTA G3 (keyframes) — aprobar ANTES de animar."""

from tools._common import simple_stage_tool


def main() -> None:
    simple_stage_tool("s04_images", "Genera los keyframes por escena (abre compuerta G3).")


if __name__ == "__main__":
    main()
