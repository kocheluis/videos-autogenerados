"""Exportación para subida MANUAL (TikTok/IG/FB hasta tener auditorías de API).

No publica: deja un paquete listo (video + metadata.json + caption.txt) en
assets/{slug}/publish/{platform}/ para que subas a mano. Esto evita suscripciones
y el bloqueo de auditoría de TikTok.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from core.config import Config
from core.providers.base import PublishProvider


class ManualExportProvider(PublishProvider):
    def __init__(self, *, options: dict[str, Any], cfg: Config):
        self.cfg = cfg
        self.options = options

    def publish(self, video: Path, metadata: dict[str, Any]) -> dict[str, Any]:
        platform = metadata.get("platform", "unknown")
        out_dir = Path(metadata["export_dir"]) / platform
        out_dir.mkdir(parents=True, exist_ok=True)

        dest_video = out_dir / video.name
        if video.resolve() != dest_video.resolve():
            shutil.copy2(video, dest_video)

        (out_dir / "metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        caption = metadata.get("caption") or metadata.get("description", "")
        (out_dir / "caption.txt").write_text(caption, encoding="utf-8")

        return {"status": "exported", "platform": platform, "path": str(out_dir)}
