# Workflows (SOPs) — WAT Layer 1

Procedimientos en lenguaje claro que el **agente** lee y ejecuta llamando a los **tools**
de `tools/`. La lógica de orquestación vive AQUÍ, no en prompts ni en código disperso.

## Índice de SOPs

| SOP | Objetivo |
|---|---|
| [generate_video.md](generate_video.md) | **Maestro** — de un tema a un video publicado, con las 4 compuertas |
| [calibrate_reference.md](calibrate_reference.md) | Paso 0 — calibrar el estilo desde un video de referencia |
| [generate_script.md](generate_script.md) | Guion (G1) |
| [design_bible.md](design_bible.md) | Bible + personajes (G2) |
| [generate_keyframes.md](generate_keyframes.md) | Keyframes por escena (G3) |
| [produce_clips.md](produce_clips.md) | i2v → upscale → voz → subtítulos |
| [render_final.md](render_final.md) | Render del master 9:16 (G4) |
| [publish_video.md](publish_video.md) | Derivar variantes y publicar/exportar |

## Reglas (de CLAUDE.md)

- **Precheck obligatorio** en cada SOP: revisar `docs/errores-resueltos.md` y aplicar los
  "check preventivo" de las entradas relevantes; buscar tools existentes antes de crear nuevos.
- **Tras corregir un error nuevo**: añadir entrada en `docs/errores-resueltos.md`.
- **No crear/sobrescribir SOPs sin permiso del usuario.**

## Exit codes de los tools

`0` OK · `1` error · `2` etapa no cableada (falta modelo) · `3` bloqueado por compuerta.
