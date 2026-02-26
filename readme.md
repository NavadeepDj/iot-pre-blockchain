## IoT PRE + Blockchain Data Sharing – README

This project is a complete working example of **privacy‑preserving IoT data sharing** using:

- **IoT devices (simulated)** → produce JSON sensor data
- **Proxy Re‑Encryption (PRE, Umbral)** → encrypt once, share with multiple recipients
- **IPFS** → off‑chain, content‑addressed storage for encrypted blobs
- **Ethereum smart contract (Foundry/Anvil)** → registry + access control + audit trail
- **Python backend** → CLI tools, workers, and (optionally) an API that orchestrate the flow
- **Web UI (optional)** → visual layer for demos

It’s designed so someone can read this document and easily build a **presentation (PPT)** explaining the system and demo it live.

---

## 1. Problem & Goals

### 1.1 Problem

Typical IoT data flows:

- Devices push **raw or weakly protected data** to a server.
- Access control is often implemented with central DB flags or API keys.
- Once data is stored, the operator (or an attacker) can often read everything.

We want:

- End‑to‑end encrypted IoT data (even the server can’t read plaintext).
- Fine‑grained, auditable access control for **who** can decrypt **which** data.
- Off‑chain storage for large blobs (IPFS) with on‑chain metadata and permissions.

### 1.2 Goals

- **Encrypt once, share many**: the device encrypts with an owner key; later, the owner can grant access to new recipients without re‑uploading or re‑encrypting the raw data.
- **Proxy Re‑Encryption**: a proxy transforms ciphertexts for recipients without seeing plaintext.
- **Blockchain registry**: smart contract holds:
  - **What** exists: CID + hash + owner + sensor ID
  - **Who** can access: grant/revoke events for each CID and recipient
- **IPFS storage**: data is referenced by CID; integrity enforced by content hash.
- **Developer‑friendly tooling**: Foundry (Forge/Anvil) for contracts, Python for crypto + glue, small CLIs to demo flows.

---

## 2. High‑Level Architecture

### 2.1 Components

- **IoT Sensor (Python)**  
  `python-backend/src/sensor_service.py`  
  - Reads sensor JSON (e.g., `sample_payload.json`).
  - Encrypts it using **Umbral** with the owner’s public key.
  - Wraps ciphertext + PRE capsule into a JSON blob.
  - Stores blob:
    - Locally under `python-backend/data/ciphertexts/…`
    - On IPFS → gets a **CID**.
  - Registers record:
    - On‑chain (DataRegistry contract) if blockchain is configured.
    - In local registry (for caching / simpler local flows).

- **Owner CLI (Python)**  
  `python-backend/src/owner_cli.py`  
  - Generates and stores **re‑encryption key fragments** (kfrags) for a recipient.
  - Records an **AccessGrant**:
    - Optionally on‑chain (`grantAccess` call on DataRegistry).
    - Also saves kfrags on disk (`data/kfrags/...`) and logs their location.

- **Proxy Worker (Python)**  
  `python-backend/src/proxy_worker.py`  
  - Periodically:
    - Looks up access grants (local registry and/or on‑chain events).
    - Fetches original encrypted blob from IPFS by CID.
    - Uses kfrags to re‑encrypt the capsule for the recipient.
    - Uploads **re‑encrypted blob** to IPFS (new CID).
    - Updates the grant as “processed” with the re‑encrypted CID.
  - Proxy never sees plaintext; it only sees ciphertext, capsules, and kfrags.

- **Recipient CLI (Python)**  
  `python-backend/src/recipient_cli.py`  
  - Given a CID and a `recipient_id`:
    - Checks that there’s a processed grant for that CID + recipient.
    - Downloads the re‑encrypted blob from IPFS.
    - Decrypts it using the recipient’s Umbral private key and the owner’s public key.
    - Prints the original IoT JSON and saves it to `data/decrypted/...`.

