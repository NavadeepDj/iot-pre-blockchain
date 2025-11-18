from __future__ import annotations

import typer
from rich.console import Console

from .config import settings

app = typer.Typer(help="Owner utilities for managing data + re-encryption keys.")
console = Console()


@app.command("register-data")
def register_data(cid: str, data_hash: str, sensor_id: str):
    """
    Placeholder implementation for registering data on-chain.
    """
    console.print(
        f"[cyan]Would register CID={cid} hash={data_hash} sensor={sensor_id} "
        f"using contract {settings.contract_address} on {settings.eth_rpc_url}[/]"
    )
    console.print("[yellow]Smart-contract bindings pending implementation.[/]")


@app.command("grant-access")
def grant_access(recipient_address: str):
    """
    Stub for generating & broadcasting a re-encryption key.
    """
    console.print(
        f"[cyan]Would generate re-encryption key for recipient {recipient_address}[/]"
    )
    console.print(
        "[yellow]PRE key generation not yet wired; ensure pyUmbral is configured.[/]"
    )


if __name__ == "__main__":
    app()

