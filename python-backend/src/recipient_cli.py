from __future__ import annotations

import json
from base64 import b64decode
from pathlib import Path

import typer
from rich.console import Console

from .config import settings
from .registry import LocalRegistry
from .utils.crypto_utils import (
    decrypt_reencrypted,
    load_or_create_owner_keys,
    load_or_create_recipient_keys,
)
from .utils.ipfs_client import get_ipfs_client
from umbral.capsule import Capsule
from umbral.capsule_frag import CapsuleFrag, VerifiedCapsuleFrag

app = typer.Typer(help="Recipient workflow for fetching + decrypting data.")
console = Console()

REGISTRY = LocalRegistry(settings.data_dir / "registry.json")


@app.command("decrypt")
def decrypt(
    cid: str = typer.Argument(..., help="Original CID of the encrypted data"),
    recipient_id: str = typer.Option(
        default="recipient-1",
        help="Your recipient identifier/address",
    ),
):
    """
    Fetch and decrypt re-encrypted data that was granted to you.

    This command:
    1. Checks if you have access to the given CID
    2. Fetches the re-encrypted blob from IPFS
    3. Decrypts it using your private key
    4. Displays the original IoT data

    Example:
        python -m src.recipient_cli decrypt QmXXX...
    """
    # Check if grant exists
    grant = REGISTRY.get_grant(cid, recipient_id)
    if not grant:
        console.print(
            f"[red]Error: No access grant found for {recipient_id} on CID {cid}[/]"
        )
        console.print("[yellow]Make sure the owner has granted you access first.[/]")
        raise typer.Exit(code=1)

    if not grant.processed:
        console.print(
            f"[yellow]Grant exists but proxy hasn't processed it yet.[/]"
        )
        console.print("[yellow]Run the proxy worker to re-encrypt the data.[/]")
        raise typer.Exit(code=1)

    if not grant.reencrypted_cid:
        console.print("[red]Error: Re-encrypted CID not found.[/]")
        raise typer.Exit(code=1)

    console.print(f"[cyan]Fetching re-encrypted blob from IPFS (CID: {grant.reencrypted_cid})...[/]")

    # Fetch re-encrypted blob
    try:
        ipfs_client = get_ipfs_client()
        reencrypted_blob_bytes = ipfs_client.cat(grant.reencrypted_cid)
    except Exception as exc:
        console.print(f"[red]Failed to fetch from IPFS: {exc}[/]")
        raise typer.Exit(code=1) from exc

    # Parse the blob
    try:
        reencrypted_blob = json.loads(reencrypted_blob_bytes)
        ciphertext_b64 = reencrypted_blob["ciphertext"]
        original_capsule_b64 = reencrypted_blob["original_capsule"]
        cfrag_b64 = reencrypted_blob["cfrag"]

        ciphertext = b64decode(ciphertext_b64)
        original_capsule = Capsule.from_bytes(b64decode(original_capsule_b64))
        cfrag = CapsuleFrag.from_bytes(b64decode(cfrag_b64))
        verified_cfrag = VerifiedCapsuleFrag(cfrag)
    except Exception as exc:
        console.print(f"[red]Failed to parse re-encrypted blob: {exc}[/]")
        raise typer.Exit(code=1) from exc

    # Load recipient keys
    console.print(f"[cyan]Loading your keys...[/]")
    recipient_keys = load_or_create_recipient_keys(recipient_id)

    # Load owner's public key (needed for decryption)
    owner_keys = load_or_create_owner_keys()
    owner_pubkey = owner_keys.public_key

    # Decrypt
    console.print(f"[cyan]Decrypting data...[/]")
    try:
        plaintext = decrypt_reencrypted(
            recipient_keys=recipient_keys,
            owner_pubkey=owner_pubkey,
            capsule=original_capsule,
            cfrags=[verified_cfrag],
            ciphertext=ciphertext,
        )
    except Exception as exc:
        console.print(f"[red]Decryption failed: {exc}[/]")
        raise typer.Exit(code=1) from exc

    # Display the decrypted data
    console.print(f"[bold green]✓ Successfully decrypted![/]")
    console.print(f"\n[bold]Original IoT Data:[/]")
    try:
        data_json = json.loads(plaintext)
        console.print_json(json.dumps(data_json, indent=2))
    except json.JSONDecodeError:
        console.print(plaintext.decode("utf-8", errors="replace"))

    # Optionally save to file
    output_path = settings.data_dir / "decrypted" / f"{recipient_id}_{cid[:16]}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(plaintext)
    console.print(f"\n[dim]Saved to {output_path}[/]")


@app.command("list-access")
def list_access(
    recipient_id: str = typer.Option(
        default="recipient-1",
        help="Your recipient ID",
    ),
):
    """List all CIDs you have access to."""
    all_grants = REGISTRY.list_grants()
    my_grants = [g for g in all_grants if g.recipient_address == recipient_id]

    if not my_grants:
        console.print(f"[yellow]No access grants found for {recipient_id}[/]")
        return

    console.print(f"[bold]Access grants for {recipient_id}:[/]")
    for grant in my_grants:
        status = "✓ Processed" if grant.processed else "⏳ Pending"
        console.print(
            f"- CID: {grant.cid} | Status: {status} | "
            f"Re-encrypted CID: {grant.reencrypted_cid or 'N/A'}"
        )


if __name__ == "__main__":
    app()

