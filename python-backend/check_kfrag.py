"""
Check kfrag file existence and path resolution
"""
from src.registry import BlockchainRegistry
from pathlib import Path
from urllib.parse import urlparse, unquote
from rich.console import Console

console = Console()

def resolve_kfrag_uri(uri: str) -> Path:
    """Resolve kfrag URI to local path"""
    if uri.startswith("file://"):
        parsed = urlparse(uri)
        local_path = unquote(parsed.path)
        # On Windows, remove leading slash if present
        if local_path.startswith("/") and ":" in local_path:
            local_path = local_path[1:]
        return Path(local_path)
    else:
        # Assume it's already a local path
        return Path(uri)

try:
    registry = BlockchainRegistry()
    grants = registry.list_grants()
    
    for grant in grants:
        if not grant.processed:
            console.print(f"[cyan]Checking grant for {grant.recipient_address}[/]")
            console.print(f"  Kfrag URI from blockchain: {grant.reencryption_key_path}")
            
            if grant.reencryption_key_path:
                resolved_path = resolve_kfrag_uri(grant.reencryption_key_path)
                console.print(f"  Resolved path: {resolved_path}")
                console.print(f"  Path exists: {resolved_path.exists()}")
                
                if resolved_path.exists():
                    console.print(f"  File size: {resolved_path.stat().st_size} bytes")
                    # Try to read it
                    try:
                        import json
                        with open(resolved_path, 'r') as f:
                            data = json.load(f)
                        console.print(f"  [green]✓ Valid JSON file with {len(data)} kfrags[/]")
                    except Exception as e:
                        console.print(f"  [red]✗ Error reading file: {e}[/]")
                else:
                    # List files in kfrags directory
                    kfrags_dir = Path("data/kfrags")
                    if kfrags_dir.exists():
                        console.print(f"\n  [yellow]Files in {kfrags_dir}:[/]")
                        for f in kfrags_dir.iterdir():
                            console.print(f"    - {f.name}")
            else:
                console.print(f"  [red]No kfrag path set[/]")
                
except Exception as e:
    console.print(f"[red]Error: {e}[/]")
    import traceback
    console.print(traceback.format_exc())
