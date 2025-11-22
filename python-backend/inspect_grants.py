"""
Inspect grant details to debug kfrag path issue
"""
from src.registry import BlockchainRegistry
from rich.console import Console
import json

console = Console()

try:
    registry = BlockchainRegistry()
    grants = registry.list_grants()
    
    console.print(f"[yellow]Total grants: {len(grants)}[/]")
    
    for i, grant in enumerate(grants):
        console.print(f"\n[bold cyan]Grant {i+1}:[/]")
        console.print(f"  CID: {grant.cid}")
        console.print(f"  Owner: {grant.owner_address}")
        console.print(f"  Recipient: {grant.recipient_address}")
        console.print(f"  Recipient Public Key: {grant.recipient_public_key}")
        console.print(f"  Kfrag Path: {grant.reencryption_key_path}")
        console.print(f"  Reencrypted CID: {grant.reencrypted_cid}")
        console.print(f"  Processed: {grant.processed}")
        console.print(f"  Created At: {grant.created_at}")
        
        # Try to get raw data from blockchain
        raw_grant = registry.client.get_grant(grant.cid, grant.recipient_address)
        console.print(f"\n[dim]Raw blockchain data:[/]")
        console.print(f"  kfragUri: {raw_grant['kfragUri']}")
        console.print(f"  recipientPublicKey: {raw_grant['recipientPublicKey']}")
        
except Exception as e:
    console.print(f"[red]Error: {e}[/]")
    import traceback
    console.print(traceback.format_exc())
