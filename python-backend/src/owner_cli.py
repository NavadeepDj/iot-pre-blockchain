from __future__ import annotations

import hashlib
from base64 import b64encode
from pathlib import Path

import typer
from rich.console import Console

from web3 import Web3
from web3.exceptions import ContractLogicError

from .config import settings
from .models import AccessGrant
from .registry import BlockchainRegistry
from .utils.crypto_utils import (
    generate_reencryption_keys,
    load_or_create_owner_keys,
    load_or_create_recipient_keys,
    save_kfrags,
)
from .blockchain_client import (
    BlockchainUnavailable,
    MissingPrivateKey,
)

app = typer.Typer(help="Owner utilities for managing data + re-encryption keys.")
console = Console()

try:
    REGISTRY = BlockchainRegistry()
except BlockchainUnavailable:
    console.print("[yellow]Blockchain client unavailable. Ensure Anvil is running.[/]")
    REGISTRY = None



@app.command("register-data")
def register_data_command(
    cid: str = typer.Argument(..., help="IPFS CID of the encrypted blob"),
    data_hash: str = typer.Argument(..., help="SHA-256 hash (hex) of the ciphertext"),
    sensor_id: str = typer.Argument(..., help="Sensor identifier"),
):
    """
    Manually register a data record on-chain.
    Useful if the automatic registration failed or for backfilling.
    """
    if not REGISTRY:
        console.print("[yellow]Blockchain client unavailable; cannot register on-chain.[/]")
        raise typer.Exit(code=1)

    try:
        receipt = REGISTRY.client.register_data(cid, data_hash, sensor_id)
    except MissingPrivateKey:
        console.print("[red]OWNER_PRIVATE_KEY missing; cannot send transaction.[/]")
        raise typer.Exit(code=1)
    except BlockchainUnavailable as exc:
        console.print(f"[red]{exc}[/]")
        raise typer.Exit(code=1)
    except ContractLogicError as exc:
        console.print(f"[yellow]On-chain call reverted: {exc}[/]")
        raise typer.Exit(code=1)

    console.print(
        f"[bold green]Registered![/] tx={receipt.tx_hash} block={receipt.block_number}"
    )


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
    kfrag_uri = Path(kfrag_path).as_uri()

    # Create and save the grant on-chain
    try:
        receipt = REGISTRY.client.grant_access(
            cid, 
            recipient_address, 
            b64encode(bytes(recipient_keys.public_key)).decode("ascii"),
            kfrag_uri
        )
        console.print(
            f"[bold green]Success![/] Access granted to {recipient_address} for CID {cid}"
        )
        console.print(
            f"[cyan]On-chain AccessGranted tx:[/] {receipt.tx_hash} "
            f"(block {receipt.block_number})"
        )
    except MissingPrivateKey:
        console.print("[red]OWNER_PRIVATE_KEY missing; cannot send transaction.[/]")
        raise typer.Exit(code=1)
    except Exception as exc:
        console.print(f"[red]Failed to grant access on-chain: {exc}[/]")
        raise typer.Exit(code=1)

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