- **Smart Contract: DataRegistry (Solidity)**  
  `blockchain/src/Counter.sol` (renamed logically to DataRegistry)  
  - Stores **DataRecord**:
    - `cid` (IPFS CID for the encrypted blob)
    - `dataHash` (SHA‑256 of the encrypted blob)
    - `sensorId` (logical device ID)
    - `owner` (Ethereum address)
    - `createdAt` (timestamp)
  - Stores **Grant**:
    - `recipient` (address)
    - `kfragURI` (location of re‑encryption material – e.g., `file://...` or IPFS)
  - Emits events:
    - `DataRegistered(recordId, cid, dataHash, sensorId, owner)`
    - `AccessGranted(recordId, owner, recipient, kfragURI)`
    - `AccessRevoked(recordId, owner, recipient)`

- **Blockchain Client (Python)**  
  `python-backend/src/blockchain_client.py`  
  - Loads the contract ABI (`blockchain/out/...`) and address.
  - Provides methods:
    - `register_data(cid, sha256_hex, sensor_id)`
    - `grant_access(cid, recipient_address, ...)`
    - `fetch_access_granted_events(...)`
    - `get_record(cid)` and `get_grant(...)`
  - Signs transactions with `OWNER_PRIVATE_KEY`.

- **Web UI + start script**  
  - `start-web-ui.bat`:
    - Opens Anvil, IPFS daemon, Flask API (if present), static web server for `web-ui/`, and browser at `http://localhost:8080`.
  - Good for demos once back and front are configured.

---

## 3. Data Flow – End to End

### 3.1 Encrypt & Upload (Owner / Sensor)

1. Sensor script reads a JSON sample.
2. Encrypts payload with owner’s Umbral public key:
   - Produces `ciphertext` and `capsule`.
3. Creates encrypted blob JSON:

   ```json
   {
     "sensor_id": "sensor-1",
     "original_filename": "sample_payload.json",
     "ciphertext": "<base64 ciphertext>",
     "capsule": "<base64 capsule>",
     "note": "ciphertext + capsule are all we need for future re-encryption"
   }
   ```

4. Saves blob locally and uploads to IPFS:
   - IPFS returns **CID** (e.g. `QmRwW6m...`).
5. Computes SHA‑256 of the blob.
6. Registers record:
   - On‑chain via `DataRegistry.registerData(cid, dataHash, sensorId)`.
   - And/or in local registry JSON.

### 3.2 Grant Access (Owner → Recipient)

1. Owner chooses:
   - `cid` of the IoT data.
   - `recipient_address` (Ethereum address from Anvil).
2. Owner CLI:
   - Ensures keys exist (owner + recipient).
   - Calls pyUmbral to generate **kfrags** (re‑encryption key fragments).
   - Saves kfrags to disk, e.g. `data/kfrags/<grant_id>.json`.
   - Builds `kfragURI` (e.g. `file:///C:/.../kfrags/<grant_id>.json`).
   - Calls `DataRegistry.grantAccess(recordId, recipient, kfragURI)`.
   - Optionally adds the grant to local registry cache.

### 3.3 Re‑Encrypt (Proxy)

1. Proxy worker is running continuously:
   - Subscribes to `AccessGranted` events, and/or reads local registry.
2. When it finds an unprocessed grant:
   - Fetches original blob by CID from IPFS.
   - Extracts `ciphertext` and `capsule`.
   - Loads kfrags from `kfragURI`.
   - Applies `pre.reencrypt(...)` to build a **cfrag** (capsule fragment).
   - Constructs a new re‑encrypted blob:

     ```json
     {
       "original_cid": "<CID>",
       "recipient": "<recipient address>",
       "ciphertext": "<same base64 ciphertext>",
       "original_capsule": "<base64 original capsule>",
       "cfrag": "<base64 capsule fragment>",
       "note": "This blob contains the re-encrypted capsule fragment (cfrag) that the recipient needs to decrypt"
     }
     ```

   - Uploads this re‑encrypted blob to IPFS (new **CID**).
   - Updates the grant record with:
     - `reencrypted_cid`
     - `processed = true`

### 3.4 Decrypt (Recipient)

