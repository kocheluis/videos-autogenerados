"""LLM local vía Ollama (Qwen2.5-14B por defecto). Genera guion/bible/metadata.

`keep_alive: 0` hace que el modelo se descargue de VRAM apenas responde, clave para
no competir con ComfyUI/Whisper en 12 GB.
"""

from __future__ import annotations

import json
import os
from typing import Any

import httpx

from core.config import Config
from core.providers.base import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(self, *, options: dict[str, Any], cfg: Config):
        self.cfg = cfg
        self.options = options
        svc = cfg.settings["services"]["ollama"]
        self.base_url = svc["base_url"].rstrip("/")
        self.keep_alive = svc.get("keep_alive", 0)
        # Override por entorno (útil para pruebas con un modelo más liviano ya descargado).
        self.model = os.environ.get("VAUTOGEN_LLM_MODEL") or options.get(
            "model", "qwen2.5:14b-instruct-q4_K_M"
        )
        self.temperature = options.get("temperature", 0.7)

    def _generate(self, prompt: str, system: str | None, fmt: str | None) -> str:
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": self.keep_alive,
            "options": {"temperature": self.temperature},
        }
        if system:
            payload["system"] = system
        if fmt:
            payload["format"] = fmt
        with httpx.Client(timeout=600) as client:
            resp = client.post(f"{self.base_url}/api/generate", json=payload)
            resp.raise_for_status()
            return resp.json()["response"]

    def generate_text(self, prompt: str, *, system: str | None = None) -> str:
        return self._generate(prompt, system, fmt=None)

    def generate_json(
        self, prompt: str, *, system: str | None = None, schema: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        # Ollama acepta format="json" o un JSON Schema como `format`.
        fmt: Any = schema if schema else "json"
        raw = self._generate(prompt, system, fmt=fmt)
        return json.loads(raw)
