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
| 004 | 2026-05-31 | caché HuggingFace (D:) | `model.bin incomplete` tras mover caché con robocopy (symlinks rotos) |
| 005 | 2026-05-31 | .venv (torch) | ComfyUI requirements degradó torch a CPU (CUDA False) |
| 006 | 2026-05-31 | s09_render (Remotion) | 404/EncodingError: assets en public/{slug}/{slug} (doble) |
| 007 | 2026-06-01 | s08_align / s09_render | Subtítulos desincronizados (captions de un audio viejo) |
| 008 | 2026-06-02 | comfyui_wan / comfy_client / providers.yaml | i2v 400 `value_not_in_list` (modelo no reconocido / nombre erróneo) |

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

## 004 — `model.bin is incomplete` tras mover la caché de HuggingFace
- **Componente(s):** caché HF en `D:\AI\huggingface\hub` (faster-whisper, Kokoro, etc.)
- **Síntoma:** `RuntimeError: File model.bin is incomplete: failed to read a value of size 4 at position 0`.
- **Causa raíz:** la caché HF usa symlinks `snapshots/ → blobs/`. Mover con `robocopy /MOVE`
  rompió los symlinks dejándolos como archivos de **0 bytes** (los blobs con el contenido real
  quedaron intactos). HF ve el archivo "presente" (0 bytes) y no lo re-valida.
- **Fix:** borrar los punteros de 0 bytes bajo `hub\*\snapshots\*` (NO los blobs); al cargar el
  modelo, `huggingface_hub` re-crea el enlace desde el blob existente (sin re-descargar).
  Comando: `Get-ChildItem $hub -Recurse -File | ? {$_.Length -eq 0 -and $_.FullName -like '*\snapshots\*'} | Remove-Item`.
- **Check preventivo:** para mover cachés HF, fijar `HF_HOME` ANTES de descargar, o mover con un
  método que preserve symlinks; tras cualquier mudanza, correr un tool que cargue cada modelo y
  verificar exit 0. `.env` del proyecto fija `HF_HOME`/`HF_HUB_CACHE`/`INSIGHTFACE_HOME`/`TORCH_HOME` a D:.
- **Archivos:** `.env`, cachés en `D:\AI\`

---

## 005 — ComfyUI degradó torch a CPU (CUDA False)
- **Componente(s):** `.venv` compartido (torch), instalación de ComfyUI
- **Síntoma:** tras `pip install -r ComfyUI/requirements.txt`, `torch.cuda.is_available()` pasó a
  False (`torch 2.12.0+cpu`); se perdió la GPU para Kokoro/Whisper/ComfyUI.
- **Causa raíz:** `requirements.txt` de ComfyUI trae `torch` sin pin; pip instaló la rueda CPU
  de PyPI (versión más alta) sobre el build `cu124`.
- **Fix:** `pip uninstall -y torch torchvision torchaudio` y reinstalar desde el índice CUDA:
  `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124`.
- **Check preventivo:** tras instalar deps de ComfyUI o de cualquier custom node, verificar
  `torch.cuda.is_available()`. Idealmente instalar requirements de ComfyUI con `--no-deps`, o
  reinstalar el torch cu124 al final. Considerar un venv separado para ComfyUI si reincide.
- **Archivos:** `.venv`

---

## 006 — Remotion 404 / EncodingError al cargar imágenes
- **Componente(s):** `core/pipeline/stages/s09_render.py`
- **Síntoma:** render Remotion falla con `404 Not Found` y `EncodingError: The source image
  cannot be decoded` para `public/{slug}/scenes/NN/keyframe.png`.
- **Causa raíz:** se copiaban los assets a `render/public/{slug}/{slug}/...` (slug duplicado)
  porque `public_dir` ya incluía el slug y el `rel` lo repetía; `staticFile("{slug}/...")`
  buscaba `public/{slug}/...` (un solo slug) → no existía.
- **Fix:** usar `public_root = render/public` como base y `rel = "{slug}/..."` (un solo slug);
  limpiar solo `public/{slug}` antes de copiar.
- **Check preventivo:** la ruta física `render/public/<rel>` debe coincidir exactamente con
  `staticFile(rel)`. Probar con `--dry-run` y verificar 1 ruta antes del render completo.
- **Archivos:** `core/pipeline/stages/s09_render.py`

---

## 007 — Subtítulos desincronizados / no coinciden con la voz
- **Componente(s):** `core/pipeline/stages/s08_align.py`, `s09_render.py`
- **Síntoma:** los subtítulos del video no son los de la voz y se cortan a la mitad
  (captions hasta 32 s con audio de 65 s, y otro texto).
- **Causa raíz:** se regeneró la voz (s07_tts) DESPUÉS de alinear (s08), dejando
  `captions.json` obsoleto (de una versión anterior, más corta y con otro guion).
- **Fix:** re-ejecutar `align_captions` sobre el audio actual; y **guard de frescura** en
  s09_render que aborta si `captions.json` es más viejo que `narration.wav`.
- **Check preventivo:** respetar el orden s07 (voz) → s08 (subtítulos) → s09 (render).
  El run_batch/UI lo respeta; en ejecución manual, re-alinear tras regenerar la voz.
  Mejora futura: alineación forzada del texto del guion (forced alignment) para subtítulos
  con palabras EXACTAS del guion (el usuario ya tiene `mms-300m-forced-aligner` en caché).
- **Archivos:** `core/pipeline/stages/s08_align.py`, `core/pipeline/stages/s09_render.py`

---

## 008 — i2v Wan: ComfyUI 400 `value_not_in_list` (modelo no encontrado)
- **Componente(s):** `core/providers/i2v/comfyui_wan.py`, `core/services/comfy_client.py`, `config/providers.yaml`
- **Síntoma:** al generar i2v, ComfyUI rechaza el workflow con HTTP 400 `prompt_outputs_failed_validation`
  → `unet_name: 'wan2.2-ti2v-5b.safetensors' not in [...]`.
- **Causa raíz (doble):** (a) los modelos agregados DESPUÉS de arrancar ComfyUI no se reconocen
  hasta refrescar `/object_info`; (b) el `model` en providers.yaml (`wan2.2-ti2v-5b.safetensors`)
  NO coincidía con el archivo real (`wan2.2_ti2v_5B_fp16.safetensors`), y el provider lo sobreescribía.
- **Fix:** `ComfyClient.refresh()` (GET /object_info de los loaders) antes de cada submit; y corregir
  el nombre EXACTO en providers.yaml. `submit()` ahora muestra el cuerpo del 400 para diagnosticar.
- **Check preventivo:** el nombre del modelo en config debe coincidir EXACTO con el archivo en
  ComfyUI/models. Tras añadir modelos, refrescar object_info (el provider ya lo hace).
- **Archivos:** `core/providers/i2v/comfyui_wan.py`, `core/services/comfy_client.py`, `config/providers.yaml`

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