1. Recipient knows:
   - Original CID.
   - Their `recipient_id` (which maps to their Umbral keys).
2. Recipient CLI:
   - Looks up the grant for `(cid, recipient_id)`.
   - Confirms it is `processed` and has a `reencrypted_cid`.
   - Fetches re‑encrypted blob from IPFS.
   - Loads recipient private key and owner’s public key.
   - Uses `pre.decrypt_reencrypted(...)` with capsule + cfrag:
     - Recovers symmetric key.
     - Decrypts `ciphertext` to plaintext JSON.
   - Prints and saves the decrypted IoT data.

---

## 4. Repository Structure

At the top level:

- `project_description.md` / `project_MVP.md` / `Complete_Project_Description.md`  
  Design documents describing goals, MVP, and extended features.
- `USER_GUIDE.md`  
  Longer, human‑oriented walkthrough.
- `total_working_example.md`  
  A short, end‑to‑end command transcript for reference.
- `blockchain/`  
  Foundry project with `DataRegistry` smart contract:
  - `src/Counter.sol` → holds the DataRegistry contract.
  - `test/Counter.t.sol` → tests for register/grant/revoke flows.
  - `script/Counter.s.sol` → deployment script.
- `python-backend/`
  - `venv/` – Python virtual environment.
  - `requirements.txt` – Python deps (FastAPI, Umbral, web3, etc.).
  - `sample_payload.json` – example IoT JSON.
  - `PRE_WORKFLOW.md` – PRE‑only workflow guide.
  - `src/`
    - `config.py` – loads `.env`: RPC URL, contract address, keys, IPFS URL.
    - `models.py` – `DataRecord`, `AccessGrant`.
    - `sensor_service.py` – CLI for IoT sensor (produce, list‑records).
    - `owner_cli.py` – CLI for owner (register‑data, grant‑access, list‑grants).
    - `proxy_worker.py` – proxy process for PRE re‑encryption.
    - `recipient_cli.py` – CLI for recipients (decrypt, list‑access).
    - `blockchain_client.py` – typed client for the DataRegistry contract.
    - `registry.py` – registry abstraction (chain vs local file).
    - `utils/crypto_utils.py` – Umbral key management, encryption, PRE helpers.
    - `utils/ipfs_client.py` – IPFS HTTP client wrapper.
  - `data/`
    - `ciphertexts/` – encrypted IoT blobs.
    - `kfrags/` – re‑encryption key fragments.
    - `reenciphered/` – re‑encrypted blobs for recipients.
    - `decrypted/` – decrypted JSON payloads.

- `start-web-ui.bat`
  - Launch script to start Anvil, IPFS, Flask API, and static web UI.

---

## 5. Setup & Prerequisites

### 5.1 Tools

- **Python 3.11+**
- **Node.js** (if you use any Node‑based tooling or web UI; not strictly required for backend/chain).
- **Git**
- **IPFS** (Kubo)
- **Foundry**:
  - Install via:

    ```powershell
    # In PowerShell with Git Bash installed
    & 'C:\Program Files\Git\bin\bash.exe' -lc "curl -L https://foundry.paradigm.xyz | bash"
    & 'C:\Program Files\Git\bin\bash.exe' -lc "source ~/.bashrc && foundryup"
    ```

  - Add to PATH for your PowerShell session:

    ```powershell
    $env:PATH = "$env:USERPROFILE\.foundry\bin;$env:PATH"
    ```

  - Check:

    ```powershell
    forge --version
    ```

### 5.2 Python backend

```powershell
cd C:\Users\navad\iot-pre-blockchain\python-backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 5.3 Smart contract build & deploy

From the `blockchain` folder:

```powershell
cd C:\Users\navad\iot-pre-blockchain\blockchain
forge build
anvil   # keep this window open (local chain)
```

In another window:

```powershell
cd C:\Users\navad\iot-pre-blockchain\blockchain
$env:PATH = "$env:USERPROFILE\.foundry\bin;$env:PATH"

forge script script/Counter.s.sol `
  --rpc-url http://127.0.0.1:8545 `
  --private-key 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80 `
  --broadcast
```

