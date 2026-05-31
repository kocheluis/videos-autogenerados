"""Núcleo del sistema de generación de videos autogenerados."""

from pathlib import Path

# Raíz del proyecto (carpeta que contiene config/, core/, render/, ...).
ROOT = Path(__file__).resolve().parent.parent

__all__ = ["ROOT"]
