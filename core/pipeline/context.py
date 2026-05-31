"""ProjectContext — rutas de assets y estado persistido por proyecto.

En Fase 1 (MVP manual, sin DB) el estado vive en assets/{slug}/state.json. En Fase 2
este estado se migra a SQLite/SQLAlchemy sin cambiar las firmas de las etapas.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from core.config import Config, load_config


def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:60] or "proyecto"


@dataclass
class ProjectContext:
    slug: str
    cfg: Config = field(default_factory=load_config)

    @property
    def root(self) -> Path:
        return self.cfg.path("assets_dir") / self.slug

    # Sub-carpetas estándar por proyecto.
    @property
    def bible_dir(self) -> Path: return self.root / "bible"
    @property
    def script_dir(self) -> Path: return self.root / "script"
    @property
    def scenes_dir(self) -> Path: return self.root / "scenes"
    @property
    def audio_dir(self) -> Path: return self.root / "audio"
    @property
    def subtitles_dir(self) -> Path: return self.root / "subtitles"
    @property
    def render_dir(self) -> Path: return self.root / "render"
    @property
    def publish_dir(self) -> Path: return self.root / "publish"
    @property
    def logs_dir(self) -> Path: return self.root / "logs"
    @property
    def state_path(self) -> Path: return self.root / "state.json"

    def scene_dir(self, idx: int) -> Path:
        return self.scenes_dir / f"{idx:02d}"

    def ensure_dirs(self) -> None:
        for d in (
            self.bible_dir, self.script_dir, self.scenes_dir, self.audio_dir,
            self.subtitles_dir, self.render_dir, self.publish_dir, self.logs_dir,
        ):
            d.mkdir(parents=True, exist_ok=True)

    # --- Estado (Fase 1: JSON) ---
    def load_state(self) -> dict[str, Any]:
        if self.state_path.exists():
            return json.loads(self.state_path.read_text(encoding="utf-8"))
        return {"slug": self.slug, "stage": None, "approvals": {}}

    def save_state(self, state: dict[str, Any]) -> None:
        self.ensure_dirs()
        self.state_path.write_text(
            json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
        )