- Note the contract address from the output (e.g. `0x5FbDB2...`).

### 5.4 Configure `.env` for Python

In `python-backend`:

```powershell
cd C:\Users\navad\iot-pre-blockchain\python-backend
copy env.example .env
```

Edit `.env`:

```env
ETH_RPC_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
IPFS_API_URL=/ip4/127.0.0.1/tcp/5001
OWNER_PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
OWNER_ADDRESS=0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
DATA_DIR=./data
```

Start IPFS:

```powershell
ipfs daemon
```

---

## 6. Demo: Full PRE + Blockchain Flow

### 6.1 Produce IoT data (encrypt + upload + register)

```powershell
cd C:\Users\navad\iot-pre-blockchain\python-backend
.\venv\Scripts\activate

python -m src.sensor_service produce sample_payload.json
```

Output should include:

- `On-chain registration tx: ... (block N)`
- `CID: Qm...`
- `SHA-256: ...`

### 6.2 Grant access to a recipient

Choose an Anvil account as recipient, e.g. `(1)`:

- Address: `0x70997970C51812dc3A010C7d01b50e0d17dc79C8`

Run:

```powershell
python -m src.owner_cli grant-access <CID> 0x70997970C51812dc3A010C7d01b50e0d17dc79C8
```

You should see:

- Path to kfrags file under `data/kfrags/...`
- `Success! Access granted to ...`
- `On-chain AccessGranted tx: ... (block M)`

Optionally list grants:

```powershell
python -m src.owner_cli list-grants
```

*(Depending on registry implementation, this may read from chain or local cache.)*

### 6.3 Run proxy worker

In a new terminal:

```powershell
cd C:\Users\navad\iot-pre-blockchain\python-backend
.\venv\Scripts\activate

python -m src.proxy_worker
```

You should see:

- `Proxy worker starting. Polling for access grants...`
- When it finds a grant:
  - `Processing grant: CID ... for recipient ...`
  - `Re-encrypted blob uploaded to IPFS: Qm...`
  - `Saved locally at data/reenciphered/...`

### 6.4 Recipient decrypts

Back in the Python backend terminal:

```powershell
python -m src.recipient_cli decrypt <CID> --recipient-id 0x70997970C51812dc3A010C7d01b50e0d17dc79C8
```

Expected output:

- `✓ Successfully decrypted!`
- Pretty‑printed original JSON (should match `sample_payload.json`).
- Path under `data/decrypted/`.

---

## 7. Optional: Web UI & start script

Once the backend and chain are working, you can use the **start script**:

```powershell
cd C:\Users\navad\iot-pre-blockchain
.\start-web-ui.bat
```

It will:

- Start Anvil (if not already running).
- Start IPFS daemon.
- Start Flask API (`python-backend/app.py`) if present.
- Start a static web server in `web-ui/` at `http://localhost:8080`.
- Open the browser pointing to `http://localhost:8080`.

This is ideal for live demos and PPT screenshots.

---

## 8. How to Turn This Into a PPT

For a presentation, suggested slide sequence:

1. **Motivation & Problem**  
   - Raw IoT data, privacy risk, centralization.
2. **High‑Level Architecture Diagram**  
   - Boxes: Device → PRE → IPFS → Smart Contract → Proxy → Recipient.
   - Highlight trust boundaries.
3. **Data Flow Slides**  
   - Slide per phase: Produce, Grant, Proxy, Decrypt.
4. **Smart Contract Slide**  
   - Show fields of `DataRecord` and `Grant`.
   - Explain events and on‑chain audit.
5. **Crypto Slide (PRE)**  
   - Explain kfrags and cfrags at a conceptual level.
6. **Demo Slides**  
   - Screenshot of:
     - Anvil console (accounts and tx).
     - IPFS WebUI with CID input.
     - Terminal with `produce`, `grant-access`, `proxy_worker`, `decrypt`.
7. **Security & Future Work**  
   - Hardening key storage, kfrag distribution over IPFS, real identity layer, UI improvements.

