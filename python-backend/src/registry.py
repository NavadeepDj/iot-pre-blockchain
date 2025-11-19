from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from .models import AccessGrant, DataRecord


class LocalRegistry:
    """
    Simplified metadata store until the smart contract is ready.

    The registry persists JSON under data/registry.json so that the flow can be
    demonstrated without spinning up blockchain tooling.
    """

    def __init__(self, registry_path: Path):
        self.registry_path = registry_path
        if not self.registry_path.exists():
            self.registry_path.write_text('{"records": [], "grants": []}')
        else:
            # Migrate old format (list) to new format (dict)
            self._migrate_if_needed()

    def _migrate_if_needed(self) -> None:
        """Migrate old registry format (list) to new format (dict with records/grants)."""
        try:
            content = self.registry_path.read_text()
            data = json.loads(content)
            # If it's a list, convert to new format
            if isinstance(data, list):
                self.registry_path.write_text(
                    json.dumps({"records": data, "grants": []}, indent=2, default=str)
                )
        except (json.JSONDecodeError, KeyError):
            # If corrupted, reset to empty
            self.registry_path.write_text('{"records": [], "grants": []}')

    def add_record(self, record: DataRecord) -> None:
        data = self._load()
        records = [DataRecord(**item) for item in data.get("records", [])]
        records.append(record)
        data["records"] = [r.model_dump() for r in records]
        self._save(data)

    def list_records(self) -> List[DataRecord]:
        data = self._load()
        return [DataRecord(**item) for item in data.get("records", [])]

    def add_grant(self, grant: AccessGrant) -> None:
        """Add an access grant (permission for recipient to access a CID)."""
        data = self._load()
        grants = [AccessGrant(**item) for item in data.get("grants", [])]
        grants.append(grant)
        data["grants"] = [g.model_dump() for g in grants]
        self._save(data)

    def list_grants(self, cid: Optional[str] = None) -> List[AccessGrant]:
        """List all grants, optionally filtered by CID."""
        data = self._load()
        grants = [AccessGrant(**item) for item in data.get("grants", [])]
        if cid:
            grants = [g for g in grants if g.cid == cid]
        return grants

    def get_grant(self, cid: str, recipient_address: str) -> Optional[AccessGrant]:
        """Get a specific grant for a CID and recipient."""
        grants = self.list_grants(cid)
        for grant in grants:
            if grant.recipient_address == recipient_address:
                return grant
        return None

    def _load(self) -> dict:
        return json.loads(self.registry_path.read_text())

    def _save(self, data: dict) -> None:
        self.registry_path.write_text(json.dumps(data, indent=2, default=str))

