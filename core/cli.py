"""CLI del sistema (Fase 1, operación manual con compuertas).

Ejemplos:
    vautogen new "Cómo cambiar un pañal sin estrés" --platforms youtube,instagram
    vautogen status padres-...-slug
    vautogen advance <slug>            # corre la siguiente etapa (se detiene en compuertas)
    vautogen approve <slug> script     # aprueba una compuerta (script|design|images|final)
    vautogen run <slug> s02_script     # corre una etapa puntual
"""

from __future__ import annotations

import json

import typer
from rich import print as rprint
from rich.table import Table

from core.pipeline.context import ProjectContext, slugify
from core.pipeline.runner import advance as advance_runner
from core.pipeline.runner import approve as approve_gate
from core.pipeline.runner import blocked_gate
from core.pipeline.stages import get_runner
from core.pipeline.state_machine import STAGES
from core.schemas import Brief

app = typer.Typer(add_completion=False, help="Generador de Reels narrativos self-hosted.")


@app.command()
def new(
    topic: str,
    platforms: str = typer.Option("youtube", help="Lista separada por comas."),
    style_preset: str = typer.Option("parenting_primerizos"),
    duration: int = typer.Option(150, help="Duración objetivo en segundos."),
):
    """Crea un proyecto y corre s01_brief."""
    brief = Brief(
        topic=topic,
        platforms=[p.strip() for p in platforms.split(",") if p.strip()],  # type: ignore[arg-type]
        style_preset=style_preset,
        target_duration_s=duration,
    )
    ctx = ProjectContext(slug=slugify(topic))
    result = get_runner("s01_brief")(ctx, brief=brief)
    rprint(f"[green]Proyecto creado:[/green] [bold]{ctx.slug}[/bold]")
    rprint(result)


@app.command()
def status(slug: str):
    """Muestra el estado y la posición en el pipeline."""
    ctx = ProjectContext(slug=slug)
    state = ctx.load_state()
    table = Table(title=f"Estado — {slug}")
    table.add_column("Etapa"); table.add_column("Compuerta"); table.add_column("Aprobada")
    approvals = state.get("approvals", {})
    for s in STAGES:
        gate = s.gate_after or "—"
        ok = "✅" if (s.gate_after and approvals.get(s.gate_after)) else ("—" if not s.gate_after else "⏳")
        marker = "➡️ " if state.get("stage") == s.key else "  "
        table.add_row(marker + s.key, gate, ok)
    rprint(table)
    rprint(f"Etapa actual: [bold]{state.get('stage')}[/bold]")
    g = blocked_gate(ctx)
    if g:
        rprint(f"[yellow]Bloqueado en compuerta:[/yellow] {g}  (usa: approve {slug} {g})")


@app.command()
def advance(slug: str):
    """Corre la siguiente etapa (se detiene en compuertas pendientes)."""
    ctx = ProjectContext(slug=slug)
    try:
        result = advance_runner(ctx)
    except NotImplementedError as exc:
        rprint(f"[yellow]Etapa no cableada todavía (Fase 1):[/yellow] {exc}")
        raise typer.Exit(code=2)
    except Exception as exc:  # conexión a Ollama/ComfyUI, etc.
        rprint(f"[red]Error ejecutando la etapa:[/red] {type(exc).__name__}: {exc}")
        raise typer.Exit(code=1)
    rprint(result)


@app.command()
def approve(slug: str, gate: str):
    """Aprueba una compuerta: script | design | images | final."""
    ctx = ProjectContext(slug=slug)
    approve_gate(ctx, gate)
    rprint(f"[green]Compuerta '{gate}' aprobada para {slug}.[/green]")


@app.command()
def run(slug: str, stage: str):
    """Corre una etapa puntual por su clave (s01_brief..s10_publish)."""
    ctx = ProjectContext(slug=slug)
    try:
        result = get_runner(stage)(ctx)
    except NotImplementedError as exc:
        rprint(f"[yellow]Etapa no cableada todavía (Fase 1):[/yellow] {exc}")
        raise typer.Exit(code=2)
    rprint(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    app()
