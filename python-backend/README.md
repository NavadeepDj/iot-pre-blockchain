# Python Backend Prototype

This folder hosts the Python reference implementation that glues IoT data producers, proxy re-encryption, IPFS storage, and blockchain coordination together.

## Layout

- `venv/` – local virtual environment (already created).
- `requirements.txt` – dependency lock for pip installs into the venv.
- `src/`
  - `config.py` – environment + settings loader.
  - `models.py` – shared dataclasses/pydantic models for data records.
  - `registry.py` – temporary local metadata store (until the Solidity contract is in place).
  - `sensor_service.py` – mock IoT producer that now encrypts data, uploads to IPFS, and records metadata.
  - `owner_cli.py` – helper CLI for owners to register data and generate re-encryption keys (stub).
  - `proxy_worker.py` – long-running worker that listens to blockchain events and performs blind re-encryption using pyUmbral (stub).
  - `recipient_cli.py` – consumer workflow to fetch re-encrypted data and decrypt locally (stub).
  - `utils/` – helpers for crypto + IPFS connectivity.

## Getting Started

```powershell
cd python-backend
.\venv\Scripts\activate
pip install -r requirements.txt   # pulls umbral directly from GitHub (requires git)
copy env.example .env             # configure RPC/IPFS endpoints + addresses
python -m src.sensor_service produce sample_payload.json
python -m src.sensor_service list-records
```

- `produce` now performs real encryption with Umbral, pushes the blob to IPFS, stores a backup under `data/`, and logs the metadata in `data/registry.json`.
- `list-records` lets you inspect what has been registered without touching blockchain yet.
- Once the smart contract exists we will swap the local registry for on-chain calls and wire the owner/proxy/recipient flows into those bindings.

