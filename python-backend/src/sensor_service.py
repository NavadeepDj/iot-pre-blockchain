from __future__ import annotations

from base64 import b64encode
import json
import time
from pathlib import Path

import typer
from rich.console import Console

# from config import settings
from .config import settings

from .models import DataRecord
from .registry import LocalRegistry
from .utils.crypto_utils import (
    encrypt_payload,
    load_or_create_owner_keys,
    sha256_digest,
)
from .utils.ipfs_client import get_ipfs_client

app = typer.Typer(help="Mock IoT sensor that produces encrypted payloads.")
console = Console()

REGISTRY = LocalRegistry(settings.data_dir / "registry.json")
CIPHERS_DIR = settings.data_dir / "ciphertexts"
CIPHERS_DIR.mkdir(parents=True, exist_ok=True)


def _store_blob_locally(blob_bytes: bytes, sensor_id: str) -> Path:
    timestamp = int(time.time())
    file_path = CIPHERS_DIR / f"{sensor_id}_{timestamp}.json"
    file_path.write_bytes(blob_bytes)
    return file_path


@app.command()
def produce(
    sample_file: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to the plaintext JSON produced by a mock sensor.",
    ),
    sensor_id: str = typer.Option(
        "sensor-1", help="Logical ID for the sensor producing this payload."
    ),
):
    """
    Encrypt a JSON sample, upload it to IPFS, and log metadata locally.

    Even if the terminology is new, you can think of this command as:
    1. read some sensor data,
    2. lock it with the owner's key,
    3. store the locked blob in IPFS,
    4. remember where we put it (CID + hash) for future sharing.
    """
    payload_bytes = sample_file.read_bytes()
    console.print(f"[bold green]Loaded sample payload[/] ({len(payload_bytes)} bytes)")

    owner_keys = load_or_create_owner_keys()
    ciphertext, capsule = encrypt_payload(payload_bytes, owner_keys.public_key)

    blob = {
        "sensor_id": sensor_id,
        "original_filename": sample_file.name,
        "ciphertext": b64encode(ciphertext).decode("ascii"),
        "capsule": b64encode(capsule).decode("ascii"),
        "note": "ciphertext + capsule are all we need for future re-encryption",
    }
    blob_bytes = json.dumps(blob, indent=2).encode()
    local_path = _store_blob_locally(blob_bytes, sensor_id)
    console.print(f"[cyan]Stored encrypted blob locally at[/] {local_path}")

    try:
        ipfs_client = get_ipfs_client()
        cid = ipfs_client.add_bytes(blob_bytes)
    except Exception as exc:  # noqa: BLE001
        console.print(
            "[red]Could not reach IPFS. Make sure the daemon is running "
            f"(error: {exc}).[/]"
        )
        raise typer.Exit(code=1) from exc

    data_hash = sha256_digest(blob_bytes)
    record = DataRecord(
        cid=cid,
        data_hash=data_hash,
        owner_address=settings.owner_address,
        sensor_id=sensor_id,
    )
    REGISTRY.add_record(record)

    console.print(
        "[bold green]Success![/] "
        "Encrypted data is now in IPFS and tracked in the local registry."
    )
    console.print(f"CID: [magenta]{cid}[/]")
    console.print(f"SHA-256: [magenta]{data_hash}[/]")


@app.command("list-records")
def list_records():
    """
    Show everything the local registry knows about (until the smart contract is live).
    """
    records = REGISTRY.list_records()
    if not records:
        console.print("[yellow]No records yet. Run `produce` first.[/]")
        return

    for record in records:
        console.print(
            f"- Sensor: {record.sensor_id} | CID: {record.cid} | Hash: {record.data_hash}"
        )


if __name__ == "__main__":
    app()

