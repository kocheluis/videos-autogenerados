"""process_manager — arranca/para servicios locales (ComfyUI, Ollama) por fase.

Mantener ComfyUI y Ollama encendidos a la vez puede no caber en 12 GB. Este módulo
permite levantar un servicio justo antes de su fase y apagarlo al terminar, liberando VRAM.

Para Ollama basta `OLLAMA_KEEP_ALIVE=0` (descarga el modelo tras responder) — no hace
falta matar el proceso. Para ComfyUI se usa el endpoint /free entre lotes, o se reinicia.

NOTA (Fase 1): implementación mínima. Asume que instalaste ComfyUI en
settings.paths.comfyui_dir y Ollama como servicio del sistema.
"""

from __future__ import annotations

import subprocess
import time
from contextlib import contextmanager

import httpx

from core.config import load_config


def _is_up(url: str) -> bool:
    try:
        httpx.get(url, timeout=1.5)
        return True
    except Exception:
        return False


def free_comfyui_vram() -> None:
    """Pide a ComfyUI liberar modelos y VRAM (entre imagen / i2v / upscale)."""
    cfg = load_config()
    base_url = cfg.settings["services"]["comfyui"]["base_url"]
    try:
        httpx.post(f"{base_url}/free", json={"unload_models": True, "free_memory": True}, timeout=10)
    except Exception:
        pass


@contextmanager
def comfyui_running(boot_timeout: float = 120.0):
    """Garantiza ComfyUI arriba durante el bloque (lo arranca si no está)."""
    cfg = load_config()
    svc = cfg.settings["services"]["comfyui"]
    base_url = svc["base_url"]
    started = False
    proc: subprocess.Popen | None = None
    if not _is_up(base_url):
        comfy_dir = cfg.path("comfyui_dir")
        args = ["python", "main.py", *svc.get("extra_args", [])]
        proc = subprocess.Popen(args, cwd=str(comfy_dir))
        started = True
        deadline = time.monotonic() + boot_timeout
        while not _is_up(base_url):
            if time.monotonic() > deadline:
                raise TimeoutError("ComfyUI no respondió a tiempo.")
            time.sleep(2)
    try:
        yield base_url
    finally:
        free_comfyui_vram()
        if started and proc is not None:
            proc.terminate()
