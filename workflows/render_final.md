# SOP: Render final (G4)

## Objetivo
Ensamblar clips + audio + subtítulos + overlays en el master 9:16 con Remotion.

## Inputs
- `slug` con clips_1080, audio y captions listos. Proyecto Remotion en `render/` (Node 24).

## Precheck
Revisar `docs/errores-resueltos.md` (WebGL/headless). `--dry-run` genera solo `props.json`.

## Tools
1. (opcional) `python -m tools.render_video --slug {slug} --dry-run` → valida `props.json`.
2. `python -m tools.render_video --slug {slug}` → `render/master_9x16.mp4` + thumbnail.

## Compuerta
🚦 **G4 (final).** Reproducir el master. Esperar `approve_gate --gate final`.

## Edge cases
- WebGL inestable → `--gl=angle` o fallback MoviePy/FFmpeg para overlays simples.
- npx falla → verificar `npm install` en `render/`.
