from __future__ import annotations

import hashlib
from base64 import b64encode

import typer
from rich.console import Console

from .config import settings
from .models import AccessGrant
from .registry import LocalRegistry
from .utils.crypto_utils import (
    generate_reencryption_keys,
    load_or_create_owner_keys,
    load_or_create_recipient_keys,
    save_kfrags,
)

app = typer.Typer(help="Owner utilities for managing data + re-encryption keys.")
console = Console()

REGISTRY = LocalRegistry(settings.data_dir / "registry.json")


@app.command("grant-access")
def grant_access(
    cid: str = typer.Argument(..., help="IPFS CID of the data to grant access to"),
    recipient_address: str = typer.Argument(..., help="Recipient's address/ID"),
):
    """
    Generate re-encryption keys for a recipient to access encrypted data.

    This command:
    1. Loads the owner's keys
    2. Loads or creates the recipient's keys
    3. Generates re-encryption key fragments (kfrags)
    4. Saves the kfrags and records the grant in the local registry

    Example:
        python -m src.owner_cli grant-access QmXXX... 0xRecipient
    """
    # Check if data record exists
    records = REGISTRY.list_records()
    record = next((r for r in records if r.cid == cid), None)
    if not record:
        console.print(f"[red]Error: No data record found for CID {cid}[/]")
        console.print("[yellow]Make sure you've run 'sensor_service produce' first.[/]")
        raise typer.Exit(code=1)

    # Check if grant already exists
    existing_grant = REGISTRY.get_grant(cid, recipient_address)
    if existing_grant:
        console.print(
            f"[yellow]Grant already exists for {recipient_address} on CID {cid}[/]"
        )
        console.print(f"Kfrags stored at: {existing_grant.reencryption_key_path}")
        return

    console.print(f"[cyan]Loading owner keys...[/]")
    owner_keys = load_or_create_owner_keys()

    console.print(f"[cyan]Loading/creating recipient keys for {recipient_address}...[/]")
    recipient_keys = load_or_create_recipient_keys(recipient_address)

    console.print(f"[cyan]Generating re-encryption keys...[/]")
    kfrags = generate_reencryption_keys(
        owner_keys=owner_keys,
        recipient_pubkey=recipient_keys.public_key,
        threshold=1,
        shares=1,
    )

    # Create a unique grant ID
    grant_id = hashlib.sha256(
        f"{cid}:{recipient_address}".encode()
    ).hexdigest()[:16]

    kfrag_path = save_kfrags(kfrags, grant_id)
    console.print(f"[green]Saved kfrags to {kfrag_path}[/]")

    # Create and save the grant
    grant = AccessGrant(
        cid=cid,
        owner_address=settings.owner_address,
        recipient_address=recipient_address,
        recipient_public_key=b64encode(bytes(recipient_keys.public_key)).decode("ascii"),
        reencryption_key_path=str(kfrag_path),
    )
    REGISTRY.add_grant(grant)

    console.print(
        f"[bold green]Success![/] Access granted to {recipient_address} for CID {cid}"
    )
    console.print(f"Recipient can now use the proxy to decrypt this data.")


@app.command("list-grants")
def list_grants(cid: str = typer.Option(None, help="Filter by CID")):
    """List all access grants, optionally filtered by CID."""
    grants = REGISTRY.list_grants(cid)
    if not grants:
        console.print("[yellow]No grants found.[/]")
        return

    for grant in grants:
        console.print(
            f"- CID: {grant.cid} | Recipient: {grant.recipient_address} | "
            f"Created: {grant.created_at}"
        )


if __name__ == "__main__":
    app()

