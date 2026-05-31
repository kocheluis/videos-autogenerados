"""Tool WAT: alinea subtítulos palabra-por-palabra (s08_align, faster-whisper)."""

from tools._common import simple_stage_tool


def main() -> None:
    simple_stage_tool("s08_align", "Genera subtítulos palabra-por-palabra alineados.")


if __name__ == "__main__":
    main()
