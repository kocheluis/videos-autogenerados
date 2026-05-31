"""Interfaces (ABCs) de cada capa externa del pipeline.

Cada implementación concreta (local u cloud) hereda de la ABC correspondiente.
El pipeline depende SOLO de estas interfaces, nunca de una implementación concreta.
Esto hace que pasar de local a cloud sea cambiar `config/providers.yaml`.

Las firmas usan tipos del dominio definidos en `core.schemas`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from core.schemas import Bible, CaptionTrack, Scene, Script


class LLMProvider(ABC):
    """Genera texto/JSON estructurado (guion, bible, metadata por plataforma)."""

    @abstractmethod
    def generate_json(
        self, prompt: str, *, system: str | None = None, schema: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Devuelve un objeto JSON validado contra `schema` si se provee."""

    @abstractmethod
    def generate_text(self, prompt: str, *, system: str | None = None) -> str: ...


class ImageProvider(ABC):
    """Genera el character sheet y los keyframes por escena con consistencia."""

    @abstractmethod
    def generate_character_sheet(self, bible: Bible, out_path: Path) -> Path: ...

    @abstractmethod
    def generate_keyframe(self, scene: Scene, bible: Bible, out_path: Path) -> Path:
        """Imagen 1080x1920 que respeta paleta, personaje y style_lock."""


class I2VProvider(ABC):
    """Anima un keyframe a un clip corto (image-to-video)."""

    @abstractmethod
    def animate(
        self, keyframe: Path, motion_prompt: str, *, seconds: float, out_path: Path
    ) -> Path: ...


class UpscaleProvider(ABC):
    @abstractmethod
    def upscale(self, media: Path, *, target_long_side: int, out_path: Path) -> Path: ...


class TTSProvider(ABC):
    """Sintetiza la narración (voz cálida en español; clonación opcional)."""

    @abstractmethod
    def synthesize(self, text: str, *, out_path: Path, speaker_wav: Path | None = None) -> Path: ...


class ASRProvider(ABC):
    """Alinea audio+texto para subtítulos palabra por palabra."""

    @abstractmethod
    def align(self, audio: Path, transcript: str) -> CaptionTrack: ...


class PublishProvider(ABC):
    """Publica o exporta el paquete para subida (según plataforma)."""

    @abstractmethod
    def publish(self, video: Path, metadata: dict[str, Any]) -> dict[str, Any]:
        """Devuelve {status, remote_id?, post_url?} o el paquete exportado."""


# Re-export para imports cómodos desde implementaciones.
__all__ = [
    "LLMProvider",
    "ImageProvider",
    "I2VProvider",
    "UpscaleProvider",
    "TTSProvider",
    "ASRProvider",
    "PublishProvider",
    "Bible",
    "Scene",
    "Script",
    "CaptionTrack",
]
