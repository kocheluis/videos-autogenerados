# SOP: Diseño — Style/Character Bible (G2)

## Objetivo
Definir paleta + personajes (anchors, outfit) + `style_lock` (look lana/crochet) y generar
la character sheet ancla para consistencia.

## Inputs
- `slug` con guion aprobado (G1). Preset con paleta.
- ComfyUI corriendo + SDXL/InstantID + LoRA de afieltrado instalados.

## Precheck
Revisar `docs/errores-resueltos.md` (ComfyUI/VRAM). Verificar `python -m tools.smoke_test`.

## Tools
1. `python -m tools.build_bible --slug {slug}` → `bible/bible.json` + `bible/character_sheet.png`.

## Compuerta
🚦 **G2 (diseño).** Mostrar paleta + character sheet. Esperar `approve_gate --gate design`.

## Edge cases
- exit 2 (no cableado) → cablear `comfyui_sdxl` y el workflow `scene_image_sdxl_instantid.json`.
- Personaje "deriva" → subir weight de InstantID o regenerar con la misma seed base.
