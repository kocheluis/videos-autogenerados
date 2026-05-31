"""Factory que instancia el provider correcto según `config/providers.yaml`.

Mapea (capability, provider_name) -> "modulo:Clase" y lo importa de forma perezosa,
de modo que el núcleo se puede importar sin tener instaladas las dependencias pesadas
de ML (torch, TTS, whisper). El import real ocurre al pedir el provider.
"""

from __future__ import annotations

import importlib
from typing import Any

from core.config import Config, load_config

# capability -> { provider_name -> "module:Class" }
_REGISTRY: dict[str, dict[str, str]] = {
    "llm": {
        "ollama": "core.providers.llm.ollama_provider:OllamaProvider",
    },
    "image": {
        # SDXL primario (OpenRAIL++, comercial); Flux.1-schnell alternativa Apache.
        "comfyui_sdxl": "core.providers.image.comfyui_sdxl:ComfyUISDXLProvider",
        "comfyui_flux_schnell": "core.providers.image.comfyui_flux_schnell:ComfyUIFluxSchnellProvider",
    },
    "i2v": {
        "comfyui_ltx": "core.providers.i2v.comfyui_ltx:ComfyUILTXProvider",
        "comfyui_wan": "core.providers.i2v.comfyui_wan:ComfyUIWanProvider",
    },
    "upscale": {
        "realesrgan": "core.providers.upscale.realesrgan_provider:RealESRGANProvider",
    },
    "tts": {
        # Solo licencias comerciales (XTTS queda PROHIBIDO por su licencia CPML).
        "kokoro": "core.providers.tts.kokoro_provider:KokoroProvider",
        "chatterbox": "core.providers.tts.chatterbox_provider:ChatterboxProvider",
        "piper": "core.providers.tts.piper_provider:PiperProvider",
    },
    "asr": {
        "faster_whisper": "core.providers.asr.faster_whisper_provider:FasterWhisperProvider",
    },
    "publish": {
        "youtube_api": "core.providers.publish.youtube_provider:YouTubeProvider",
        "manual_export": "core.providers.publish.manual_export_provider:ManualExportProvider",
    },
}


def _import_target(target: str) -> type:
    module_path, _, class_name = target.partition(":")
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def get_provider(capability: str, *, name: str | None = None, cfg: Config | None = None) -> Any:
    """Instancia el provider de `capability`.

    Si `name` es None, se toma de providers.yaml[capability]['provider'].
    La sub-configuración del provider (providers.yaml[capability][name]) se pasa al
    constructor como `options`.
    """
    cfg = cfg or load_config()
    section = cfg.providers.get(capability, {})
    provider_name = name or section.get("provider")
    if provider_name is None:
        raise KeyError(f"No hay 'provider' configurado para la capacidad '{capability}'.")

    if capability not in _REGISTRY or provider_name not in _REGISTRY[capability]:
        raise KeyError(
            f"Provider '{provider_name}' no registrado para '{capability}'. "
            f"Disponibles: {sorted(_REGISTRY.get(capability, {}))}"
        )

    options = section.get(provider_name, {}) if isinstance(section, dict) else {}
    klass = _import_target(_REGISTRY[capability][provider_name])
    return klass(options=options, cfg=cfg)


def available(capability: str) -> list[str]:
    return sorted(_REGISTRY.get(capability, {}))
