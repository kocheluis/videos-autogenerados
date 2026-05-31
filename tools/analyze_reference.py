"""Paso 0 — Calibración del video de referencia.

Extrae parámetros de ESTILO (no copia activos) de un video de referencia y genera
un preset en config/style_presets/<name>.yaml que guía al pipeline:
  - formato (aspect, fps, duración)
  - ritmo: nº de cortes y duración media de toma -> nº/duración de clips i2v
  - paleta dominante (k-means) -> colores cálidos del look lana/crochet
  - notas de captions / voz

Sólo depende de FFmpeg/ffprobe (en PATH) + Pillow + numpy + scikit-learn.

Uso:
    python scripts/analyze_reference.py "C:/ruta/al/video.mp4" --name parenting_primerizos
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import yaml
from PIL import Image
from sklearn.cluster import KMeans

ROOT = Path(__file__).resolve().parent.parent


def _require(tool: str) -> str:
    path = shutil.which(tool)
    if not path:
        sys.exit(f"ERROR: no se encontró '{tool}' en el PATH. Instala FFmpeg.")
    return path


def ffprobe_metadata(video: Path) -> dict:
    """Devuelve formato y streams principales con ffprobe."""
    ffprobe = _require("ffprobe")
    cmd = [
        ffprobe, "-v", "error", "-print_format", "json",
        "-show_format", "-show_streams", str(video),
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    data = json.loads(out)
    v = next((s for s in data["streams"] if s["codec_type"] == "video"), {})
    a = next((s for s in data["streams"] if s["codec_type"] == "audio"), {})
    num, _, den = v.get("r_frame_rate", "0/1").partition("/")
    fps = round(float(num) / float(den), 3) if float(den or 0) else None
    return {
        "width": int(v.get("width", 0)),
        "height": int(v.get("height", 0)),
        "fps": fps,
        "duration_s": round(float(data["format"].get("duration", 0)), 2),
        "video_codec": v.get("codec_name"),
        "audio_codec": a.get("codec_name"),
        "audio_channels": a.get("channels"),
        "audio_sample_rate": a.get("sample_rate"),
    }


def detect_cuts(video: Path, threshold: float = 0.3) -> list[float]:
    """Timestamps de cortes duros vía el filtro 'select=scene' de FFmpeg."""
    ffmpeg = _require("ffmpeg")
    cmd = [
        ffmpeg, "-hide_banner", "-i", str(video),
        "-vf", f"select='gt(scene,{threshold})',showinfo", "-f", "null", "-",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    cuts: list[float] = []
    for line in proc.stderr.splitlines():
        if "pts_time:" in line:
            try:
                cuts.append(float(line.split("pts_time:")[1].split()[0]))
            except (IndexError, ValueError):
                pass
    return cuts


def extract_frames(video: Path, out_dir: Path, n: int = 24) -> list[Path]:
    """Extrae ~n fotogramas equiespaciados, escalados a 320px de ancho."""
    ffmpeg = _require("ffmpeg")
    meta = ffprobe_metadata(video)
    dur = meta["duration_s"] or 1
    rate = max(n / dur, 0.01)
    cmd = [
        ffmpeg, "-y", "-loglevel", "error", "-i", str(video),
        "-vf", f"fps={rate},scale=320:-1", str(out_dir / "f_%03d.png"),
    ]
    subprocess.run(cmd, check=True)
    return sorted(out_dir.glob("f_*.png"))


def dominant_palette(frames: list[Path], k: int = 5) -> list[str]:
    """Paleta dominante (k-means) sobre los fotogramas muestreados -> hex."""
    pixels: list[np.ndarray] = []
    for fp in frames:
        img = Image.open(fp).convert("RGB").resize((80, 142))  # ~9:16 reducido
        pixels.append(np.asarray(img).reshape(-1, 3))
    if not pixels:
        return []
    data = np.concatenate(pixels, axis=0).astype(float)
    km = KMeans(n_clusters=k, n_init=4, random_state=0).fit(data)
    # Ordena por tamaño de cluster (color más frecuente primero).
    counts = np.bincount(km.labels_, minlength=k)
    order = np.argsort(counts)[::-1]
    centers = km.cluster_centers_[order].astype(int)
    return ["#{:02x}{:02x}{:02x}".format(*c) for c in centers]


def build_preset(video: Path, name: str) -> dict:
    meta = ffprobe_metadata(video)
    cuts = detect_cuts(video)
    n_shots = len(cuts) + 1
    avg_shot = round((meta["duration_s"] or 0) / max(n_shots, 1), 1)
    with tempfile.TemporaryDirectory() as tmp:
        frames = extract_frames(video, Path(tmp))
        palette = dominant_palette(frames)
    return {
        "name": name,
        "source_file": video.name,
        "format": {
            "width": meta["width"],
            "height": meta["height"],
            "fps": meta["fps"],
            "duration_s": meta["duration_s"],
            "aspect": f"{meta['width']}x{meta['height']}",
        },
        "pacing": {
            "hard_cuts": len(cuts),
            "approx_shots": n_shots,
            "avg_shot_seconds": avg_shot,
            "recommended_clip_seconds": min(max(round(avg_shot), 3), 6),
        },
        "palette": palette,
        "style_lock": {
            "description": (
                "needle-felted wool / crochet amigurumi characters, soft yarn texture, "
                "rosy cheeks, warm cinematic lighting, shallow depth of field, "
                "with glowing 3D anatomical inserts and golden particles"
            ),
        },
        "captions": {"style": "word_by_word", "color": "#ffffff", "outline": True, "position": "lower_center"},
        "audio": {
            "channels": meta["audio_channels"],
            "sample_rate": meta["audio_sample_rate"],
            "note": "Voz en off cálida en es-LA; clonar con XTTS desde voz propia/licenciada.",
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Analiza un video de referencia (Paso 0).")
    ap.add_argument("video", type=Path, help="Ruta al video de referencia (.mp4).")
    ap.add_argument("--name", default="parenting_primerizos", help="Nombre del preset.")
    args = ap.parse_args()

    if not args.video.exists():
        sys.exit(f"ERROR: no existe el archivo {args.video}")

    print(f"Analizando {args.video} ...")
    preset = build_preset(args.video, args.name)

    out_dir = ROOT / "config" / "style_presets"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.name}.yaml"
    with out_path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(preset, fh, allow_unicode=True, sort_keys=False)

    print(f"OK -> {out_path}")
    print(yaml.safe_dump(preset, allow_unicode=True, sort_keys=False))


if __name__ == "__main__":
    main()
