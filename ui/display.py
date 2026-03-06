from rich.console import Console

console = Console()

def title(text):
    console.rule(f"[bold cyan]{text}")

def success(msg):
    console.print(f"[green]{msg}")

def error(msg):
    console.print(f"[red]{msg}")