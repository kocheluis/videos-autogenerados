"""smoke_test.py — valida el entorno y la disciplina de VRAM (Fase 0).

Comprueba, sin depender de que TODO esté instalado:
  1. GPU visible y VRAM total (nvidia-smi).
  2. FFmpeg/ffprobe en PATH.
  3. (si está) torch.cuda disponible.
  4. (si están) que Ollama/ComfyUI responden.
  5. Imprime recordatorio del presupuesto de VRAM y del criterio i2v.

Cuando los modelos estén instalados, se ampliará para cargar→generar→descargar cada uno
midiendo el pico de VRAM y el tiempo de un clip i2v de 4 s (criterio de viabilidad).
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _ok(msg: str) -> None: print(f"  [OK]   {msg}")
def _warn(msg: str) -> None: print(f"  [WARN] {msg}")


def check_gpu() -> None:
    print("== GPU ==")
    smi = shutil.which("nvidia-smi")
    if not smi:
        _warn("nvidia-smi no encontrado.")
        return
    out = subprocess.run(
        [smi, "--query-gpu=name,memory.total,memory.used,driver_version", "--format=csv,noheader"],
        capture_output=True, text=True,
    ).stdout.strip()
    _ok(out)


def check_ffmpeg() -> None:
    print("== FFmpeg ==")
    for tool in ("ffmpeg", "ffprobe"):
        _ok(tool) if shutil.which(tool) else _warn(f"{tool} no encontrado")


def check_torch() -> None:
    print("== PyTorch / CUDA ==")
    try:
        import torch  # type: ignore

        if torch.cuda.is_available():
            _ok(f"torch {torch.__version__} | CUDA {torch.version.cuda} | {torch.cuda.get_device_name(0)}")
        else:
            _warn(f"torch {torch.__version__} sin CUDA disponible")
    except ImportError:
        _warn("torch no instalado (se instala en el venv ML / ComfyUI)")


def check_services() -> None:
    print("== Servicios locales ==")
    try:
        import httpx  # type: ignore

        from core.config import load_config

        cfg = load_config()
        for name, url in [
            ("ollama", cfg.settings["services"]["ollama"]["base_url"]),
            ("comfyui", cfg.settings["services"]["comfyui"]["base_url"]),
        ]:
            try:
                httpx.get(url, timeout=1.5)
                _ok(f"{name} responde en {url}")
            except Exception:
                _warn(f"{name} no responde en {url} (arráncalo cuando toque su fase)")
    except ImportError:
        _warn("httpx/core no disponibles (pip install -e .)")


def check_budget() -> None:
    print("== Presupuesto de VRAM ==")
    try:
        from core.config import load_config

        cfg = load_config()
        _ok(f"Objetivo por etapa: < {cfg.vram_budget_mb} MB (un modelo grande a la vez)")
        _ok("Criterio i2v: medir tiempo de un clip de 4 s; si es prohibitivo, evaluar híbrido cloud.")
    except Exception as exc:  # pragma: no cover
        _warn(f"No se pudo leer la config: {exc}")


def main() -> None:
    print("== SMOKE TEST — entorno y disciplina de VRAM ==\n")
    check_gpu()
    check_ffmpeg()
    check_torch()
    check_services()
    check_budget()
    print("\nListo. Revisa los [WARN]: indican lo que falta instalar/arrancar para la Fase 1.")


if __name__ == "__main__":
    main()
