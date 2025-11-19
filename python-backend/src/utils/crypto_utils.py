from __future__ import annotations

import json
from base64 import b64decode, b64encode
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

from cryptography.hazmat.primitives import hashes
from umbral import keys, pre
from umbral.capsule import Capsule
from umbral.capsule_frag import VerifiedCapsuleFrag
from umbral.key_frag import VerifiedKeyFrag
from umbral.signing import Signer

from ..config import settings


KEYS_FILE = settings.data_dir / "owner_keys.json"
RECIPIENT_KEYS_DIR = settings.data_dir / "recipient_keys"
RECIPIENT_KEYS_DIR.mkdir(parents=True, exist_ok=True)
KFrags_DIR = settings.data_dir / "kfrags"
KFrags_DIR.mkdir(parents=True, exist_ok=True)


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


# Recipient key management
def load_or_create_recipient_keys(recipient_id: str) -> OwnerKeyPair:
    """
    Load or create recipient keys (same structure as owner keys).
    Each recipient gets their own key file.
    """
    key_file = RECIPIENT_KEYS_DIR / f"{recipient_id}_keys.json"
    if key_file.exists():
        blob = json.loads(key_file.read_text())
        priv = keys.SecretKey.from_bytes(b64decode(blob["private_key"]))
        pub = keys.PublicKey.from_bytes(b64decode(blob["public_key"]))
        return OwnerKeyPair(private_key=priv, public_key=pub)

    priv = keys.SecretKey.random()
    pub = priv.public_key()
    key_file.write_text(
        json.dumps(
            {
                "private_key": b64encode(priv.to_secret_bytes()).decode("ascii"),
                "public_key": b64encode(bytes(pub)).decode("ascii"),
            },
            indent=2,
        )
    )
    return OwnerKeyPair(private_key=priv, public_key=pub)


# PRE functions
def generate_reencryption_keys(
    owner_keys: OwnerKeyPair,
    recipient_pubkey: keys.PublicKey,
    threshold: int = 1,
    shares: int = 1,
) -> List[VerifiedKeyFrag]:
    """
    Generate re-encryption key fragments (kfrags) that allow a proxy to
    re-encrypt data from the owner to the recipient.

    Args:
        owner_keys: Owner's key pair
        recipient_pubkey: Recipient's public key
        threshold: Minimum kfrags needed for decryption (usually 1 for simple case)
        shares: Number of kfrags to generate (usually 1 for simple case)

    Returns:
        List of verified key fragments
    """
    # Create a signer for the owner (needed for kfrag generation)
    signer = Signer(owner_keys.private_key)
    kfrags = pre.generate_kfrags(
        delegating_sk=owner_keys.private_key,
        receiving_pk=recipient_pubkey,
        signer=signer,
        threshold=threshold,
        shares=shares,
    )
    return kfrags


def save_kfrags(kfrags: List[VerifiedKeyFrag], grant_id: str) -> Path:
    """Save kfrags to disk for the proxy to use later."""
    kfrag_file = KFrags_DIR / f"{grant_id}.json"
    kfrag_data = {
        "kfrags": [b64encode(bytes(kfrag.kfrag)).decode("ascii") for kfrag in kfrags]
    }
    kfrag_file.write_text(json.dumps(kfrag_data, indent=2))
    return kfrag_file


def load_kfrags(kfrag_path: Path) -> List[VerifiedKeyFrag]:
    """Load kfrags from disk."""
    from umbral.key_frag import KeyFrag

    blob = json.loads(kfrag_path.read_text())
    kfrags = []
    for kfrag_bytes in blob["kfrags"]:
        kfrag = KeyFrag.from_bytes(b64decode(kfrag_bytes))
        # Note: In a real system, we'd verify the kfrag here
        # For now, we'll trust it (in production, verify against owner/recipient keys)
        kfrags.append(VerifiedKeyFrag(kfrag))
    return kfrags


def reencrypt_capsule(
    capsule: Capsule, kfrag: VerifiedKeyFrag
) -> VerifiedCapsuleFrag:
    """
    Re-encrypt a capsule using a key fragment.
    This is what the proxy does - transforms the capsule so the recipient can decrypt.
    """
    return pre.reencrypt(capsule, kfrag)


def decrypt_reencrypted(
    recipient_keys: OwnerKeyPair,
    owner_pubkey: keys.PublicKey,
    capsule: Capsule,
    cfrags: List[VerifiedCapsuleFrag],
    ciphertext: bytes,
) -> bytes:
    """
    Decrypt re-encrypted data using recipient's private key.
    This is what the recipient does after receiving the re-encrypted capsule fragments.
    """
    return pre.decrypt_reencrypted(
        receiving_sk=recipient_keys.private_key,
        delegating_pk=owner_pubkey,
        capsule=capsule,
        verified_cfrags=cfrags,
        ciphertext=ciphertext,
    )

