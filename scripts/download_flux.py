"""Descarga Flux.1-schnell (fp8 all-in-one, Apache 2.0) a checkpoints de ComfyUI en D:.

Calidad muy superior a SDXL base para personajes humanoides con textura de fieltro.
"""

from __future__ import annotations

import os
import shutil

from huggingface_hub import hf_hub_download

COMFY = r"D:\Jose\Proyecto videos autogenerados\third_party\ComfyUI\models"
TMP = os.path.join(COMFY, "_dl_flux")

# (repo, filename, subcarpeta destino)
CANDIDATES = [
    ("Comfy-Org/flux1-schnell", "flux1-schnell-fp8.safetensors", "checkpoints"),
]


def main() -> None:
    for repo, fname, sub in CANDIDATES:
        dst_dir = os.path.join(COMFY, sub)
        os.makedirs(dst_dir, exist_ok=True)
        dst = os.path.join(dst_dir, fname)
        if os.path.exists(dst) and os.path.getsize(dst) > 1_000_000:
            print("YA EXISTE", dst)
            continue
        print("descargando", repo, fname, "...", flush=True)
        p = hf_hub_download(repo, fname, local_dir=TMP)
        shutil.move(p, dst)
        print("OK", dst, round(os.path.getsize(dst) / 1e9, 2), "GB", flush=True)
    shutil.rmtree(TMP, ignore_errors=True)
    print("FLUX_DOWNLOAD_DONE", flush=True)


if __name__ == "__main__":
    main()
