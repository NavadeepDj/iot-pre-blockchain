from __future__ import annotations

import json
from base64 import b64decode, b64encode
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

from cryptography.hazmat.primitives import hashes
from umbral import keys, pre

from ..config import settings


KEYS_FILE = settings.data_dir / "owner_keys.json"


@dataclass
class OwnerKeyPair:
    private_key: keys.SecretKey
    public_key: keys.PublicKey


def _serialize_keypair(privkey: keys.SecretKey, pubkey: keys.PublicKey) -> None:
    KEYS_FILE.write_text(
        json.dumps(
            {
                "private_key": b64encode(privkey.to_secret_bytes()).decode("ascii"),
                "public_key": b64encode(bytes(pubkey)).decode("ascii"),
            },
            indent=2,
        )
    )


def _deserialize_keypair() -> OwnerKeyPair:
    blob = json.loads(KEYS_FILE.read_text())
    priv = keys.SecretKey.from_bytes(b64decode(blob["private_key"]))
    pub = keys.PublicKey.from_bytes(b64decode(blob["public_key"]))
    return OwnerKeyPair(private_key=priv, public_key=pub)


def load_or_create_owner_keys() -> OwnerKeyPair:
    """
    Load Umbral keys from disk, generating them if this is the first run.
    """
    if KEYS_FILE.exists():
        return _deserialize_keypair()

    priv = keys.SecretKey.random()
    pub = priv.public_key()
    _serialize_keypair(priv, pub)
    return OwnerKeyPair(private_key=priv, public_key=pub)


def encrypt_payload(payload: bytes, public_key: keys.PublicKey) -> Tuple[bytes, bytes]:
    """
    Encrypt plaintext bytes, returning ciphertext + capsule bytes.
    """
    capsule, ciphertext = pre.encrypt(public_key, payload)
    return ciphertext, bytes(capsule)


def sha256_digest(data: bytes) -> str:
    digest = hashes.Hash(hashes.SHA256())
    digest.update(data)
    return digest.finalize().hex()

