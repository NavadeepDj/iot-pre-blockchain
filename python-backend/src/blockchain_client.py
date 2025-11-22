from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional

from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3 import Web3
from web3.contract.contract import Contract
from web3.exceptions import ContractLogicError

from .config import settings


class BlockchainUnavailable(Exception):
    """Raised when the blockchain layer is not configured or reachable."""


class MissingPrivateKey(Exception):
    """Raised when a write-operation is attempted without OWNER_PRIVATE_KEY."""


ARTIFACT_PATH = (
    Path(__file__).resolve().parents[2]
    / "blockchain"
    / "out"
    / "Registry.sol"
    / "Registry.json"
)


def _load_artifact() -> dict[str, Any]:
    if not ARTIFACT_PATH.exists():
        raise BlockchainUnavailable(
            f"DataRegistry artifact not found at {ARTIFACT_PATH}. "
            "Run `forge build` inside the blockchain workspace first."
        )
    return json.loads(ARTIFACT_PATH.read_text())


def _ensure_connection(w3: Web3) -> None:
    if not w3.is_connected():
        raise BlockchainUnavailable(
            f"Unable to connect to ETH_RPC_URL ({settings.eth_rpc_url}). "
            "Make sure Anvil/Hardhat is running."
        )


def get_data_registry_client(require_private_key: bool = False) -> Optional["DataRegistryClient"]:
    """
    Helper to safely create a client if settings are present.
    Returns None if CONTRACT_ADDRESS / RPC are missing.
    """
    if not settings.contract_address or not settings.eth_rpc_url:
        return None
    try:
        return DataRegistryClient(require_private_key=require_private_key)
    except BlockchainUnavailable:
        return None


@dataclass
class TxResult:
    tx_hash: str
    block_number: int


class DataRegistryClient:
    def __init__(self, require_private_key: bool = False):
        if not settings.eth_rpc_url or not settings.contract_address:
            raise BlockchainUnavailable("ETH_RPC_URL and CONTRACT_ADDRESS must be configured.")

        artifact = _load_artifact()
        abi = artifact["abi"]

        self.w3 = Web3(Web3.HTTPProvider(settings.eth_rpc_url))
        _ensure_connection(self.w3)

        self.contract: Contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(settings.contract_address), abi=abi
        )
        self.chain_id = self.w3.eth.chain_id

        self._account: Optional[LocalAccount] = None
        if settings.owner_private_key:
            self._account = Account.from_key(settings.owner_private_key)
        elif require_private_key:
            raise MissingPrivateKey("Set OWNER_PRIVATE_KEY to send transactions.")

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------
    def register_data(self, cid: str, data_hash_hex: str, sensor_id: str) -> TxResult:
        payload = self.contract.functions.registerData(
            cid, self._hex_to_bytes32(data_hash_hex), sensor_id
        )
        receipt = self._broadcast(payload)
        return TxResult(receipt.transactionHash.hex(), receipt.blockNumber)

    def grant_access(self, cid: str, recipient: str, recipient_public_key: str, kfrag_uri: str) -> TxResult:
        payload = self.contract.functions.grantAccess(
            cid, Web3.to_checksum_address(recipient), recipient_public_key, kfrag_uri
        )
        receipt = self._broadcast(payload)
        return TxResult(receipt.transactionHash.hex(), receipt.blockNumber)

    def complete_access(self, cid: str, recipient: str, reencrypted_cid: str) -> TxResult:
        payload = self.contract.functions.completeAccess(
            cid, Web3.to_checksum_address(recipient), reencrypted_cid
        )
        receipt = self._broadcast(payload)
        return TxResult(receipt.transactionHash.hex(), receipt.blockNumber)

    # ------------------------------------------------------------------
    # Read helpers
    # ------------------------------------------------------------------
    def get_record(self, cid: str) -> dict[str, Any]:
        record = self.contract.functions.getRecord(self._record_id(cid)).call()
        return {
            "cid": record[0],
            "dataHash": record[1],
            "sensorId": record[2],
            "owner": record[3],
            "createdAt": record[4],
        }

    def get_record_by_id(self, record_id: bytes) -> dict[str, Any]:
        record = self.contract.functions.getRecord(record_id).call()
        return {
            "cid": record[0],
            "dataHash": record[1],
            "sensorId": record[2],
            "owner": record[3],
            "createdAt": record[4],
        }

    def get_grant(self, cid: str, recipient: str) -> dict[str, Any]:
        grant_id = self.w3.keccak(text=cid + recipient) # This might be wrong if solidity uses abi.encodePacked
        # Solidity: keccak256(abi.encodePacked(_cid, _recipient))
        # Python web3.solidity_keccak(['string', 'address'], [cid, recipient])
        grant_id = Web3.solidity_keccak(['string', 'address'], [cid, Web3.to_checksum_address(recipient)])
        
        grant = self.contract.functions.getGrant(grant_id).call()
        # Struct: cid, recipient, recipientPublicKey, kfragUri, reencryptedCid, processed, createdAt
        return {
            "cid": grant[0],
            "recipient": grant[1],
            "recipientPublicKey": grant[2],
            "kfragUri": grant[3],
            "reencryptedCid": grant[4],
            "processed": grant[5],
            "createdAt": grant[6],
        }

    def fetch_access_granted_events(self, from_block: int, to_block: Optional[int] = None):
        event = self.contract.events.AccessGranted()
        return event.get_logs(from_block=from_block, to_block=to_block or "latest")

    def current_block(self) -> int:
        return self.w3.eth.block_number

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _broadcast(self, tx_func) -> Any:
        if not self._account:
            raise MissingPrivateKey("OWNER_PRIVATE_KEY is required to send transactions.")

        nonce = self.w3.eth.get_transaction_count(self._account.address)
        gas_price = self.w3.eth.gas_price
        tx = tx_func.build_transaction(
            {
                "from": self._account.address,
                "nonce": nonce,
                "gas": 500_000,
                "gasPrice": gas_price,
                "chainId": self.chain_id,
            }
        )
        signed = self._account.sign_transaction(tx)
        raw_tx = getattr(signed, "rawTransaction", None)
        if raw_tx is None:
            raw_tx = getattr(signed, "raw_transaction", None)
        if raw_tx is None:
            raw_tx = signed["raw_transaction"]
        tx_hash = self.w3.eth.send_raw_transaction(raw_tx)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt

    @staticmethod
    def _hex_to_bytes32(value: str) -> bytes:
        clean = value.lower().removeprefix("0x")
        if len(clean) != 64:
            raise ValueError("Expected 32-byte hex string for data hash.")
        return bytes.fromhex(clean)

    def _record_id(self, cid: str) -> bytes:
        return self.w3.keccak(text=cid)

