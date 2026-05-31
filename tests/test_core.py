"""Pruebas del núcleo que NO requieren GPU ni modelos."""

from __future__ import annotations

from core.config import load_config
from core.pipeline.state_machine import (
    GATE_SCRIPT,
    STAGES,
    gate_for_stage,
    next_stage,
)
from core.schemas import CaptionTrack, Word


def test_config_loads():
    cfg = load_config()
    assert cfg.settings["video"]["master"]["width"] == 1080
    assert cfg.providers["llm"]["provider"] == "ollama"
    assert cfg.vram_budget_mb <= cfg.settings["gpu"]["total_vram_mb"]


def test_stage_order_and_gates():
    assert STAGES[0].key == "s01_brief"
    assert next_stage("s01_brief").key == "s02_script"
    assert next_stage("s10_publish") is None
    assert gate_for_stage("s02_script") == GATE_SCRIPT
    assert gate_for_stage("s05_i2v") is None


def test_caption_srt():
    track = CaptionTrack(words=[Word(text="hola", start=0.0, end=0.4)])
    srt = track.to_srt()
    assert "00:00:00,000 --> 00:00:00,400" in srt
    assert "hola" in srt


def test_registry_resolves_without_heavy_imports():
    # El registry debe poder construir el provider LLM (httpx) sin tocar torch.
    from core.providers.registry import get_provider

    llm = get_provider("llm")
    assert llm.model
