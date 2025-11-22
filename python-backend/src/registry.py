from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from .blockchain_client import get_data_registry_client, BlockchainUnavailable
from .models import AccessGrant, DataRecord


class BlockchainRegistry:
    """
    Registry implementation that interacts with the smart contract.
    """

    def __init__(self):
        self.client = get_data_registry_client()
        if not self.client:
            raise BlockchainUnavailable("Blockchain client not available")

    def add_record(self, record: DataRecord) -> None:
        # This is handled by the client directly usually, but we can wrap it.
        # However, the CLI calls register_data on the client directly.
        # We can leave this empty or implement it if we want to unify.
        # For now, let's assume the CLI handles the transaction.
        pass

    def list_records(self) -> List[DataRecord]:
        # Fetch DataRegistered events
        events = self.client.contract.events.DataRegistered().get_logs(from_block=0)
        records = []
        for event in events:
            args = event["args"]
            # We need to fetch full details or just use event data
            # Event has: recordId, cid, owner
            # We need data_hash, sensor_id, created_at
            # We can fetch individual records
            try:
                r = self.client.get_record(args["cid"])
                records.append(DataRecord(
                    cid=r["cid"],
                    data_hash=r["dataHash"].hex(),
                    owner_address=r["owner"],
                    sensor_id=r["sensorId"],
                    created_at=datetime.fromtimestamp(r["createdAt"])
                ))
            except Exception:
                continue
        return records

    def add_grant(self, grant: AccessGrant) -> None:
        # Handled by client transaction
        pass

    def list_grants(self, cid: Optional[str] = None) -> List[AccessGrant]:
        events = self.client.fetch_access_granted_events(from_block=0)
        grants = []
        for event in events:
            args = event["args"]
            event_cid = args["cid"]
            recipient = args["recipient"]
            
            if cid and event_cid != cid:
                continue
                
            try:
                g = self.client.get_grant(event_cid, recipient)
                # g has: cid, recipient, recipientPublicKey, kfragUri, reencryptedCid, processed, createdAt
                grants.append(AccessGrant(
                    cid=g["cid"],
                    owner_address=self.client.get_record(g["cid"])["owner"], # Need owner
                    recipient_address=g["recipient"],
                    recipient_public_key=g["recipientPublicKey"],
                    reencryption_key_path=g["kfragUri"],
                    reencrypted_cid=g["reencryptedCid"] if g["reencryptedCid"] else None,
                    processed=g["processed"],
                    created_at=datetime.fromtimestamp(g["createdAt"])
                ))
            except Exception:
                continue
        return grants

    def get_grant(self, cid: str, recipient_address: str) -> Optional[AccessGrant]:
        try:
            g = self.client.get_grant(cid, recipient_address)
            if not g["cid"]: # Empty struct
                return None
            
            return AccessGrant(
                cid=g["cid"],
                owner_address=self.client.get_record(g["cid"])["owner"],
                recipient_address=g["recipient"],
                recipient_public_key=g["recipientPublicKey"],
                reencryption_key_path=g["kfragUri"],
                reencrypted_cid=g["reencryptedCid"] if g["reencryptedCid"] else None,
                processed=g["processed"],
                created_at=datetime.fromtimestamp(g["createdAt"])
            )
        except Exception:
            return None


