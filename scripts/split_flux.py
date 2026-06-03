"""Separa el all-in-one flux1-schnell-fp8 en UNET + VAE + clip_l + t5xxl.

El CheckpointLoaderSimple crashea con el all-in-one de 17GB en este setup; en cambio
UNETLoader (modelo separado) sí funciona (como con Wan). Reusa el archivo ya descargado,
sin bajar más GB.
"""

from __future__ import annotations

import os

from safetensors import safe_open
from safetensors.torch import save_file

COMFY = r"D:\Jose\Proyecto videos autogenerados\third_party\ComfyUI\models"
SRC = os.path.join(COMFY, "checkpoints", "flux1-schnell-fp8.safetensors")

# (prefijo a quitar, ruta destino)
PARTS = [
    ("model.diffusion_model.", os.path.join(COMFY, "diffusion_models", "flux1-schnell.safetensors")),
    ("vae.", os.path.join(COMFY, "vae", "flux_ae.safetensors")),
    ("text_encoders.clip_l.", os.path.join(COMFY, "clip", "clip_l.safetensors")),
    ("text_encoders.t5xxl.", os.path.join(COMFY, "clip", "t5xxl_fp8_e4m3fn.safetensors")),
]


def main() -> None:
    with safe_open(SRC, framework="pt") as f:
        keys = list(f.keys())
        for prefix, dst in PARTS:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            sub = {k[len(prefix):]: f.get_tensor(k) for k in keys if k.startswith(prefix)}
            if not sub:
                print("SIN claves para", prefix)
                continue
            save_file(sub, dst)
            print("OK", os.path.basename(dst), len(sub), "tensores", round(os.path.getsize(dst) / 1e9, 2), "GB", flush=True)
    print("SPLIT_FLUX_DONE", flush=True)


if __name__ == "__main__":
    main()
