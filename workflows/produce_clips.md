# SOP: Producir clips (i2v → upscale → voz → subtítulos)

## Objetivo
Convertir los keyframes aprobados en clips animados con audio y subtítulos listos para render.

## Inputs
- `slug` con keyframes aprobados (G3). LTX-Video, RealESRGAN, Kokoro/Chatterbox, faster-whisper.

## Precheck
Revisar `docs/errores-resueltos.md`. Recordar: i2v es la etapa más cara (~min por clip).

## Tools (en orden)
1. `python -m tools.animate_clips --slug {slug}` → `scenes/NN/clip.mp4` (480-720p).
2. `python -m tools.upscale_clips --slug {slug}` → `scenes/NN/clip_1080.mp4`.
3. `python -m tools.synthesize_voice --slug {slug}` → `audio/narration.wav`.
4. `python -m tools.align_captions --slug {slug}` → `subtitles/captions.{json,srt}`.

## Outputs
Clips 1080, narración WAV y subtítulos word-level.

## Edge cases
- i2v lento/inviable en 12 GB → bajar resolución de generación o evaluar híbrido cloud (Fase 4).
- Clonación de voz sin `speaker_wav` → Kokoro usa voz base; Chatterbox requiere referencia.
- Subtítulos desalineados → revisar que `narration_full.txt` coincide con el WAV.
