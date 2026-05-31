"""Carga de configuración desde config/*.yaml con acceso tipado básico.

Uso:
    from core.config import load_config
    cfg = load_config()
    cfg.settings["gpu"]["budget_mb"]
    cfg.providers["llm"]["provider"]
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from core import ROOT

# Cargar secretos de .env al importar (no falla si python-dotenv no está instalado).
try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:  # pragma: no cover
    pass

CONFIG_DIR = ROOT / "config"


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo de configuración: {path}")
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"El YAML {path} debe ser un mapeo en el nivel raíz.")
    return data


@dataclass(frozen=True)
class Config:
    """Configuración agregada del sistema."""

    settings: dict[str, Any]
    providers: dict[str, Any]
    platforms: dict[str, Any]
    root: Path = ROOT

    # --- Accesos convenientes y resolución de rutas ---

    def path(self, key: str) -> Path:
        """Resuelve una ruta declarada en settings['paths'] contra la raíz."""
        raw = self.settings["paths"][key]
        p = Path(raw)
        return p if p.is_absolute() else (self.root / p)

    @property
    def vram_budget_mb(self) -> int:
        return int(self.settings["gpu"]["budget_mb"])

    @property
    def language(self) -> str:
        return str(self.settings.get("language", "es"))

    def style_preset_path(self, name: str | None = None) -> Path:
        name = name or self.settings.get("default_style_preset", "default")
        return self.root / "config" / "style_presets" / f"{name}.yaml"


@lru_cache(maxsize=1)
def load_config() -> Config:
    return Config(
        settings=_read_yaml(CONFIG_DIR / "settings.yaml"),
        providers=_read_yaml(CONFIG_DIR / "providers.yaml"),
        platforms=_read_yaml(CONFIG_DIR / "platforms.yaml"),
    )
