"""Cliente mínimo de la API de ComfyUI (HTTP /prompt + /history + /view).

Los providers de imagen / i2v / upscale lo reutilizan: cargan un workflow en formato
API (JSON exportado con "Save (API Format)"), sobreescriben nodos concretos
(prompt, seed, lora, imagen de entrada, ruta de salida) y encolan la ejecución.

Patrón: submit -> wait(history) -> download_outputs. VRAM se libera con free().
"""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any

import httpx

from core.config import Config


class ComfyError(RuntimeError):
    pass


class ComfyClient:
    def __init__(self, cfg: Config, *, client_id: str | None = None):
        self.base_url = cfg.settings["services"]["comfyui"]["base_url"].rstrip("/")
        self.client_id = client_id or uuid.uuid4().hex

    # --- carga y edición del workflow ---
    @staticmethod
    def load_workflow(path: Path) -> dict[str, Any]:
        return json.loads(Path(path).read_text(encoding="utf-8"))

    @staticmethod
    def set_input(workflow: dict, node_id: str, key: str, value: Any) -> None:
        """Sobreescribe workflow[node_id]['inputs'][key] = value."""
        node = workflow.get(str(node_id))
        if node is None:
            raise ComfyError(f"Nodo '{node_id}' no existe en el workflow.")
        node.setdefault("inputs", {})[key] = value

    # --- ejecución ---
    def submit(self, workflow: dict) -> str:
        with httpx.Client(timeout=30) as c:
            r = c.post(f"{self.base_url}/prompt", json={"prompt": workflow, "client_id": self.client_id})
            r.raise_for_status()
            data = r.json()
        prompt_id = data.get("prompt_id")
        if not prompt_id:
            raise ComfyError(f"ComfyUI no devolvió prompt_id: {data}")
        return prompt_id

    def wait(self, prompt_id: str, *, timeout: float = 1800, poll: float = 1.5) -> dict:
        deadline = time.monotonic() + timeout
        with httpx.Client(timeout=30) as c:
            while True:
                r = c.get(f"{self.base_url}/history/{prompt_id}")
                r.raise_for_status()
                hist = r.json()
                if prompt_id in hist:
                    entry = hist[prompt_id]
                    status = entry.get("status", {})
                    if status.get("status_str") == "error":
                        raise ComfyError(f"ComfyUI falló: {status}")
                    return entry
                if time.monotonic() > deadline:
                    raise ComfyError(f"Timeout esperando ComfyUI (prompt {prompt_id}).")
                time.sleep(poll)

    def download_outputs(self, history_entry: dict, out_path: Path) -> Path:
        """Descarga la primera salida (imagen o video) al out_path indicado."""
        out_path.parent.mkdir(parents=True, exist_ok=True)
        outputs = history_entry.get("outputs", {})
        for node_out in outputs.values():
            for key in ("images", "gifs", "videos"):
                for item in node_out.get(key, []):
                    params = {
                        "filename": item["filename"],
                        "subfolder": item.get("subfolder", ""),
                        "type": item.get("type", "output"),
                    }
                    with httpx.Client(timeout=120) as c:
                        r = c.get(f"{self.base_url}/view", params=params)
                        r.raise_for_status()
                        out_path.write_bytes(r.content)
                    return out_path
        raise ComfyError("El workflow no produjo salidas descargables.")

    def run(self, workflow_path: Path, overrides: dict[str, dict[str, Any]], out_path: Path) -> Path:
        """Atajo: carga + aplica overrides {node_id: {key: value}} + ejecuta + descarga."""
        wf = self.load_workflow(workflow_path)
        for node_id, kv in overrides.items():
            for key, value in kv.items():
                self.set_input(wf, node_id, key, value)
        entry = self.wait(self.submit(wf))
        return self.download_outputs(entry, out_path)

    def free(self) -> None:
        try:
            with httpx.Client(timeout=10) as c:
                c.post(f"{self.base_url}/free", json={"unload_models": True, "free_memory": True})
        except Exception:
            pass
