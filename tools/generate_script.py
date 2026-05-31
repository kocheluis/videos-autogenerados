"""Tool WAT: genera el guion (s02_script) con Ollama+Qwen2.5. SOP: workflows/generate_script.md.
Tras este tool se abre la COMPUERTA G1 (guion)."""

from tools._common import simple_stage_tool


def main() -> None:
    simple_stage_tool("s02_script", "Genera el guion del proyecto (abre compuerta G1).")


if __name__ == "__main__":
    main()
