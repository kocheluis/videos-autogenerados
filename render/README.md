# Render — proyecto Remotion (TypeScript)

Capa de ensamblaje: combina los clips i2v + audio + subtítulos palabra-por-palabra +
overlays/glow en el master 9:16, y deriva 1:1 y 16:9.

## Inicializar

```powershell
cd render
npm create video@latest -- --blank   # o el template "Hello World"
npm install
```

## Composiciones esperadas (en `src/`)

- `VerticalVideo` (1080×1920) — composición principal. Props (JSON desde `s09_render`):
  `{ title, audio, captions{words[]}, scenes[{idx, clip, duration_s}], width, height, fps }`.
- `Square` (1080×1080) y `Landscape` (1920×1080) — re-render para derivados.

## Componentes sugeridos

- `VideoClip` — reproduce cada `clip_1080.mp4` con su duración.
- `AnimatedCaptions` — resalta palabra por palabra usando `captions.words[].start/end`.
- `GlowOverlay` — partículas/glow cálido para acentos.
- `KenBurnsImage` — fallback (paneo/zoom) para tomas sin i2v.

## Render desde el pipeline

`s09_render` llama:
```
npx remotion render VerticalVideo <out.mp4> --props=<props.json>
```
Usa `--gl=angle` si hay problemas de WebGL en headless; o `--concurrency` para acelerar.
