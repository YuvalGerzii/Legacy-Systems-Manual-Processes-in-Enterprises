#!/usr/bin/env python3
"""
Enterprise AI - Model Management CLI
100% FREE - Manage your local LLMs with ease!

Usage:
    python cli.py models list
    python cli.py models pull llama3.2:3b
    python cli.py models delete old-model
    python cli.py stats
    python cli.py test
    python cli.py benchmark
"""

import asyncio
import sys
from pathlib import Path
from typing import List

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich import print as rprint

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.llm import get_local_llm
from src.legacy_migrator.analyzer import CodeTranslator
from src.legacy_migrator.models import SourceLanguage, TargetLanguage

console = Console()


@click.group()
def cli():
    """Enterprise AI Model Management CLI - 100% FREE!"""
    pass


@cli.group()
def models():
    """Manage local LLM models."""
    pass


@models.command("list")
def list_models():
    """List all installed local models."""
    async def _list():
        llm = get_local_llm()

        # Check if Ollama is available
        if not await llm.is_available():
            console.print("[red]❌ Ollama service not available![/red]")
            console.print("\nStart it with: docker-compose up -d ollama")
            return

        console.print("\n[bold cyan]📦 Installed Local Models[/bold cyan]\n")

        model_list = await llm.list_models()

        if not model_list:
            console.print("[yellow]No models installed yet.[/yellow]")
            console.print("\nInstall a model with:")
            console.print("  python cli.py models pull llama3.2:3b")
            return

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Model Name", style="cyan")
        table.add_column("Status", style="green")

        for model in model_list:
            table.add_row(model, "✓ Installed")

        console.print(table)
        console.print(f"\n[green]Total: {len(model_list)} models[/green]")

    asyncio.run(_list())


@models.command("pull")
@click.argument("model_name")
def pull_model(model_name: str):
    """Download a model from Ollama library."""
    async def _pull():
        llm = get_local_llm()

        console.print(f"\n[bold cyan]📥 Pulling model: {model_name}[/bold cyan]\n")

        with Progress() as progress:
            task = progress.add_task(f"Downloading {model_name}...", total=None)

            success = await llm.pull_model(model_name)

            progress.update(task, completed=True)

        if success:
            console.print(f"\n[green]✓ Successfully pulled {model_name}[/green]")
        else:
            console.print(f"\n[red]❌ Failed to pull {model_name}[/red]")

    asyncio.run(_pull())


@models.command("delete")
@click.argument("model_name")
@click.confirmation_option(prompt="Are you sure you want to delete this model?")
def delete_model(model_name: str):
    """Delete a local model to free space."""
    async def _delete():
        llm = get_local_llm()

        console.print(f"\n[bold yellow]🗑️  Deleting model: {model_name}[/bold yellow]\n")

        success = await llm.delete_model(model_name)

        if success:
            console.print(f"\n[green]✓ Successfully deleted {model_name}[/green]")
        else:
            console.print(f"\n[red]❌ Failed to delete {model_name}[/red]")

    asyncio.run(_delete())


@models.command("recommend")
def recommend_models():
    """Show recommended models for different use cases."""
    console.print("\n[bold cyan]🌟 Recommended FREE Models[/bold cyan]\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Model", style="cyan")
    table.add_column("Size", style="yellow")
    table.add_column("Use Case", style="green")
    table.add_column("Speed", style="blue")

    recommendations = [
        ("llama3.2:3b", "3B", "General tasks, fast", "⚡⚡⚡"),
        ("llama3.1:8b", "8B", "Balanced performance", "⚡⚡"),
        ("llama3.1:70b", "70B", "Highest quality", "⚡"),
        ("codellama:13b", "13B", "Code generation", "⚡⚡"),
        ("mistral:7b", "7B", "Fast & capable", "⚡⚡⚡"),
        ("nomic-embed-text", "768d", "Embeddings", "⚡⚡⚡"),
    ]

    for model, size, use_case, speed in recommendations:
        table.add_row(model, size, use_case, speed)

    console.print(table)

    console.print("\n[bold]Installation:[/bold]")
    console.print("  python cli.py models pull llama3.2:3b")


@cli.command()
def stats():
    """Show LLM usage statistics and cost savings."""
    async def _stats():
        llm = get_local_llm()

        console.print("\n[bold cyan]📊 LLM Usage Statistics[/bold cyan]\n")

        # Get metrics
        metrics = llm.get_metrics()

        table = Table(show_header=False)
        table.add_column("Metric", style="cyan", width=30)
        table.add_column("Value", style="green", justify="right")

        table.add_row("Total Requests", str(metrics["total_requests"]))
        table.add_row("Total Tokens", f"{metrics['total_tokens']:,}")
        table.add_row("Avg Response Time", metrics["avg_response_time"])
        table.add_row("Error Rate", metrics["error_rate"])
        table.add_row("💰 Cost Saved (vs GPT-4)", metrics["cost_saved"])

        console.print(table)

        # Cache stats
        console.print("\n[bold cyan]💾 Cache Statistics[/bold cyan]\n")
        cache_stats = llm.get_cache_stats()

        if cache_stats.get("enabled", True):
            cache_table = Table(show_header=False)
            cache_table.add_column("Metric", style="cyan", width=30)
            cache_table.add_column("Value", style="green", justify="right")

            cache_table.add_row("Cache Hits", str(cache_stats["hits"]))
            cache_table.add_row("Cache Misses", str(cache_stats["misses"]))
            cache_table.add_row("Hit Rate", cache_stats["hit_rate"])
            cache_table.add_row("Cache Size", str(cache_stats["size"]))

            console.print(cache_table)
        else:
            console.print("[yellow]Caching disabled[/yellow]")

    asyncio.run(_stats())


