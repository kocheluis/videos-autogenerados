"""Descarga Wan 2.2 TI2V-5B (repackaged por Comfy-Org) a los models/ de ComfyUI en D:.

Sin duplicar en caché: descarga con local_dir temporal y mueve a su carpeta final.
"""

from __future__ import annotations

import os
import shutil

from huggingface_hub import hf_hub_download

REPO = "Comfy-Org/Wan_2.2_ComfyUI_Repackaged"
COMFY = r"D:\Jose\Proyecto videos autogenerados\third_party\ComfyUI\models"
TMP = os.path.join(COMFY, "_dl_wan")

FILES = {
    "split_files/diffusion_models/wan2.2_ti2v_5B_fp16.safetensors": "diffusion_models",
    "split_files/vae/wan2.2_vae.safetensors": "vae",
    "split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors": "text_encoders",
}


def main() -> None:
    for f, sub in FILES.items():
        dst_dir = os.path.join(COMFY, sub)
        os.makedirs(dst_dir, exist_ok=True)
        dst = os.path.join(dst_dir, os.path.basename(f))
        if os.path.exists(dst) and os.path.getsize(dst) > 1_000_000:
            print("YA EXISTE", dst)
            continue
        print("descargando", f, "...")
        p = hf_hub_download(REPO, f, local_dir=TMP)
        shutil.move(p, dst)
        print("OK", dst, round(os.path.getsize(dst) / 1e9, 2), "GB")
    shutil.rmtree(TMP, ignore_errors=True)
    print("WAN_DOWNLOAD_DONE")


if __name__ == "__main__":
    main()
