# Proxy Re-Encryption (PRE) Workflow Guide

This guide walks you through the complete PRE workflow: **Owner → Proxy → Recipient**.

## Prerequisites

1. IPFS daemon running: `ipfs daemon`
2. Python venv activated: `.\venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)

## Step-by-Step Workflow

### Step 1: Owner Encrypts and Uploads Data

```powershell
# Produce encrypted IoT data and upload to IPFS
python -m src.sensor_service produce sample_payload.json

# Note the CID that gets printed (e.g., Qmbc8riFXNuhZPMBf9x9mJidPX68y4UvqAMsYijfWifGEt)
```

**What happens:**
- Sensor data is encrypted using owner's public key
- Encrypted blob (ciphertext + capsule) is uploaded to IPFS
- Metadata is stored in local registry

### Step 2: Owner Grants Access to Recipient

```powershell
# Grant access to a recipient (replace CID with the one from Step 1)
python -m src.owner_cli grant-access Qmbc8riFXNuhZPMBf9x9mJidPX68y4UvqAMsYijfWifGEt recipient-1
```

**What happens:**
- Owner generates re-encryption keys (kfrags) for the recipient
- Kfrags are saved to disk
- Access grant is recorded in the registry

### Step 3: Proxy Re-encrypts the Data

```powershell
# Run the proxy worker (it will poll for new grants)
python -m src.proxy_worker

# The worker will:
# - Detect the new grant
# - Fetch the original encrypted blob from IPFS
# - Re-encrypt the capsule using the kfrags
# - Upload the re-encrypted blob to IPFS
# - Mark the grant as processed
```

**What happens:**
- Proxy fetches original ciphertext from IPFS
- Uses kfrags to re-encrypt the capsule (without seeing the plaintext!)
- Uploads re-encrypted blob to IPFS
- Updates grant with new CID

### Step 4: Recipient Decrypts the Data

```powershell
# In a new terminal, recipient decrypts the data
python -m src.recipient_cli decrypt Qmbc8riFXNuhZPMBf9x9mJidPX68y4UvqAMsYijfWifGEt --recipient-id recipient-1
```

**What happens:**
- Recipient checks they have access
- Fetches re-encrypted blob from IPFS
- Decrypts using their private key
- Displays the original IoT data!

## Quick Test Script

You can also test the full flow in one go:

```powershell
# Terminal 1: Start IPFS
ipfs daemon

# Terminal 2: Run the full workflow
python -m src.sensor_service produce sample_payload.json
# Copy the CID from output

python -m src.owner_cli grant-access <CID> recipient-1

# Terminal 3: Run proxy (leave it running)
python -m src.proxy_worker

# Back to Terminal 2: Wait a few seconds, then decrypt
python -m src.recipient_cli decrypt <CID> --recipient-id recipient-1
```

## Understanding the Flow

1. **Encryption (Owner)**: Data encrypted once with owner's public key → stored in IPFS
2. **Key Generation (Owner)**: Re-encryption keys (kfrags) created for specific recipient
3. **Re-encryption (Proxy)**: Proxy transforms the capsule using kfrags (blind operation - proxy never sees plaintext)
4. **Decryption (Recipient)**: Recipient uses their private key to decrypt the re-encrypted data

## Key Files Created

- `data/owner_keys.json` - Owner's encryption keys
- `data/recipient_keys/recipient-1_keys.json` - Recipient's keys
- `data/kfrags/<grant_id>.json` - Re-encryption key fragments
- `data/reenciphered/` - Re-encrypted blobs (local copies)
- `data/decrypted/` - Decrypted data (for recipients)
- `data/registry.json` - All records and grants

## Next Steps

Once you understand this flow, we can add the blockchain layer to:
- Store metadata on-chain (instead of local registry)
- Emit access grant events that the proxy listens to
- Provide tamper-proof audit logs

