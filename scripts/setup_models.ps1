# setup_models.ps1 — Descarga/instala los modelos locales (Fase 0).
# RTX 3080 Ti (12 GB). Ejecutar por SECCIONES, revisando espacio en disco (cada modelo
# pesa varios GB). Requiere: venv ML (Python 3.11), git, y Ollama instalado.
#
# IMPORTANTE: este script NO se corre entero a ciegas — está pensado para revisar y
# ejecutar paso a paso. Descomenta lo que necesites.

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Models = Join-Path $Root "models_cache"
New-Item -ItemType Directory -Force -Path $Models | Out-Null

Write-Host "=== 1) LLM (Ollama) ===" -ForegroundColor Cyan
# ollama pull qwen2.5:14b-instruct-q4_K_M
# ollama pull llama3.1:8b-instruct-q4_K_M   # fallback

Write-Host "=== 2) ComfyUI ===" -ForegroundColor Cyan
$Comfy = Join-Path $Root "third_party\ComfyUI"
if (-not (Test-Path $Comfy)) {
    # git clone https://github.com/comfyanonymous/ComfyUI $Comfy
    # En $Comfy: python -m venv .venv ; .\.venv\Scripts\pip install -r requirements.txt
    # Instalar PyTorch CUDA 12.x:  pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
    Write-Host "  (pendiente) clona ComfyUI en $Comfy"
}
# Custom nodes recomendados (ComfyUI-Manager): PuLID, IPAdapter_plus, ControlNet aux,
#   LTX-Video, ComfyUI_essentials, RealESRGAN/UltimateSDUpscale.

Write-Host "=== 3) Checkpoints de imagen (Flux primario, SDXL fallback) ===" -ForegroundColor Cyan
# Flux.1-dev fp8  -> ComfyUI/models/unet  (o checkpoints, según nodo)
# LoRA de afieltrado/crochet -> ComfyUI/models/loras
# PuLID + EVA-CLIP -> según nodo PuLID
# SDXL base 1.0 + InstantID (fallback) -> ComfyUI/models/checkpoints

Write-Host "=== 4) Image-to-video ===" -ForegroundColor Cyan
# LTX-Video 2B -> ComfyUI/models/checkpoints (o el path del nodo LTX)
# (fallback) Wan 2.2 TI2V-5B

Write-Host "=== 5) Upscale ===" -ForegroundColor Cyan
# RealESRGAN_x4plus / 4x-UltraSharp -> ComfyUI/models/upscale_models

Write-Host "=== 6) TTS / ASR (venv ML) ===" -ForegroundColor Cyan
# pip install TTS faster-whisper
# XTTS v2 se descarga al primer uso; faster-whisper 'medium' también.

Write-Host "=== 7) Remotion (render) ===" -ForegroundColor Cyan
$Remotion = Join-Path $Root "render"
if (-not (Test-Path (Join-Path $Remotion "package.json"))) {
    Write-Host "  (pendiente) en $Remotion : npm create video@latest -- --blank"
}

Write-Host "Listo. Ahora valida la VRAM con: python scripts/smoke_test.py" -ForegroundColor Green
