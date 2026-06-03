"""Modelos del dominio (DTOs Pydantic) compartidos por providers, stages y la UI.

Estos NO son las tablas de la base de datos (eso vive en core/models/). Son las
estructuras que viajan entre etapas y que el LLM debe producir/consumir.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

Platform = Literal["youtube", "instagram", "tiktok", "facebook"]

_VALID_MOTIONS = {"subtle_push_in", "blink_gesture", "glow_pulse"}


# --------------------------------------------------------------------------- #
# Brief / entrada
# --------------------------------------------------------------------------- #
class Brief(BaseModel):
    topic: str
    audience: str = "padres primerizos"
    platforms: list[Platform] = Field(default_factory=lambda: ["youtube"])
    style_preset: str = "parenting_primerizos"
    language: str = "es"
    target_duration_s: int = 150


# --------------------------------------------------------------------------- #
# Guion
# --------------------------------------------------------------------------- #
class Scene(BaseModel):
    idx: int
    narration_text: str          # lo que dice la voz en off (es)
    image_prompt: str = ""       # prompt visual (sin estilo; el estilo lo añade el bible)
    motion_preset: str = "subtle_push_in"  # clave en bible.motion_presets
    duration_s: float = 5.0
    on_screen_note: str = ""     # nota opcional (no son los captions; esos salen del ASR)

    @field_validator("motion_preset", mode="before")
    @classmethod
    def _default_motion(cls, v: str) -> str:
        # El LLM a veces devuelve "" o una clave inválida → caer al preset por defecto.
        return v if v in _VALID_MOTIONS else "subtle_push_in"



class Script(BaseModel):
    title: str
    hook: str
    scenes: list[Scene]

    @property
    def full_narration(self) -> str:
        return " ".join(s.narration_text.strip() for s in self.scenes)


# --------------------------------------------------------------------------- #
# Style / Character Bible
# --------------------------------------------------------------------------- #
class Character(BaseModel):
    name: str
    role: str = ""
    face_anchors: str            # forma de cara, ojos, peinado, color de pelo
    outfit: str                  # vestuario fijo
    sheet_path: str = ""         # ruta al character_sheet_{name}.png aprobado


class StyleLock(BaseModel):
    # Look del referente: muñeco de fieltro HUMANOIDE con piel afieltrada detallada.
    description: str = (
        "a charming needle-felted wool doll character with humanoid body proportions, "
        "highly detailed soft felt skin texture with freckles, big expressive eyes, "
        "knitted fabric clothing, full body, standing, in a realistic cozy room, "
        "warm cinematic lighting, shallow depth of field, professional photography, "
        "stop-motion film aesthetic, intricate handmade detail"
    )
    prompt_prefix: str = ""
    prompt_suffix: str = ""
    negative_prompt: str = (
        "extra arms, extra limbs, extra legs, fused limbs, too many fingers, deformed, "
        "mutated, malformed, disfigured, blurry, low quality, flat, simple, smooth plastic, "
        "glossy cgi, text, watermark, signature"
    )
    steps: int = 25
    guidance: float = 3.5
    seed: int = 1234567
    style_lora: str = ""


class Bible(BaseModel):
    project_slug: str
    palette: list[str] = Field(default_factory=list)  # 3-5 hex cálidos
    characters: list[Character] = Field(default_factory=list)
    style_lock: StyleLock = Field(default_factory=StyleLock)
    # Prompts de movimiento reutilizables para el i2v.
    motion_presets: dict[str, str] = Field(
        default_factory=lambda: {
            "subtle_push_in": "slow camera push-in, gentle breathing, soft particle shimmer",
            "blink_gesture": "character blinks and makes a small hand gesture, static camera",
            "glow_pulse": "warm glow slowly pulsing, dust particles floating",
        }
    )
    version: int = 1
    approved: bool = False


# --------------------------------------------------------------------------- #
# Subtítulos (salida del ASR)
# --------------------------------------------------------------------------- #
class Word(BaseModel):
    text: str
    start: float
    end: float


class CaptionTrack(BaseModel):
    words: list[Word]

    def to_srt(self) -> str:
        def ts(t: float) -> str:
            h, rem = divmod(int(t), 3600)
            m, s = divmod(rem, 60)
            ms = int((t - int(t)) * 1000)
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

        lines: list[str] = []
        for i, w in enumerate(self.words, 1):
            lines += [str(i), f"{ts(w.start)} --> {ts(w.end)}", w.text, ""]
        return "\n".join(lines)
