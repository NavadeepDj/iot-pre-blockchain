from __future__ import annotations

import json
import time
from base64 import b64decode, b64encode
from pathlib import Path

from rich.console import Console

from .config import settings
from .models import AccessGrant
from .registry import LocalRegistry
from .utils.crypto_utils import (
    load_kfrags,
    reencrypt_capsule,
)
from .utils.ipfs_client import get_ipfs_client
from umbral.capsule import Capsule

console = Console()

REGISTRY = LocalRegistry(settings.data_dir / "registry.json")
REENCIPHERED_DIR = settings.data_dir / "reenciphered"
REENCIPHERED_DIR.mkdir(parents=True, exist_ok=True)


def process_grant(grant):
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

    kfrags = load_kfrags(Path(grant.reencryption_key_path))
    if not kfrags:
        console.print(f"[red]Failed to load kfrags from {grant.reencryption_key_path}[/]")
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

    # Update grant with re-encrypted CID
    grant.reencrypted_cid = reencrypted_cid
    grant.processed = True

    # Save updated grant back to registry
    data = REGISTRY._load()
    grants = [AccessGrant(**item) for item in data.get("grants", [])]
    for i, g in enumerate(grants):
        if g.cid == grant.cid and g.recipient_address == grant.recipient_address:
            grants[i] = grant
            break
    data["grants"] = [g.model_dump() for g in grants]
    REGISTRY._save(data)

    # Also save locally for easy access
    local_path = REENCIPHERED_DIR / f"{grant.recipient_address}_{grant.cid[:16]}.json"
    local_path.write_bytes(reencrypted_bytes)
    console.print(f"[green]Saved locally at {local_path}[/]")

    return True


def main(poll_interval: float = 2.0):
    """
    Proxy worker that polls for new access grants and re-encrypts data.

    In a real system, this would listen to blockchain events. For now,
    it polls the local registry for unprocessed grants.
    """
    console.print("[cyan]Proxy worker starting. Polling for access grants...[/]")

    try:
        while True:
            # Get all unprocessed grants
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


if __name__ == "__main__":
    main()

