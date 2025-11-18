from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    """Typed configuration for all backend components."""

    eth_rpc_url: str
    contract_address: str
    ipfs_api_url: str
    owner_address: str
    owner_private_key: Optional[str]
    proxy_private_key: Optional[str]
    data_dir: Path

    @staticmethod
    def load(env_file: str | Path | None = None) -> "Settings":
        """
        Load settings from the environment (optionally reading an .env file).
        """
        load_dotenv(dotenv_path=env_file)

        data_dir = Path(os.getenv("DATA_DIR", "./data")).resolve()
        data_dir.mkdir(parents=True, exist_ok=True)

        return Settings(
            eth_rpc_url=os.environ.get("ETH_RPC_URL", "http://127.0.0.1:8545"),
            contract_address=os.environ.get("CONTRACT_ADDRESS", ""),
            ipfs_api_url=os.environ.get("IPFS_API_URL", "/ip4/127.0.0.1/tcp/5001"),
            owner_address=os.environ.get("OWNER_ADDRESS", "0xOwner"),
            owner_private_key=os.environ.get("OWNER_PRIVATE_KEY"),
            proxy_private_key=os.environ.get("PROXY_PRIVATE_KEY"),
            data_dir=data_dir,
        )


settings = Settings.load()

