from typing import Optional
import typer
from rich.console import Console
from rich.prompt import IntPrompt, Prompt
from rich.panel import Panel
from agents.orchestrator import Orchestrator
from agents.trend_engine import TrendEngine
from agents.sources import SOURCES

app = typer.Typer(add_completion=False)
console = Console()


@app.command("trends")
def trends(
    sources: str = typer.Option("reddit,civitai,promptschat", "--sources", help="Comma-separated: reddit, civitai, promptschat"),
    top: int = typer.Option(20, "--top", min=1, max=100, help="How many ranked trends to keep"),
):
    """Fetch viral prompts, score them, extract insights, store to trends.json."""
    source_list = [s.strip() for s in sources.split(",") if s.strip()]
    unknown = [s for s in source_list if s not in SOURCES]
    if unknown:
        console.print(f"[bold red]Error:[/bold red] unknown source(s): {', '.join(unknown)}. Valid: {', '.join(SOURCES)}")
        raise typer.Exit(code=1)

    console.print(f"[green]Fetching viral prompts from: {', '.join(source_list)}...[/green]")
    engine = TrendEngine()
    engine.run(sources=source_list, top=top)
    console.print("\n[bold green]Done![/bold green] View ranked trends: http://localhost:8000/trends")


@app.command("run")
def main(
    topics: Optional[int] = typer.Option(None, "--topics", min=0, help="Number of trending topics"),
    prompts: Optional[int] = typer.Option(None, "--prompts", min=0, help="Prompt posts per topic"),
    workflows: Optional[int] = typer.Option(None, "--workflows", min=0, help="Workflow posts per topic"),
    categories: Optional[str] = typer.Option(None, "--categories", help="Comma-separated categories, or 'all'"),
    publish: bool = typer.Option(False, "--publish", help="Publish immediately instead of saving as drafts"),
):
    non_interactive = topics is not None or prompts is not None or workflows is not None or categories is not None

    if non_interactive:
        if topics is None or prompts is None or workflows is None:
            console.print("[bold red]Error:[/bold red] --topics, --prompts, and --workflows are all required together in non-interactive mode.")
            raise typer.Exit(code=1)
        n_topics, n_prompts, n_workflows = topics, prompts, workflows
        categories_list = [c.strip() for c in (categories or "all").split(",")]
    else:
        console.print(Panel.fit("[bold yellow]ContentPilot[/bold yellow] — AI Content Agent", border_style="yellow"))
        n_topics = IntPrompt.ask("\nHow many trending topics today")
        n_prompts = IntPrompt.ask("Prompts per topic [bold](with image)[/bold]")
        n_workflows = IntPrompt.ask("Workflows per topic")
        categories_raw = Prompt.ask(
            "Categories [dim](generative-ai, genz, photography, or all)[/dim]",
            default="all",
        )
        categories_list = [c.strip() for c in categories_raw.split(",")]

    console.print(f"\n[green]Fetching {n_topics} trending topics...[/green]")

    orch = Orchestrator()
    orch.run(
        n_topics=n_topics,
        n_prompts=n_prompts,
        n_workflows=n_workflows,
        categories=categories_list,
        draft=not publish,
    )

    mode = "published" if publish else "saved as drafts — review at http://localhost:8000/drafts"
    console.print(f"\n[bold green]Done![/bold green] Content {mode}.")


if __name__ == "__main__":
    app()
