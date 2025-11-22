from __future__ import annotations

import json
import time
from base64 import b64decode, b64encode
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse, unquote

from rich.console import Console

from .config import settings
from .models import AccessGrant
from .registry import BlockchainRegistry
from .blockchain_client import BlockchainUnavailable
from .utils.crypto_utils import (
    load_kfrags,
    reencrypt_capsule,
)
from .utils.ipfs_client import get_ipfs_client
from umbral.capsule import Capsule

console = Console()

try:
    REGISTRY = BlockchainRegistry()
except BlockchainUnavailable:
    console.print("[yellow]Blockchain client unavailable. Ensure Anvil is running.[/]")
    REGISTRY = None

REENCIPHERED_DIR = settings.data_dir / "reenciphered"
REENCIPHERED_DIR.mkdir(parents=True, exist_ok=True)


def process_grant(grant: AccessGrant) -> bool:
    """
    Process a single access grant: fetch original data, re-encrypt, upload to IPFS.
    """
    console.print(
        f"[cyan]Processing grant: CID {grant.cid} for recipient {grant.recipient_address}[/]"
    )

    # Load kfrags
    if not grant.reencryption_key_path:
        console.print(f"[red]No kfrag path found for grant[/]")
        return False

    # Resolve kfrag path (it might be a URI)
    kfrag_path = _resolve_kfrag_uri(grant.reencryption_key_path)
    if not kfrag_path or not kfrag_path.exists():
         console.print(f"[red]Kfrag file not found at {grant.reencryption_key_path}[/]")
         return False

    kfrags = load_kfrags(kfrag_path)
    if not kfrags:
        console.print(f"[red]Failed to load kfrags from {kfrag_path}[/]")
        return False

    # Fetch original encrypted blob from IPFS
    try:
        ipfs_client = get_ipfs_client()
        original_blob_bytes = ipfs_client.cat(grant.cid)
    except Exception as exc:
        console.print(f"[red]Failed to fetch CID {grant.cid} from IPFS: {exc}[/]")
        return False

    # Parse the blob to extract ciphertext and capsule
    try:
        original_blob = json.loads(original_blob_bytes)
        ciphertext_b64 = original_blob["ciphertext"]
        capsule_b64 = original_blob["capsule"]
        ciphertext = b64decode(ciphertext_b64)
        capsule = Capsule.from_bytes(b64decode(capsule_b64))
    except Exception as exc:
        console.print(f"[red]Failed to parse encrypted blob: {exc}[/]")
        return False

    # Re-encrypt the capsule using the kfrag
    console.print(f"[cyan]Re-encrypting capsule...[/]")
    try:
        cfrag = reencrypt_capsule(capsule, kfrags[0])
    except Exception as exc:
        console.print(f"[red]Re-encryption failed: {exc}[/]")
        return False

    # Create re-encrypted blob
    reencrypted_blob = {
        "original_cid": grant.cid,
        "recipient": grant.recipient_address,
        "ciphertext": b64encode(ciphertext).decode("ascii"),
        "original_capsule": capsule_b64,
        "cfrag": b64encode(bytes(cfrag.cfrag)).decode("ascii"),
        "note": "This blob contains the re-encrypted capsule fragment (cfrag) that the recipient needs to decrypt",
    }
    reencrypted_bytes = json.dumps(reencrypted_blob, indent=2).encode()

    # Upload to IPFS
    try:
        reencrypted_cid = ipfs_client.add_bytes(reencrypted_bytes)
        console.print(f"[green]Re-encrypted blob uploaded to IPFS: {reencrypted_cid}[/]")
    except Exception as exc:
        console.print(f"[red]Failed to upload to IPFS: {exc}[/]")
        return False

    # Update grant on chain
    try:
        receipt = REGISTRY.client.complete_access(grant.cid, grant.recipient_address, reencrypted_cid)
        console.print(f"[green]Updated grant on chain: {receipt.tx_hash}[/]")
    except Exception as exc:
        console.print(f"[red]Failed to update grant on chain: {exc}[/]")
        return False

    # Also save locally for easy access
    local_path = REENCIPHERED_DIR / f"{grant.recipient_address}_{grant.cid[:16]}.json"
    local_path.write_bytes(reencrypted_bytes)
    console.print(f"[green]Saved locally at {local_path}[/]")

    return True


def main(poll_interval: float = 5.0):
    """
    Proxy worker that polls for new access grants and re-encrypts data.
    """
    console.print("[cyan]Proxy worker starting. Polling for access grants...[/]")

    if not REGISTRY:
        console.print("[red]Registry not available. Exiting.[/]")
        return

    try:
        while True:
            # Get all grants and filter for unprocessed ones
            # Note: list_grants fetches all events, which is inefficient but simple
            all_grants = REGISTRY.list_grants()
            unprocessed = [g for g in all_grants if not g.processed]

            if unprocessed:
                console.print(f"[yellow]Found {len(unprocessed)} unprocessed grant(s)[/]")
                for grant in unprocessed:
                    success = process_grant(grant)
                    if success:
                        console.print(
                            f"[bold green]✓[/] Processed grant for {grant.recipient_address}"
                        )
                    else:
                        console.print(
                            f"[bold red]✗[/] Failed to process grant for {grant.recipient_address}"
                        )
            else:
                console.print("[dim]No unprocessed grants. Waiting...[/]", end="\r")

            time.sleep(poll_interval)
    except KeyboardInterrupt:
        console.print("\n[green]Proxy worker stopped.[/]")


def _resolve_kfrag_uri(uri: str) -> Optional[Path]:
    if not uri:
        return None
    parsed = urlparse(uri)
    if parsed.scheme in ("", "file"):
        if parsed.scheme == "file":
            local_path = unquote(parsed.path)
            # On Windows, remove leading slash if path contains drive letter
            if local_path.startswith("/") and len(local_path) > 2 and local_path[2] == ":":
                local_path = local_path[1:]
            path = Path(local_path)
        else:
            path = Path(uri)
        return path
    # If it's http/https, we might need to download it, but for now we assume local file access for kfrags
    # In a real PRE system, the kfrag might be encrypted and stored on IPFS too.
    console.print(f"[yellow]Unsupported kfrag URI scheme '{parsed.scheme}'.[/]")
    return None


if __name__ == "__main__":
    main()


