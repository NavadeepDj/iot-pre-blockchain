"""
Debug proxy worker with detailed error logging
"""
from src.proxy_worker import process_grant, REGISTRY
from rich.console import Console
import traceback

console = Console()

def debug_proxy():
    console.print("[cyan]Starting proxy worker debug...[/]")
    
    if not REGISTRY:
        console.print("[red]Registry not available.[/]")
        return

    all_grants = REGISTRY.list_grants()
    console.print(f"[yellow]Total grants found: {len(all_grants)}[/]")
    
    unprocessed = [g for g in all_grants if not g.processed]
    console.print(f"[yellow]Unprocessed grants: {len(unprocessed)}[/]")

    if unprocessed:
        for i, grant in enumerate(unprocessed):
            console.print(f"\n[bold]Grant {i+1}/{len(unprocessed)}:[/]")
            console.print(f"  CID: {grant.cid}")
            console.print(f"  Recipient: {grant.recipient_address}")
            console.print(f"  Kfrag path: {grant.reencryption_key_path}")
            console.print(f"  Processed: {grant.processed}")
            
            try:
                success = process_grant(grant)
                if success:
                    console.print(f"[bold green]✓ Success[/]")
                else:
                    console.print(f"[bold red]✗ Failed (returned False)[/]")
            except Exception as e:
                console.print(f"[bold red]✗ Exception: {e}[/]")
                console.print(f"[dim]{traceback.format_exc()}[/]")
    else:
        console.print("[dim]No unprocessed grants found.[/]")

if __name__ == "__main__":
    debug_proxy()
