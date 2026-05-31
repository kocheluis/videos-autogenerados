"""Tool WAT: anima cada keyframe a un clip i2v (s05_i2v, LTX-Video).
Etapa más cara en tiempo. SOP: workflows/produce_clips.md."""

from tools._common import simple_stage_tool


def main() -> None:
    simple_stage_tool("s05_i2v", "Anima los keyframes a clips image-to-video.")


if __name__ == "__main__":
    main()
