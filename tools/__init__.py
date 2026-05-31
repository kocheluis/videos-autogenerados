"""WAT Layer 3 — Tools: scripts Python deterministas, una responsabilidad por archivo.

Cada tool envuelve una etapa de `core.pipeline.stages` (o el runner), imprime su
resultado como JSON a stdout y usa exit codes explícitos (ver tools._common).
Se invocan desde los SOPs en `workflows/` o a mano: `python -m tools.<nombre> --slug ...`.
"""
