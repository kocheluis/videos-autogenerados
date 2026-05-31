"""Tool WAT: genera un reporte HTML visual del proceso completo de un proyecto.

Muestra, etapa por etapa, los INPUTS y OUTPUTS reales (brief, guion, paleta, character
sheet, keyframes, audio, subtítulos, video final) usando los artefactos en assets/{slug}/.
El HTML se guarda en assets/{slug}/report.html con rutas relativas (se abre en el navegador).

Uso: python -m tools.build_report --slug <slug>
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

from core.pipeline.context import ProjectContext
from core.pipeline.state_machine import STAGES
from tools._common import EXIT_ERROR, emit

CSS = """
:root { --bg:#1c1714; --card:#2a2320; --ink:#f3e9dd; --muted:#b9a892; --accent:#d8a86a; --line:#3c322c; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--ink); font:15px/1.6 system-ui,Segoe UI,sans-serif; }
.wrap { max-width:1100px; margin:0 auto; padding:28px 20px 80px; }
h1 { font-size:26px; margin:0 0 4px; }
h2 { font-size:19px; margin:0 0 12px; color:var(--accent); }
.sub { color:var(--muted); margin:0 0 22px; }
.badges { display:flex; flex-wrap:wrap; gap:8px; margin:14px 0 26px; }
.badge { padding:4px 10px; border-radius:999px; font-size:12px; border:1px solid var(--line); background:var(--card); }
.badge.ok { border-color:#4c7a4c; color:#bfe3bf; }
.badge.pend { color:var(--muted); }
.card { background:var(--card); border:1px solid var(--line); border-radius:14px; padding:20px; margin:0 0 20px; }
.io { display:grid; grid-template-columns:1fr 2fr; gap:18px; }
@media(max-width:720px){ .io{ grid-template-columns:1fr; } }
.io .lbl { font-size:12px; text-transform:uppercase; letter-spacing:.08em; color:var(--muted); margin:0 0 6px; }
.box { background:#221c19; border:1px solid var(--line); border-radius:10px; padding:12px; }
table { width:100%; border-collapse:collapse; font-size:13.5px; }
th,td { text-align:left; padding:7px 9px; border-bottom:1px solid var(--line); vertical-align:top; }
th { color:var(--muted); font-weight:600; }
.swatches { display:flex; gap:8px; flex-wrap:wrap; }
.sw { width:54px; height:54px; border-radius:8px; border:1px solid var(--line); position:relative; }
.sw span { position:absolute; bottom:2px; left:0; right:0; text-align:center; font-size:9px; color:#000a; background:#fff8; }
.grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(150px,1fr)); gap:12px; }
.shot { background:#221c19; border:1px solid var(--line); border-radius:10px; overflow:hidden; }
.shot img { width:100%; display:block; aspect-ratio:9/16; object-fit:cover; }
.shot .cap { padding:8px; font-size:12px; color:var(--muted); }
.sheet { max-width:280px; border-radius:12px; border:1px solid var(--line); }
audio,video { width:100%; }
video { border-radius:12px; max-width:340px; }
.pending { color:var(--muted); font-style:italic; }
.flow { font-size:13px; color:var(--muted); }
code { background:#0003; padding:1px 5px; border-radius:5px; }
"""


def _read_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _esc(x) -> str:
    return html.escape(str(x))


def _card(title: str, inp_html: str, out_html: str) -> str:
    return (
        f'<div class="card"><h2>{title}</h2><div class="io">'
        f'<div><div class="lbl">Input</div><div class="box">{inp_html}</div></div>'
        f'<div><div class="lbl">Output</div><div class="box">{out_html}</div></div>'
        f"</div></div>"
    )


def build(ctx: ProjectContext) -> Path:
    state = ctx.load_state()
    brief = _read_json(ctx.root / "brief.json") or {}
    script = _read_json(ctx.script_dir / "script.json") or {}
    bible = _read_json(ctx.bible_dir / "bible.json") or {}
    caps = _read_json(ctx.subtitles_dir / "captions.json") or {}

    # Badges de estado por etapa
    approvals = state.get("approvals", {})
    badges = []
    for s in STAGES:
        done = state.get("stage") and STAGES.index(s) <= [st.key for st in STAGES].index(state["stage"])
        cls = "ok" if done else "pend"
        badges.append(f'<span class="badge {cls}">{_esc(s.key)}</span>')
    badges_html = '<div class="badges">' + "".join(badges) + "</div>"

    # 1. Brief
    b_in = f'Tema: <code>{_esc(brief.get("topic",""))}</code>'
    b_out = (
        f'<b>Audiencia:</b> {_esc(brief.get("audience",""))}<br>'
        f'<b>Plataformas:</b> {_esc(", ".join(brief.get("platforms",[])))}<br>'
        f'<b>Duración objetivo:</b> {_esc(brief.get("target_duration_s",""))} s'
    )
    c1 = _card("1 · Brief", b_in, b_out)

    # 2. Guion
    scenes = script.get("scenes", [])
    rows = "".join(
        f"<tr><td>{_esc(s.get('idx'))}</td><td>{_esc(s.get('narration_text',''))}</td>"
        f"<td>{_esc(s.get('image_prompt',''))}</td><td>{_esc(s.get('motion_preset',''))}</td></tr>"
        for s in scenes
    )
    g_out = (
        f'<b>{_esc(script.get("title",""))}</b><br><i>{_esc(script.get("hook",""))}</i>'
        f'<table><tr><th>#</th><th>Narración</th><th>Prompt visual</th><th>Movimiento</th></tr>{rows}</table>'
        if scenes else '<span class="pending">pendiente</span>'
    )
    c2 = _card(f"2 · Guion (LLM) — {len(scenes)} escenas", "Brief + preset de estilo", g_out)

    # 3. Bible
    palette = bible.get("palette", [])
    sw = "".join(f'<div class="sw" style="background:{_esc(c)}"><span>{_esc(c)}</span></div>' for c in palette)
    sheet = ""
    if (ctx.bible_dir / "character_sheet.png").exists():
        sheet = '<br><img class="sheet" src="bible/character_sheet.png">'
    bib_out = (f'<div class="swatches">{sw}</div>{sheet}' if (palette or sheet) else '<span class="pending">pendiente</span>')
    c3 = _card("3 · Bible / estilo + personaje", "Guion + paleta del preset", bib_out)

    # 4. Keyframes
    shots = []
    for s in scenes:
        idx = s.get("idx")
        img = ctx.scene_dir(idx) / "keyframe.png"
        if img.exists():
            rel = f"scenes/{int(idx):02d}/keyframe.png"
            shots.append(f'<div class="shot"><img src="{rel}"><div class="cap">{_esc(s.get("narration_text",""))[:90]}</div></div>')
    kf_out = (f'<div class="grid">{"".join(shots)}</div>' if shots else '<span class="pending">generando / pendiente</span>')
    c4 = _card(f"4 · Keyframes (SDXL) — {len(shots)}/{len(scenes)}", "Bible + prompt por escena", kf_out)

    # 5. Voz
    has_wav = (ctx.audio_dir / "narration.wav").exists()
    voz_out = '<audio controls src="audio/narration.wav"></audio>' if has_wav else '<span class="pending">pendiente</span>'
    c5 = _card("5 · Voz en off (Kokoro)", "Narración del guion", voz_out)

    # 6. Subtítulos
    words = caps.get("words", [])
    wl = " ".join(f'<span title="{w.get("start")}s">{_esc(w.get("text",""))}</span>' for w in words[:60])
    sub_out = (f"{len(words)} palabras con tiempos:<br>{wl} …" if words else '<span class="pending">pendiente</span>')
    c6 = _card("6 · Subtítulos (faster-whisper)", "Audio + texto", sub_out)

    # 7. Video final
    has_vid = (ctx.render_dir / "master_9x16.mp4").exists()
    vid_out = '<video controls src="render/master_9x16.mp4"></video>' if has_vid else '<span class="pending">pendiente (render)</span>'
    c7 = _card("7 · Video final (Remotion)", "Clips + voz + subtítulos", vid_out)

    flow = "Brief → Guion → Bible → Keyframes → (i2v) → Voz → Subtítulos → Render → Publicar"
    doc = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Proceso — {_esc(ctx.slug)}</title><style>{CSS}</style></head>
<body><div class="wrap">
<h1>🧶 Proceso de generación — {_esc(ctx.slug)}</h1>
<p class="sub">Etapa actual: <code>{_esc(state.get('stage'))}</code> · <span class="flow">{_esc(flow)}</span></p>
{badges_html}
{c1}{c2}{c3}{c4}{c5}{c6}{c7}
</div></body></html>"""

    out = ctx.root / "report.html"
    out.write_text(doc, encoding="utf-8")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Genera el reporte HTML visual del proceso.")
    ap.add_argument("--slug", required=True)
    args = ap.parse_args()
    ctx = ProjectContext(slug=args.slug)
    if not ctx.state_path.exists():
        emit({"ok": False, "error": "not_found", "slug": args.slug})
        raise SystemExit(EXIT_ERROR)
    out = build(ctx)
    emit({"ok": True, "report": str(out)})


if __name__ == "__main__":
    main()
