# SOP: Publicar / exportar

## Objetivo
Derivar variantes (1:1, 16:9), generar metadata/SEO por plataforma y publicar (YouTube) o
exportar paquete para subida manual (TikTok/IG/FB por la auditoría de la API de TikTok).

## Inputs
- `slug` con master aprobado (G4). Credenciales YouTube en `credentials.json`/`token.json` (Fase 3).

## Precheck
Revisar `docs/errores-resueltos.md`. Confirmar privacidad de YouTube en `providers.yaml` (private).

## Tools
1. `python -m tools.publish --slug {slug}` → `publish/{platform}/{video, metadata.json, caption.txt}`.

## Outputs
- YouTube: subida privada (revisar antes de hacer público) con `remote_id`/`post_url`.
- TikTok/IG/FB: paquete listo para subir a mano.

## Edge cases
- Sin credenciales YouTube → cae a `manual_export` para esa plataforma.
- TikTok: sin auditoría aprobada los posts son privados (SELF_ONLY); por eso export manual.
