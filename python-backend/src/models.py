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
    recipient_public_key: Optional[str] = Field(
        default=None, description="Base64-encoded recipient's Umbral public key"
    )
    reencryption_key_path: Optional[str] = Field(
        default=None, description="Path/URI to stored re-encryption key material (kfrags)"
    )
    reencrypted_cid: Optional[str] = Field(
        default=None, description="IPFS CID of the re-encrypted blob (set by proxy)"
    )
    processed: bool = Field(default=False, description="Whether proxy has processed this grant")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

