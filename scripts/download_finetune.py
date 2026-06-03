"""Descarga un finetune SDXL de alta calidad (humanoide + detalle) a checkpoints de ComfyUI.

Corre en el pipeline SDXL ya probado (CheckpointLoaderSimple), sin los crashes de Flux fp8.
Prueba candidatos comerciales en orden hasta que uno descargue.
"""

from __future__ import annotations

import os
import shutil

from huggingface_hub import hf_hub_download

COMFY = r"D:\Jose\Proyecto videos autogenerados\third_party\ComfyUI\models"
DST_DIR = os.path.join(COMFY, "checkpoints")
TMP = os.path.join(DST_DIR, "_dl_ft")
TARGET = os.path.join(DST_DIR, "sdxl_finetune.safetensors")

CANDIDATES = [
    ("RunDiffusion/Juggernaut-XL-v9", "Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors"),
    ("SG161222/RealVisXL_V5.0", "RealVisXL_V5.0_fp16.safetensors"),
    ("SG161222/RealVisXL_V4.0", "RealVisXL_V4.0.safetensors"),
]


def main() -> None:
    if os.path.exists(TARGET) and os.path.getsize(TARGET) > 1_000_000:
        print("YA EXISTE", TARGET); return
    for repo, fname in CANDIDATES:
        try:
            print("intentando", repo, fname, "...", flush=True)
            p = hf_hub_download(repo, fname, local_dir=TMP)
            shutil.move(p, TARGET)
            shutil.rmtree(TMP, ignore_errors=True)
            print("OK", repo, "->", TARGET, round(os.path.getsize(TARGET) / 1e9, 2), "GB", flush=True)
            print("FINETUNE_DONE", flush=True)
            return
        except Exception as e:
            print("  falló:", type(e).__name__, str(e)[:120], flush=True)
    print("NINGUN CANDIDATO DESCARGÓ", flush=True)


if __name__ == "__main__":
    main()
