# Errores resueltos (log vivo — NUNCA borrar entradas)

Registro de cada error corregido en el proyecto. **Antes de cambiar código**, escanea el
índice y aplica el "check preventivo" de las entradas relevantes. **Tras corregir un error
nuevo**, añade una entrada al final con la plantilla.

## Índice
| # | Fecha | Componente | Síntoma corto |
|---|-------|-----------|----------------|
| 001 | 2026-05-31 | tools/generate_script, ollama_provider | Ollama 404 al generar guion |
| 002 | 2026-05-31 | core/schemas (Scene) | LLM devuelve `motion_preset` vacío/ inválido |
| 003 | 2026-05-31 | core/pipeline/stages/s02_script | Narración demasiado corta (33s vs 150s objetivo) |

---

## 001 — Ollama responde 404 al generar guion
- **Componente(s):** `tools/generate_script.py`, `core/providers/llm/ollama_provider.py`
- **Síntoma:** `httpx.HTTPStatusError: 404 Not Found` en `POST /api/generate`.
- **Causa raíz:** el modelo configurado (`qwen2.5:14b-instruct-q4_K_M`) no estaba descargado en Ollama.
- **Fix:** `ollama pull qwen2.5:14b-instruct-q4_K_M`; documentado en `scripts/setup_models.ps1`.
  Para pruebas rápidas, override con `VAUTOGEN_LLM_MODEL=<modelo ya descargado>`.
- **Check preventivo:** `python -m tools.smoke_test` y verificar que el modelo aparece en `ollama list`.
- **Archivos:** `tools/generate_script.py`, `scripts/setup_models.ps1`, `config/providers.yaml`

---

## 002 — Escenas con `motion_preset` vacío/ inválido del LLM
- **Componente(s):** `core/schemas.py` (`Scene`)
- **Síntoma:** modelos pequeños devuelven `motion_preset: ""` o una clave inexistente; el i2v
  no encontraría el preset de movimiento.
- **Causa raíz:** el LLM no respeta el enum sugerido en el prompt.
- **Fix:** `field_validator` en `Scene.motion_preset` que cae a `subtle_push_in` si el valor no
  está en `{subtle_push_in, blink_gesture, glow_pulse}`.
- **Check preventivo:** los presets válidos viven en `Bible.motion_presets`; mantener el
  validador sincronizado con esas claves.
- **Archivos:** `core/schemas.py`

---

## 003 — Narración demasiado corta vs. duración objetivo
- **Componente(s):** `core/pipeline/stages/s02_script.py` (`_prompt`)
- **Síntoma:** con 25 escenas, la narración total dio ~33 s / 82 palabras para un objetivo de
  150 s. El video saldría mucho más corto que lo pedido.
- **Causa raíz:** el prompt pedía muchas escenas pero no exigía longitud por escena; el LLM
  produjo frases telegráficas (~3 palabras/escena).
- **Fix:** acotar nº de escenas (10-18), fijar ~2.6 palabras/seg, exigir ~N palabras por escena
  y ~`total` palabras de narración en el prompt.
- **Check preventivo:** tras `generate_script`, validar que `len(narration.split()) ≈ target_s*2.6`
  (±20%); si no, regenerar o subir la exigencia de palabras.
- **Archivos:** `core/pipeline/stages/s02_script.py`

---

## Plantilla para nuevas entradas

```
## NNN — <título corto>
- **Componente(s):**
- **Síntoma:**
- **Causa raíz:**
- **Fix:**
- **Check preventivo:**
- **Archivos:**
```
