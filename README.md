# Generador de Reels narrativos (self-hosted, WAT, monetizable)

Sistema para generar videos verticales (9:16, 1080×1920, ~2.5 min) en español, estilo
**muñecos de lana afieltrada / crochet** + insertos 3D + subtítulos palabra-por-palabra +
**movimiento image-to-video**, con **revisión humana en 4 compuertas**. 100% open-source y
**solo modelos con licencia comercial**. GPU objetivo: **NVIDIA RTX 3080 Ti (12 GB)**.

Arquitectura: **WAT (Workflows, Agents, Tools)** según `CLAUDE.md`.
Plan completo: `../../.claude/plans/deseo-realizar-un-sistema-luminous-pancake.md`.

## Arquitectura WAT

- **`workflows/`** — SOPs en markdown (orquestación). El agente los lee y ejecuta tools en orden.
- **`tools/`** — scripts Python deterministas, 1 responsabilidad c/u (wrappers delgados sobre `core/`).
- **`core/`** — librería compartida: providers (interfaces local↔cloud), state-machine, gpu_lock, schemas.
- **`docs/errores-resueltos.md`** — log obligatorio de errores (loop de auto-mejora).

```
workflows/   SOPs markdown (generate_video.md = maestro)
tools/       new_project, generate_script, build_bible, generate_keyframes,
             animate_clips, upscale_clips, synthesize_voice, align_captions,
             render_video, publish, project_status, approve_gate, run_batch,
             analyze_reference, smoke_test, comfy_graphs/ (JSON ComfyUI)
core/        config, schemas, providers/, pipeline/ (state_machine, runner, stages s01-s10), services/
config/      settings.yaml, providers.yaml (solo comercial + license:), platforms.yaml, style_presets/
render/      proyecto Remotion (9:16 + captions)
docs/        errores-resueltos.md
assets/{slug}/  salidas por proyecto (state.json + brief/script/bible/scenes/audio/subtitles/render/publish)
```

## Pipeline (etapas y compuertas)

```
new_project → generate_script ─[G1]→ build_bible ─[G2]→ generate_keyframes ─[G3]→
animate_clips → upscale_clips → synthesize_voice → align_captions → render_video ─[G4]→ publish
```

**Regla de GPU:** un solo modelo grande en VRAM a la vez (worker único + `GpuLock` + load→use→unload).

## Stack (solo licencia comercial)

| Capa | Modelo | Licencia |
|---|---|---|
| LLM | Ollama + Qwen2.5-14B | Apache 2.0 |
| Imagen | SDXL + InstantID + LoRA afieltrado (prim.); Flux.1-schnell/Z-Image (alt) | OpenRAIL++ / Apache |
| i2v | LTX-Video (vel.) / Wan 2.2 (calidad) | Community / Apache |
| Upscale | RealESRGAN | BSD |
| TTS | Kokoro (es) / Chatterbox (clonación) | Apache / MIT |
| ASR | faster-whisper | MIT |
| Render | Remotion | gratis individuo/comercial |

> ❌ **Prohibidos por licencia no comercial:** Flux.1-dev, XTTS v2. Blindado en `tests/test_licenses.py`.

## Puesta en marcha

```powershell
py -3.11 -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -e .

# Paso 0: calibrar estilo desde el video de referencia
python -m tools.analyze_reference "C:\ruta\al\video.mp4" --name parenting_primerizos

# Modelos locales (Fase 0): editar y ejecutar scripts/setup_models.ps1, luego:
python -m tools.smoke_test

# Operar el pipeline (sigue workflows/generate_video.md)
python -m tools.new_project --topic "Cómo calmar el llanto del bebé" --platforms youtube,instagram
python -m tools.generate_script --slug <slug>
python -m tools.project_status --slug <slug>
python -m tools.approve_gate --slug <slug> --gate script
```

Exit codes de los tools: `0` OK · `1` error · `2` etapa no cableada · `3` bloqueado por compuerta.

## Estado

- ✅ Paso 0, guion real (Ollama), 4 compuertas, refactor WAT, stack comercial.
- 🚧 Fase 1: cablear providers ComfyUI (SDXL+InstantID, LTX-Video, RealESRGAN), TTS (Kokoro/Chatterbox), Remotion.
