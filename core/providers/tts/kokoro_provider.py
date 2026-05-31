"""Voz en off con Kokoro (Apache 2.0, COMERCIAL) — ligero (82M), voces en español.

Buena opción por defecto para narración en es: rápido, licencia permisiva, calidad alta
para su tamaño. Para clonar una voz propia, usar Chatterbox (ver chatterbox_provider).

Voces es (lang_code='e'): ef_dora (f), em_alex (m), em_santa (m). Salida a 24 kHz.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.config import Config
from core.providers.base import TTSProvider


class KokoroProvider(TTSProvider):
    def __init__(self, *, options: dict[str, Any], cfg: Config):
        self.cfg = cfg
        self.options = options
        self.voice = options.get("voice", "ef_dora")  # voz española de Kokoro
        self.lang_code = options.get("lang_code", "e")  # 'e' = español
        self.speed = float(options.get("speed", 1.0))
        self.sample_rate = 24000

    def synthesize(self, text: str, *, out_path: Path, speaker_wav: Path | None = None) -> Path:
        # speaker_wav se ignora: Kokoro no clona (usar Chatterbox para clonación).
        import numpy as np
        import soundfile as sf
        from kokoro import KPipeline

        out_path.parent.mkdir(parents=True, exist_ok=True)
        pipeline = KPipeline(lang_code=self.lang_code)

        chunks: list[Any] = []
        for _, _, audio in pipeline(text, voice=self.voice, speed=self.speed):
            arr = audio.detach().cpu().numpy() if hasattr(audio, "detach") else np.asarray(audio)
            chunks.append(arr.astype(np.float32))

        if not chunks:
            raise RuntimeError("Kokoro no generó audio (texto vacío o voz inválida).")

        full = np.concatenate(chunks)
        sf.write(str(out_path), full, self.sample_rate)
        return out_path
