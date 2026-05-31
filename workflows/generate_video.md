# SOP: Generar un video (maestro, end-to-end)

## Objetivo
Producir 1 Reel vertical (9:16, ~2.5 min) en español, estilo lana/crochet + i2v, desde un
tema hasta el archivo publicado/exportado, pasando por las 4 compuertas de revisión humana.

## Inputs requeridos
- `topic` (tema) y `platforms` (p.ej. `youtube,instagram`).
- Preset de estilo existente (default `parenting_primerizos`; si no, correr `calibrate_reference.md`).
- Modelos instalados (ver `scripts/setup_models.ps1`) y Ollama corriendo.

## Precheck obligatorio
1. Revisar el índice de `docs/errores-resueltos.md` y aplicar los "check preventivo" de las
   entradas que toquen LLM/ComfyUI/i2v/TTS/render.
2. Confirmar entorno: `python -m tools.smoke_test`.

## Secuencia de tools y compuertas

1. **Crear proyecto** → `python -m tools.new_project --topic "{topic}" --platforms {platforms}`
   - Anota el `slug` devuelto. Produce `assets/{slug}/brief.{md,json}`.
2. **Guion** → `python -m tools.generate_script --slug {slug}`
   - Produce `script/script.json`.
   - **🚦 COMPUERTA G1 (guion). DETENER.** Mostrar el guion al usuario. Continuar solo tras
     `python -m tools.approve_gate --slug {slug} --gate script`.
3. **Bible + personajes** → `python -m tools.build_bible --slug {slug}`
   - Produce `bible/bible.json` + `bible/character_sheet.png`.
   - **🚦 COMPUERTA G2 (diseño). DETENER.** Mostrar paleta + character sheet. Esperar
     `approve_gate --gate design`.
4. **Keyframes** → `python -m tools.generate_keyframes --slug {slug}`
   - Produce `scenes/NN/keyframe.png`.
   - **🚦 COMPUERTA G3 (keyframes). DETENER.** Mostrar la grilla de keyframes. Esperar
     `approve_gate --gate images`. ⚠️ Crítico: animar (paso 5) es lo más caro en tiempo; NO
     animar sin aprobar las imágenes.
5. **Producir clips** (ver `produce_clips.md`):
   `animate_clips` → `upscale_clips` → `synthesize_voice` → `align_captions`.
6. **Render** → `python -m tools.render_video --slug {slug}`
   - Produce `render/master_9x16.mp4`.
   - **🚦 COMPUERTA G4 (final). DETENER.** Reproducir el master. Esperar `approve_gate --gate final`.
7. **Publicar** → `python -m tools.publish --slug {slug}`
   - YouTube automático; TikTok/IG/FB → paquete en `publish/{platform}/` para subida manual.

> Alternativa desatendida: `python -m tools.run_batch --slug {slug}` avanza hasta la próxima
> compuerta no aprobada (exit 3). Respeta las 4 compuertas salvo `--auto-approve` (solo pruebas).

## Outputs esperados
`assets/{slug}/render/master_9x16.mp4` + derivados y paquetes en `assets/{slug}/publish/`.

## Edge cases y manejo de fallos
- **exit 2 (no cableado):** falta instalar/cablear un modelo → revisar `scripts/setup_models.ps1`.
- **exit 3 (bloqueado):** la compuerta previa no está aprobada → revisar con `project_status`.
- **CUDA OOM:** liberar VRAM (ComfyUI `/free`) y reintentar; respetar la regla "un modelo a la vez".
- **i2v lento:** normal (~1-2 h/video en 12 GB). Si es inviable, evaluar híbrido cloud (Fase 4).
- **Tras corregir cualquier error nuevo:** añadir entrada en `docs/errores-resueltos.md`.
