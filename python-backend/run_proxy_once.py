from src.proxy_worker import process_grant, REGISTRY
from rich.console import Console

console = Console()

def run_once():
    console.print("[cyan]Running proxy worker (one-shot)...[/]")
    if not REGISTRY:
        console.print("[red]Registry not available.[/]")
        return

    all_grants = REGISTRY.list_grants()
    unprocessed = [g for g in all_grants if not g.processed]

    if unprocessed:
        console.print(f"[yellow]Found {len(unprocessed)} unprocessed grant(s)[/]")
        for grant in unprocessed:
            success = process_grant(grant)
            if success:
                console.print(f"[bold green]✓[/] Processed grant for {grant.recipient_address}")
            else:
                console.print(f"[bold red]✗[/] Failed to process grant for {grant.recipient_address}")
    else:
        console.print("[dim]No unprocessed grants found.[/]")

if __name__ == "__main__":
    run_once()
