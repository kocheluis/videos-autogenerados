# SOP: Keyframes por escena (G3)

## Objetivo
Generar 1 keyframe 1080×1920 por escena, consistente en personaje/paleta/style_lock.

## Inputs
- `slug` con bible aprobado (G2). ComfyUI + SDXL/InstantID.

## Precheck
Revisar `docs/errores-resueltos.md`. La VRAM se serializa (GpuLock) automáticamente.

## Tools
1. `python -m tools.generate_keyframes --slug {slug}` → `scenes/NN/keyframe.png`.

## Compuerta
🚦 **G3 (keyframes).** Mostrar la grilla. Esperar `approve_gate --gate images`.
⚠️ Animar (i2v) es lo más caro: NO continuar sin aprobar las imágenes aquí.

## Edge cases
- Una escena sale mal → regenerar solo esa (futuro `--scene N`) con misma seed/prompt ajustado.
- CUDA OOM → ComfyUI `--medvram` + liberar VRAM entre lotes.
