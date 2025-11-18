from __future__ import annotations

import json
from pathlib import Path
from typing import List

from .models import DataRecord


class LocalRegistry:
    """
    Simplified metadata store until the smart contract is ready.

    The registry persists JSON under data/registry.json so that the flow can be
    demonstrated without spinning up blockchain tooling.
    """

    def __init__(self, registry_path: Path):
        self.registry_path = registry_path
        if not self.registry_path.exists():
            self.registry_path.write_text("[]")

    def add_record(self, record: DataRecord) -> None:
        records = self._load()
        records.append(record.model_dump())
        self.registry_path.write_text(json.dumps(records, indent=2, default=str))

    def list_records(self) -> List[DataRecord]:
        return [DataRecord(**item) for item in self._load()]

    def _load(self) -> list:
        return json.loads(self.registry_path.read_text())

