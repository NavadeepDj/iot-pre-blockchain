# Quick Start Guide

## Terminal 1 — Start Anvil (Local Blockchain)

```bash
cd blockchain
anvil
```

Keep this running. You should see `Listening on 127.0.0.1:8545`.

---

## Terminal 2 — Start IPFS Daemon

```bash
ipfs daemon
```

Keep this running. You should see `Daemon is ready`.

---

## Terminal 3 — Deploy Contract

```bash
cd blockchain
forge script script/DeployRegistry.s.sol --rpc-url http://127.0.0.1:8545 --broadcast
```

You should see: `Contract Address: 0x5FbDB2315678afecb367f032d93F642f64180aa3`

> **Note:** Always deploy the contract **immediately** after starting a fresh Anvil, before running any Python commands. This ensures the contract address stays the same every time.

---

## Terminal 3 — Run the Workflow

### Activate Python environment

```bash
cd python-backend
.\venv\Scripts\activate
```

### Step 1: Produce sensor data

```bash
python -m src.sensor_service produce sample_payload.json
```

Output:
```
CID: QmXyz...
SHA-256: abc123...
```

Copy the **CID** — you need it for the next steps.

### Step 2: Grant access to a recipient

```bash
python -m src.owner_cli grant-access <YOUR_CID> 0x70997970C51812dc3A010C7d01b50e0d17dc79C8
```

Example:
```bash
python -m src.owner_cli grant-access QmNQpEe2tjYcFXt6JXBze6a5N1YB2U7hMDsTJMuGwZfTER 0x70997970C51812dc3A010C7d01b50e0d17dc79C8
```

### Step 3: Run proxy worker

```bash
python -m src.proxy_worker
```

Wait until you see `✓ Processed grant for 0x7099...`, then press **Ctrl+C** to stop.

### Step 4: Decrypt the data

```bash
python decrypt_tool.py <YOUR_CID> 0x70997970C51812dc3A010C7d01b50e0d17dc79C8
```

Example:
```bash
python decrypt_tool.py QmNQpEe2tjYcFXt6JXBze6a5N1YB2U7hMDsTJMuGwZfTER 0x70997970C51812dc3A010C7d01b50e0d17dc79C8
```

Output:
```json
{
  "temperature": 100.0,
  "humidity": 55.2,
  "sensor": "demoNK-station-1",
  "timestamp": "2025-11-17T00:00:00Z"
}
```

---

## Bonus: View Encrypted Data on IPFS via Browser

You can view any IPFS-stored blob directly in your browser using the local gateway:

```
http://127.0.0.1:8080/ipfs/<YOUR_CID>
```

Example:
```
http://127.0.0.1:8080/ipfs/QmQ1MNhkJJVHQn56v7FpyQuzcZFdxL8bv4EhiJFZKAyqsH
```

This shows the **encrypted** JSON blob (ciphertext + capsule) — not the plaintext. Only the authorized recipient can decrypt it.

To just view the web ui of the ipfs: 
WebUI: http://127.0.0.1:5001/webui

---

## Web UI Workflow (Step-by-Step)

Follow these steps to run the full workflow using the browser-based Web UI:

### Terminal 1 — Start Anvil (Local Blockchain)

```bash
cd blockchain
anvil
```

Keep this running. Wait for `Listening on 127.0.0.1:8545`.

### Terminal 2 — Start IPFS Daemon

```bash
ipfs daemon
```

Keep this running. Wait for `Daemon is ready`.

### Terminal 3 — Deploy Smart Contract

```bash
cd blockchain
forge script script/DeployRegistry.s.sol --rpc-url http://127.0.0.1:8545 --broadcast
```

Wait for the contract address output. (Update your `.env` if needed.)

### Terminal 4 — Start Flask API Backend

```bash
cd python-backend
./venv/Scripts/activate   # (Windows)
# or
source venv/bin/activate # (Linux/Mac)
python app.py
```

Keep this running. Wait for `Running on http://127.0.0.1:5000/`.

### Step 5 — Open the Web UI

Open the following file in your browser:

```
web-ui/index.html
```

Or, right-click and choose "Open with" → your browser.

### Step 6 — Use the Web UI

- Use the browser interface to:
  1. Produce (encrypt & register) sensor data
  2. Grant access to a recipient
  3. Run the proxy worker
  4. Decrypt data as a recipient

All actions are performed via the Web UI buttons and forms.

> **Tip:** Make sure all backend services (Anvil, IPFS, Flask API) are running before using the Web UI.

---

## Summary

| Terminal | Command | Keep Running? |
|----------|---------|---------------|
| 1 | `anvil` | Yes |
| 2 | `ipfs daemon` | Yes |
| 3 | `forge script ...` (deploy) | No (one-time) |
| 3 | `python -m src.sensor_service produce ...` | No |
| 3 | `python -m src.owner_cli grant-access ...` | No |
| 3 | `python -m src.proxy_worker` | Stop after processing |
| 3 | `python decrypt_tool.py ...` | No |
