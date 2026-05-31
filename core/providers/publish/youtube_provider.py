"""Publicación en YouTube vía Data API v3 (la más permisiva para automatizar).

Sube como `private` por defecto; tú lo pasas a público tras revisar. Requiere OAuth
(client_secret.json + token). Implementación pendiente de credenciales (Fase 3).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.config import Config
from core.providers.base import PublishProvider

_TODO = (
    "YouTubeProvider no cableado todavía. Fase 3: configurar OAuth (google-api-python-client) "
    "y videos().insert con status.privacyStatus='private'."
)


class YouTubeProvider(PublishProvider):
    def __init__(self, *, options: dict[str, Any], cfg: Config):
        self.cfg = cfg
        self.options = options

    def publish(self, video: Path, metadata: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError(_TODO)
