# Python Backend Prototype

This folder hosts the Python reference implementation that glues IoT data producers, proxy re-encryption, IPFS storage, and blockchain coordination together.

## Layout

- `venv/` – local virtual environment (already created).
- `requirements.txt` – dependency lock for pip installs into the venv.
- `src/`
  - `config.py` – environment + settings loader.
  - `models.py` – shared dataclasses/pydantic models for data records.
- `registry.py` – local metadata store (still used for caching / persistence).
- `sensor_service.py` – mock IoT producer that encrypts data, uploads to IPFS, records metadata, and now auto-registers the record on-chain.
- `owner_cli.py` – helper CLI for owners to register data, generate re-encryption keys, and emit on-chain `grantAccess` transactions.
- `proxy_worker.py` – worker that listens for on-chain `AccessGranted` events (plus local registry) and performs blind re-encryption using pyUmbral.
- `recipient_cli.py` – consumer workflow to fetch re-encrypted data and decrypt locally.
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

- `produce` performs real encryption with Umbral, pushes the blob to IPFS, stores a backup under `data/`, logs the metadata in `data/registry.json`, and (if configured) registers the record on the `DataRegistry` smart contract.
- `list-records` lets you inspect what has been registered locally.

## Blockchain Integration

The Python services can talk directly to the Foundry `DataRegistry` contract.

1. **Run Anvil (or any RPC endpoint)**
   ```powershell
   cd blockchain
   anvil
   ```

2. **Deploy the contract**
   ```powershell
   forge script script/Counter.s.sol --rpc-url http://127.0.0.1:8545 `
       --private-key <DEPLOYER_PK> --broadcast
   ```
   Copy the deployed address and set it as `CONTRACT_ADDRESS` in `.env`. Use the same private key for `OWNER_PRIVATE_KEY` if you want `sensor_service` / `owner_cli` to send transactions.

3. **Use the CLIs**
   ```powershell
   # Register a record (if the automatic registration failed)
   python -m src.owner_cli register-data <CID> <SHA256_HEX> <SENSOR_ID>

   # Grant access - generates kfrags, stores them locally, and emits AccessGranted on-chain
   python -m src.owner_cli grant-access <CID> <0xRecipientAddress>

   # Proxy worker now watches the blockchain for AccessGranted events
   python -m src.proxy_worker
   ```

If `CONTRACT_ADDRESS` or `OWNER_PRIVATE_KEY` are missing, the commands gracefully fall back to the local registry so you can continue testing without a chain.

