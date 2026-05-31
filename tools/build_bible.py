"""Tool WAT: construye el Style/Character Bible + character sheet (s03_bible).
Tras este tool se abre la COMPUERTA G2 (diseño). SOP: workflows/design_bible.md."""

from tools._common import simple_stage_tool


def main() -> None:
    simple_stage_tool("s03_bible", "Construye el bible y la character sheet (abre compuerta G2).")


if __name__ == "__main__":
    main()
