"""Tool WAT: sube cada clip i2v a 1080x1920 (s06_upscale, RealESRGAN)."""

from tools._common import simple_stage_tool


def main() -> None:
    simple_stage_tool("s06_upscale", "Upscale de clips i2v a 1080x1920.")


if __name__ == "__main__":
    main()
