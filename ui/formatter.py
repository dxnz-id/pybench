from rich.console import Console
from rich.panel import Panel

console = Console()

def log(category, message, style="white", verbose=False):
    if verbose:
        console.print(f"[[bold {style}]{category:^8}[/]] {message}")

def show_welcome():
    welcome_text = """
[bold cyan]PyBench[/bold cyan]
[white]--------------------------------------------[/white]
[yellow]Available Benchmarks:[/yellow]
[green]1.[/green] CPU Benchmark
[green]2.[/green] Memory Benchmark
[green]3.[/green] Disk Benchmark
[green]4.[/green] GPU Benchmark
[white]--------------------------------------------[/white]
[dim]Enter numbers separated by comma (e.g. 1,3) or 'all' to run.[/dim]
"""
    console.print(Panel(welcome_text, expand=False, border_style="blue"))

def mb_format(val):
    if val >= 1024:
        return f"{val/1024:.2f} GB/s"
    return f"{val:.2f} MB/s"
