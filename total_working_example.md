In your Proxy Re-Encryption system:

IoT device encrypts data with the owner’s public key.

→ C_A = Encrypt(data, Alice_pub)

This encrypted data is uploaded to IPFS.

Blockchain only stores:

CID

Data hash

Owner address

So even if a malicious user finds the CID:

They get only C_A (ciphertext).

They cannot decrypt it — unless they have:

Alice's private key, or

The re-encrypted version made for them

This is why encryption + PRE is essential.