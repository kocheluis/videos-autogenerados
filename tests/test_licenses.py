"""Blindaje de monetización: solo providers con licencia comercial.

Falla si el provider ACTIVO de alguna capa no declara `license.commercial: true`, o si
aparece un modelo de la lista negra (no comercial) en `providers.yaml`.
"""

from __future__ import annotations

import yaml

from core.config import load_config

# Modelos NO comerciales prohibidos para este proyecto (monetización).
BLACKLIST = ["flux1-dev", "flux.1-dev", "flux-dev", "xtts"]

# Capas con estructura {provider: name, name: {...}}. 'publish' es por-plataforma → aparte.
SINGLE_PROVIDER_CAPS = ["llm", "image", "i2v", "upscale", "tts", "asr"]


def test_active_providers_are_commercial():
    cfg = load_config()
    for cap in SINGLE_PROVIDER_CAPS:
        section = cfg.providers.get(cap, {})
        provider = section.get("provider")
        assert provider, f"Capa '{cap}' sin 'provider'."
        opts = section.get(provider, {})
        lic = opts.get("license")
        assert lic is not None, f"{cap}/{provider} no declara 'license'."
        assert lic.get("commercial") is True, f"{cap}/{provider} NO es comercial: {lic}"


def test_no_blacklisted_models():
    cfg = load_config()
    blob = yaml.safe_dump(cfg.providers, allow_unicode=True).lower()
    for bad in BLACKLIST:
        assert bad not in blob, f"Modelo no comercial prohibido presente en providers.yaml: {bad}"


def test_publish_providers_present():
    cfg = load_config()
    pub = cfg.providers.get("publish", {})
    assert "youtube" in pub and pub["youtube"].get("provider") == "youtube_api"