@cli.command()
def test():
    """Test local LLM with a simple prompt."""
    async def _test():
        llm = get_local_llm()

        console.print("\n[bold cyan]🧪 Testing Local LLM[/bold cyan]\n")

        # Check availability
        is_available = await llm.is_available()

        if not is_available:
            console.print("[red]❌ Ollama service not available![/red]")
            console.print("\nStart it with: docker-compose up -d ollama")
            return

        console.print(f"[green]✓ Ollama is running[/green]")
        console.print(f"[green]✓ Model: {llm.model}[/green]\n")

        # Test completion
        console.print("[bold]Testing chat completion...[/bold]")

        with Progress() as progress:
            task = progress.add_task("Generating response...", total=None)

            response = await llm.chat_completion(
                messages=[
                    {"role": "user", "content": "Say 'Hello from local LLM!' in one sentence."}
                ],
                temperature=0.7,
                max_tokens=50,
            )

            progress.update(task, completed=True)

        console.print(f"\n[bold green]Response:[/bold green] {response}\n")

        # Test embedding
        console.print("[bold]Testing embeddings...[/bold]")

        embedding = await llm.generate_embedding("test text")

        console.print(f"[green]✓ Generated {len(embedding)}-dimensional embedding[/green]\n")

        console.print("[bold green]✅ All tests passed![/bold green]")

    asyncio.run(_test())


@cli.command()
@click.option("--prompts", "-n", default=10, help="Number of prompts to test")
def benchmark(prompts: int):
    """Benchmark local LLM performance."""
    async def _benchmark():
        import time

        llm = get_local_llm()

        console.print(f"\n[bold cyan]⚡ Benchmarking Local LLM ({prompts} prompts)[/bold cyan]\n")

        test_prompts = [
            f"Count to {i} in one sentence."
            for i in range(1, prompts + 1)
        ]

        start_time = time.time()

        with Progress() as progress:
            task = progress.add_task(f"Processing {prompts} prompts...", total=prompts)

            results = await llm.batch_completion(
                test_prompts,
                temperature=0.7,
                max_tokens=50,
                max_concurrent=5,
            )

            progress.update(task, advance=prompts)

        end_time = time.time()
        duration = end_time - start_time

        # Calculate stats
        successful = sum(1 for r in results if not isinstance(r, Exception))
        failed = prompts - successful
        avg_time = duration / prompts
        throughput = prompts / duration

        # Display results
        table = Table(show_header=False)
        table.add_column("Metric", style="cyan", width=30)
        table.add_column("Value", style="green", justify="right")

        table.add_row("Total Prompts", str(prompts))
        table.add_row("Successful", str(successful))
        table.add_row("Failed", str(failed))
        table.add_row("Total Time", f"{duration:.2f}s")
        table.add_row("Avg Time/Prompt", f"{avg_time:.2f}s")
        table.add_row("Throughput", f"{throughput:.2f} prompts/s")

        console.print(table)

        # Cost savings
        estimated_gpt4_cost = prompts * 0.03  # Rough estimate
        console.print(f"\n[bold green]💰 Saved ${estimated_gpt4_cost:.2f} vs GPT-4![/bold green]")

    asyncio.run(_benchmark())


@cli.command()
def demo():
    """Run a code translation demo."""
    async def _demo():
        console.print("\n[bold cyan]🚀 Code Translation Demo[/bold cyan]\n")

        cobol_code = """
       IDENTIFICATION DIVISION.
       PROGRAM-ID. HELLO-WORLD.
       PROCEDURE DIVISION.
           DISPLAY 'Hello, Enterprise!'.
           STOP RUN.
        """

        console.print("[bold]Original COBOL code:[/bold]")
        console.print(f"[yellow]{cobol_code}[/yellow]\n")

        console.print("[bold]Translating to Python using LOCAL LLM...[/bold]\n")

        translator = CodeTranslator()

        with Progress() as progress:
            task = progress.add_task("Translating...", total=None)

            result = await translator.translate_code(
                cobol_code,
                SourceLanguage.COBOL,
                TargetLanguage.PYTHON,
            )

            progress.update(task, completed=True)

        console.print("[bold green]Translated Python code:[/bold green]")
        console.print(f"[green]{result.translated_code}[/green]\n")
        console.print(f"[bold]Confidence:[/bold] {result.confidence * 100:.0f}%")
        console.print(f"\n[bold green]✓ Translation complete - 100% FREE![/bold green]")

    asyncio.run(_demo())


@cli.command()
def health():
    """Check health of all components."""
    async def _health():
        console.print("\n[bold cyan]🏥 Health Check[/bold cyan]\n")

        checks = []

        # Ollama
        llm = get_local_llm()
        ollama_ok = await llm.is_available()
        checks.append(("Ollama Service", ollama_ok))

        # Models
        if ollama_ok:
            models = await llm.list_models()
            models_ok = len(models) > 0
            checks.append(("Installed Models", models_ok))
        else:
            checks.append(("Installed Models", False))

        # Display results
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")

        for component, status in checks:
            status_str = "[green]✓ Healthy[/green]" if status else "[red]✗ Unhealthy[/red]"
            table.add_row(component, status_str)

        console.print(table)

        all_healthy = all(status for _, status in checks)

        if all_healthy:
            console.print("\n[bold green]✅ All systems operational![/bold green]")
        else:
            console.print("\n[bold red]❌ Some systems need attention[/bold red]")
            console.print("\nTroubleshooting:")
            console.print("  1. Start Ollama: docker-compose up -d ollama")
            console.print("  2. Install models: python cli.py models pull llama3.2:3b")

    asyncio.run(_health())


if __name__ == "__main__":
    cli()
