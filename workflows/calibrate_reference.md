# SOP: Calibrar estilo desde un video de referencia (Paso 0)

## Objetivo
Extraer parámetros de ESTILO (no activos) de un video de referencia y generar el preset
`config/style_presets/{name}.yaml` que guía al pipeline (formato, ritmo, paleta, captions, voz).

## Inputs requeridos
- Ruta a un video de referencia `.mp4`.
- `name` del preset (default `parenting_primerizos`).
- FFmpeg/ffprobe en PATH; deps del analizador instaladas (`pip install -e .`).

## Precheck obligatorio
1. Revisar `docs/errores-resueltos.md` (entradas de `tools/analyze_reference`).
2. Confirmar que el video existe y es 9:16.

## Secuencia de tools
1. `python -m tools.analyze_reference "{ruta_video}" --name {name}`
   - Produce/actualiza `config/style_presets/{name}.yaml` con: formato (aspect/fps/duración),
     pacing (cortes, duración de toma → duración de clip i2v), paleta dominante (k-means),
     estilo de captions y notas de voz.

## Outputs esperados
`config/style_presets/{name}.yaml`.

## Edge cases
- Falta FFmpeg → exit 1 con mensaje claro (instalar FFmpeg).
- El pacing por cortes duros puede subestimar escenas (la animación i2v no dispara cortes);
  la granularidad real de escenas la define el guion, no este preset.
- **Legal:** el preset captura solo parámetros de estilo; NO copia activos. La voz se clona
  desde grabación propia/licenciada (nunca del video ajeno).
