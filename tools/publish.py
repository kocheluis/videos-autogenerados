"""Tool WAT: deriva variantes y publica/exporta (s10_publish).
YouTube auto; TikTok/IG/FB export manual (auditoría). SOP: workflows/publish_video.md."""

from tools._common import simple_stage_tool


def main() -> None:
    simple_stage_tool("s10_publish", "Publica en YouTube y exporta paquetes para el resto.")


if __name__ == "__main__":
    main()
