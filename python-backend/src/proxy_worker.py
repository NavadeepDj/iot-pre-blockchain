from __future__ import annotations

import time

from rich.console import Console

from .config import settings

console = Console()


def main(poll_interval: float = 2.0):
    """
    Placeholder loop that would listen for blockchain events.
    """
    console.print(
        "[cyan]Proxy worker starting. Waiting for AccessGranted events from "
        f"{settings.contract_address or 'UNSET'}[/]"
    )

    try:
        while True:
            # TODO: integrate web3.py filters + pyUmbral re-encryption.
            console.print("[yellow]No events yet (stub loop)...[/]", end="\r")
            time.sleep(poll_interval)
    except KeyboardInterrupt:
        console.print("\n[green]Proxy worker stopped.[/]")


if __name__ == "__main__":
    main()

