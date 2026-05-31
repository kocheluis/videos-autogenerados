"""Helpers compartidos por los tools WAT: salida JSON y exit codes deterministas.

Exit codes (contrato para el agente/SOP):
  0  OK
  1  error inesperado (conexión, validación, etc.)
  2  etapa no cableada (NotImplementedError) — falta instalar/cablear un modelo
  3  bloqueado por una compuerta de revisión humana
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from core.pipeline.context import ProjectContext
from core.pipeline.stages import get_runner

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_NOT_WIRED = 2
EXIT_BLOCKED = 3


def emit(obj: Any) -> None:
    """Imprime un objeto como JSON (la 'salida' que el agente/SOP parsea)."""
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def execute_stage(stage_key: str, ctx: ProjectContext, **kwargs: Any) -> None:
    """Ejecuta una etapa core y termina el proceso con el exit code adecuado."""
    try:
        result = get_runner(stage_key)(ctx, **kwargs)
    except NotImplementedError as exc:
        emit({"ok": False, "stage": stage_key, "error": "not_wired", "detail": str(exc)})
        sys.exit(EXIT_NOT_WIRED)
    except Exception as exc:  # conexión a Ollama/ComfyUI, validación Pydantic, etc.
        emit({"ok": False, "stage": stage_key, "error": type(exc).__name__, "detail": str(exc)})
        sys.exit(EXIT_ERROR)
    payload = result if isinstance(result, dict) else {"result": result}
    emit({"ok": True, **payload})
    sys.exit(EXIT_OK)


def simple_stage_tool(stage_key: str, description: str) -> None:
    """CLI estándar para una etapa que solo necesita --slug."""
    ap = argparse.ArgumentParser(description=description)
    ap.add_argument("--slug", required=True, help="Slug del proyecto.")
    args = ap.parse_args()
    execute_stage(stage_key, ProjectContext(slug=args.slug))
