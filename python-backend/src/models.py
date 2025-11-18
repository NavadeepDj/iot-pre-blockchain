from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DataRecord(BaseModel):
    """
    Representation of an IoT data artifact registered on-chain.
    """

    cid: str = Field(..., description="IPFS content identifier for ciphertext blob")
    data_hash: str = Field(..., description="Hash of the ciphertext")
    owner_address: str = Field(..., description="Ethereum address of data owner")
    sensor_id: str = Field(..., description="Logical sensor identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AccessGrant(BaseModel):
    """
    Permission event emitted / consumed by smart contracts & services.
    """

    cid: str
    owner_address: str
    recipient_address: str
    reencryption_key_path: Optional[str] = Field(
        default=None, description="Path to stored re-encryption key material"
    )
    expires_at: Optional[datetime] = None

