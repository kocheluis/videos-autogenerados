"""GpuLock — garantiza que sólo UNA etapa pesada use la GPU a la vez.

Con 12 GB de VRAM no podemos tener dos modelos grandes residentes simultáneamente
(p.ej. Flux + LTX-Video, u Ollama + Whisper). Toda etapa que toque la GPU debe
ejecutarse dentro de `with gpu_lock(): ...`.

Implementado con un lock de archivo (filelock si está disponible; fallback a un
candado por O_CREAT|O_EXCL) para que funcione incluso entre procesos (worker + UI).
"""

from __future__ import annotations

import os
import time
from contextlib import contextmanager
from pathlib import Path

from core.config import load_config


@contextmanager
def gpu_lock(timeout: float = 3600.0, poll: float = 0.5):
    """Context manager exclusivo para etapas GPU. Bloquea hasta adquirir o expira."""
    cfg = load_config()
    lock_path = Path(cfg.settings["gpu"].get("lock_file", "data/gpu.lock"))
    if not lock_path.is_absolute():
        lock_path = cfg.root / lock_path
    lock_path.parent.mkdir(parents=True, exist_ok=True)

    # Camino preferido: filelock (si está instalado).
    try:
        from filelock import FileLock, Timeout  # type: ignore

        lock = FileLock(str(lock_path) + ".flock")
        try:
            lock.acquire(timeout=timeout)
        except Timeout as exc:  # pragma: no cover
            raise TimeoutError("No se pudo adquirir el GpuLock a tiempo.") from exc
        try:
            yield
        finally:
            lock.release()
        return
    except ImportError:
        pass

    # Fallback portable sin dependencias: candado por creación exclusiva.
    deadline = time.monotonic() + timeout
    fd = None
    while fd is None:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_RDWR)
        except FileExistsError:
            if time.monotonic() > deadline:  # pragma: no cover
                raise TimeoutError("No se pudo adquirir el GpuLock a tiempo.")
            time.sleep(poll)
    try:
        yield
    finally:
        os.close(fd)
        try:
            os.unlink(lock_path)
        except OSError:  # pragma: no cover
            pass
