# SOP: Generar guion (G1)

## Objetivo
Producir el guion estructurado (`script.json`: title, hook, scenes[]) en español.

## Inputs
- `slug` de un proyecto creado (`new_project`); brief + preset en `state.json`.
- Ollama corriendo con `qwen2.5:14b` (o `VAUTOGEN_LLM_MODEL` para pruebas).

## Precheck
Revisar `docs/errores-resueltos.md` (entrada 001: Ollama 404 = modelo no descargado).

## Tools
1. `python -m tools.generate_script --slug {slug}` → `script/script.json` + `narration_full.txt`.

## Compuerta
🚦 **G1 (guion).** Mostrar el guion. Esperar `approve_gate --slug {slug} --gate script`.

## Edge cases
- exit 1 `HTTPStatusError 404` → `ollama pull qwen2.5:14b-instruct-q4_K_M`.
- exit 1 `ValidationError` → el LLM devolvió JSON inválido; reintentar o bajar temperatura.
