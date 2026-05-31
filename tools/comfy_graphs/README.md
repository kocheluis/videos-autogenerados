# Workflows de ComfyUI (formato API)

Exporta cada workflow desde ComfyUI con **"Save (API Format)"** y guárdalo aquí con
estos nombres (los providers los inyectan con prompt/seed/lora/paleta):

- `character_sheet.json` — hoja de personaje (Flux + LoRA afieltrado + PuLID).
- `scene_image_flux_pulid.json` — keyframe por escena (primario).
- `scene_image_sdxl_instantid.json` — keyframe (fallback SDXL + InstantID).
- `scene_i2v_ltx.json` — image-to-video con LTX-Video (480-720p, ~4 s).
- `scene_i2v_wan.json` — i2v con Wan 2.2 TI2V-5B (fallback).
- `upscale_realesrgan.json` — upscale de clip a 1080×1920.

Cada provider en `core/providers/{image,i2v,upscale}/` carga el JSON, reemplaza los
nodos de entrada (texto, seed, imagen, lora) y encola vía `POST {comfyui}/prompt`.

> Puntos de inyección sugeridos: nodo `CLIPTextEncode` (prompt), `KSampler`/`RandomNoise`
> (seed), `LoraLoader` (style_lora), `LoadImage` (keyframe para i2v), nodo de salida
> `SaveImage`/`VHS_VideoCombine` (ruta de salida).
