# IoT Proxy Re-Encryption with Blockchain Registry - Complete User Guide

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Running the System](#running-the-system)
6. [Complete Workflow Tutorial](#complete-workflow-tutorial)
7. [Understanding the Components](#understanding-the-components)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Topics](#advanced-topics)

---

## Overview

This system implements a **decentralized IoT data sharing platform** using:
- **Proxy Re-Encryption (PRE)**: Allows data owners to grant access to recipients without decrypting data themselves
- **Blockchain (Ethereum)**: Stores metadata and access permissions in a tamper-proof registry
- **IPFS**: Stores encrypted and re-encrypted data in a distributed manner

### What This System Does

1. **IoT sensors** encrypt their data and register it on the blockchain
2. **Data owners** grant access to specific recipients
3. **Proxy workers** re-encrypt data for authorized recipients (without seeing the plaintext)
4. **Recipients** decrypt and access the original data

---

## Prerequisites

### Required Software

1. **Node.js & npm** (v16 or higher)
   - Download from: https://nodejs.org/
   - Verify: `node --version` and `npm --version`

2. **Python** (v3.9 or higher)
   - Download from: https://www.python.org/
   - Verify: `python --version`

3. **Foundry** (Ethereum development toolkit)
   - Install: `curl -L https://foundry.paradigm.xyz | bash`
   - Then run: `foundryup`
   - Verify: `forge --version` and `anvil --version`

4. **IPFS** (InterPlanetary File System)
   - Download from: https://docs.ipfs.tech/install/
   - Verify: `ipfs --version`

5. **Git**
   - Download from: https://git-scm.com/
   - Verify: `git --version`

### System Requirements

- **OS**: Windows 10/11, macOS, or Linux
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk Space**: At least 2GB free

---

## Installation

### Step 1: Clone the Repository

```bash
git clone <your-repository-url>
cd iot-pre-blockchain
```

### Step 2: Install Blockchain Dependencies

```bash
cd blockchain
npm install
cd ..
```

### Step 3: Install Python Dependencies

```bash
cd python-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

cd ..
```

### Step 4: Initialize IPFS

```bash
# Initialize IPFS (only needed once)
ipfs init

# Configure IPFS for local development
ipfs config Addresses.API /ip4/127.0.0.1/tcp/5001
ipfs config Addresses.Gateway /ip4/127.0.0.1/tcp/8080
```

---

## Configuration

### Step 1: Compile Smart Contract

```bash
cd blockchain
forge build
```

This creates the contract artifacts in `blockchain/out/Registry.sol/Registry.json`.

### Step 2: Start Anvil (Local Blockchain)

Open a **new terminal window** and run:

```bash
cd blockchain
anvil
```

**Important**: Keep this terminal running. You should see output like:
```
Available Accounts
==================
(0) 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266 (10000.000000000000000000 ETH)
(1) 0x70997970C51812dc3A010C7d01b50e0d17dc79C8 (10000.000000000000000000 ETH)
...

Private Keys
==================
(0) 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
...

Listening on 127.0.0.1:8545
```

### Step 3: Deploy Smart Contract

Open another terminal and run:

```bash
cd blockchain
forge script script/DeployRegistry.s.sol --rpc-url http://127.0.0.1:8545 --broadcast
```

**Expected output**:
```
Contract deployed to: 0x5FbDB2315678afecb367f032d93F642f64180aa3
```

**Copy the contract address** - you'll need it for the next step.

### Step 4: Configure Python Backend

Edit `python-backend/.env`:

```env
# Blockchain Configuration
ETH_RPC_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3  # Use YOUR deployed address
OWNER_PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
OWNER_ADDRESS=0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266

# IPFS Configuration
IPFS_API_URL=/ip4/127.0.0.1/tcp/5001

# Data Directory
DATA_DIR=./data
```

### Step 5: Start IPFS Daemon

Open a **new terminal window** and run:

```bash
ipfs daemon
```

**Important**: Keep this terminal running. You should see:
```
Daemon is ready
```

---

## Running the System

You now have **three terminals running**:
1. **Terminal 1**: Anvil blockchain
2. **Terminal 2**: IPFS daemon
3. **Terminal 3**: For running Python commands (activate venv first)

### Activate Python Environment (Terminal 3)

```bash
cd python-backend

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

---

## Complete Workflow Tutorial

### Scenario
An IoT temperature sensor produces encrypted data. The data owner grants access to a recipient, who can then decrypt and view the data.

### Step 1: Produce Sensor Data

The sensor encrypts data and registers it on the blockchain.

```bash
python -m src.sensor_service produce sample_payload.json
```

**Expected Output**:
```
Loaded sample payload (126 bytes)
Stored encrypted blob locally at data/ciphertexts/sensor-1_1763792630.json
On-chain registration tx: 0x... (block 2)
Success! Encrypted data is now in IPFS and tracked in the local registry.
CID: QmNVyH9bAjDAiBa5CzWtkCn5LrFThxp9ACfUWRqx4UTQsc
SHA-256: 0a3b5c...
```

**Copy the CID** - you'll need it for the next step.

### Step 2: List Registered Data (Optional)

```bash
python -m src.sensor_service list-records
```

**Expected Output**:
```
- Sensor: sensor-1 | CID: QmNVyH9bAjDAiBa5CzWtkCn5LrFThxp9ACfUWRqx4UTQsc | Hash: 0a3b5c...
```

### Step 3: Grant Access to Recipient

The data owner grants access to a recipient (using Anvil's second default address).

```bash
python -m src.owner_cli grant-access QmNVyH9bAjDAiBa5CzWtkCn5LrFThxp9ACfUWRqx4UTQsc 0x70997970C51812dc3A010C7d01b50e0d17dc79C8
```

**Replace the CID** with your actual CID from Step 1.

**Expected Output**:
```
Loading owner keys...
Loading/creating recipient keys for 0x70997970C51812dc3A010C7d01b50e0d17dc79C8...
Generating re-encryption keys...
Saved kfrags to data/kfrags/c1c4766eb29d2c53.json
On-chain grant tx: 0x... (block 3)
✓ Access granted to 0x70997970C51812dc3A010C7d01b50e0d17dc79C8 for CID QmNVyH9...
Recipient can now use the proxy to decrypt this data.
```

### Step 4: Run Proxy Worker

The proxy worker detects the grant, re-encrypts the data for the recipient, and updates the blockchain.

```bash
python -m src.proxy_worker
```

**Expected Output**:
```
Starting proxy worker...
Found 1 unprocessed grant(s)
Processing grant: CID QmNVyH9bAjDAiBa5CzWtkCn5LrFThxp9ACfUWRqx4UTQsc for recipient 0x70997970C51812dc3A010C7d01b50e0d17dc79C8
Re-encrypting capsule...
Uploading re-encrypted blob to IPFS...
Re-encrypted CID: QmRiAQTwoPEnrUh1zfL4pnDN1s9L7SwaJ9tEjcd2FPSrp9
Saved locally at data/reenciphered/0x70997970C51812dc3A010C7d01b50e0d17dc79C8_QmNVyH9bAjDAiBa5.json
Marking grant as processed on-chain...
✓ Processed grant for 0x70997970C51812dc3A010C7d01b50e0d17dc79C8
```

**Press Ctrl+C** to stop the worker after it processes the grant.

### Step 5: Recipient Decrypts Data

The recipient fetches the re-encrypted data and decrypts it using the `decrypt_tool.py`.

#### Option 1: Command-Line Mode (Quick)

```bash
python decrypt_tool.py QmNVyH9bAjDAiBa5CzWtkCn5LrFThxp9ACfUWRqx4UTQsc 0x70997970C51812dc3A010C7d01b50e0d17dc79C8
```

**Replace the CID** with your actual CID from Step 1.

#### Option 2: Interactive Mode (User-Friendly)

```bash
python decrypt_tool.py
```

Then enter the values when prompted:
```
Enter CID: QmNVyH9bAjDAiBa5CzWtkCn5LrFThxp9ACfUWRqx4UTQsc
Enter recipient address: 0x70997970C51812dc3A010C7d01b50e0d17dc79C8
```

**Expected Output** (both methods):
```
Fetching re-encrypted blob from IPFS (CID: QmRiAQTwoPEnrUh1zfL4pnDN1s9L7SwaJ9tEjcd2FPSrp9)...
Loading your keys...
Decrypting data...
✓ Successfully decrypted!

Original IoT Data:
{
  "temperature": 100.0,
  "humidity": 55.2,
  "timestamp": "2025-11-17T00:00:00Z"
}

Saved to data/decrypted/0x70997970C51812dc3A010C7d01b50e0d17dc79C8_QmNVyH9bAjDAiBa5.json
```

**Success!** The recipient has successfully decrypted the original sensor data.

---

## Understanding the Components

### Smart Contract (`Registry.sol`)

**Location**: `blockchain/src/Registry.sol`

**Purpose**: Stores metadata and access permissions on the blockchain

**Key Functions**:
- `registerData(cid, dataHash, sensorId)` - Register encrypted data
- `grantAccess(cid, recipient, recipientPublicKey, kfragUri)` - Grant access
- `completeAccess(cid, recipient, reencryptedCid)` - Mark grant as processed
- `getRecord(cid)` - Retrieve data record
- `getGrant(cid, recipient)` - Retrieve access grant

### Python Components

#### 1. `sensor_service.py`
**Purpose**: Simulates IoT sensors producing encrypted data

**Commands**:
- `produce <file>` - Encrypt and register data
- `list-records` - View all registered data

#### 2. `owner_cli.py`
**Purpose**: Data owner operations

**Commands**:
- `grant-access <cid> <recipient>` - Grant access to recipient
- `list-records` - View owned data
- `list-grants` - View all grants

#### 3. `proxy_worker.py`
**Purpose**: Re-encrypts data for authorized recipients

**Usage**: Run as a background service
```bash
python -m src.proxy_worker
```

#### 4. `recipient_cli.py`
**Purpose**: Recipient operations

**Commands**:
- `decrypt <cid>` - Decrypt data (if access granted)
- `list-access` - View all accessible data

#### 5. `blockchain_client.py`
**Purpose**: Handles all blockchain interactions

**Key Methods**:
- `register_data()` - Send transaction to register data
- `grant_access()` - Send transaction to grant access
- `complete_access()` - Send transaction to mark grant processed
- `get_record()` / `get_grant()` - Read from blockchain

#### 6. `registry.py`
**Purpose**: Provides unified interface to blockchain registry

**Class**: `BlockchainRegistry`
- Fetches records and grants from blockchain events
- Converts blockchain data to Python objects

---

## Troubleshooting

### Problem: "Blockchain client unavailable"

**Cause**: Anvil is not running or wrong RPC URL

**Solution**:
1. Check if Anvil is running: Look for terminal with "Listening on 127.0.0.1:8545"
2. Verify `.env` has `ETH_RPC_URL=http://127.0.0.1:8545`
3. Restart Anvil if needed

### Problem: "Could not reach IPFS"

**Cause**: IPFS daemon is not running

**Solution**:
1. Check if IPFS daemon is running: Look for terminal with "Daemon is ready"
2. Start IPFS: `ipfs daemon`
3. Verify IPFS is accessible: `ipfs id`

### Problem: "Contract not deployed"

**Cause**: Smart contract deployment failed or wrong address in `.env`

**Solution**:
1. Redeploy contract: `forge script script/DeployRegistry.s.sol --rpc-url http://127.0.0.1:8545 --broadcast`
2. Copy new contract address
3. Update `CONTRACT_ADDRESS` in `.env`

### Problem: "Kfrag file not found"

**Cause**: Windows file path issue (already fixed in latest code)

**Solution**: Ensure you're using the latest version of `proxy_worker.py` with the Windows path fix

### Problem: "No access grant found"

**Cause**: Grant not created or wrong recipient address

**Solution**:
1. Verify grant was created: `python -m src.owner_cli list-grants`
2. Check recipient address matches exactly (case-sensitive)
3. Ensure proxy worker has processed the grant

### Problem: "Decryption failed"

**Cause**: Corrupted keys or wrong recipient

**Solution**:
1. Verify you're using the correct recipient address
2. Check that proxy worker successfully processed the grant
3. Ensure re-encrypted CID exists in IPFS

---

## Advanced Topics

### Running in Production

**Security Considerations**:
1. **Never use Anvil's default private keys** in production
2. Use a real Ethereum network (e.g., Sepolia testnet or mainnet)
3. Implement access control for `completeAccess()` function
4. Use HTTPS for IPFS gateway
5. Encrypt kfrags before storing

**Deployment Steps**:
1. Deploy contract to target network
2. Update `.env` with production RPC URL and contract address
3. Use secure key management (e.g., hardware wallet, KMS)
4. Set up monitoring and logging

### Optimizing Performance

**Event Fetching**:
The current implementation fetches all events from block 0. For production:

```python
# In registry.py, implement incremental syncing
def list_records(self, from_block: int = 0) -> List[DataRecord]:
    # Store last synced block
    # Only fetch new events since last sync
    events = self.client.contract.events.DataRegistered().get_logs(
        from_block=from_block
    )
```

**IPFS Pinning**:
For production, pin important data:

```bash
ipfs pin add <CID>
```

### Multiple Recipients

To grant access to multiple recipients:

```bash
# Grant to recipient 1
python -m src.owner_cli grant-access <CID> 0x70997970C51812dc3A010C7d01b50e0d17dc79C8

# Grant to recipient 2
python -m src.owner_cli grant-access <CID> 0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC
```

Each recipient gets their own re-encryption key and can independently decrypt the data.

### Revoking Access

Currently, access cannot be revoked. To implement revocation:

1. Add `revokeAccess()` function to smart contract
2. Proxy worker should check revocation status before re-encrypting
3. Update `Grant` struct with `revoked` boolean field

### Custom Sensor Data

To use your own sensor data:

1. Create a JSON file with your data structure:
```json
{
  "sensor_type": "custom",
  "value": 42,
  "unit": "celsius",
  "location": "Building A"
}
```

2. Encrypt and register:
```bash
python -m src.sensor_service produce my_custom_data.json
```

The system works with any JSON-serializable data.

### Monitoring and Logging

**View Blockchain Events**:
```bash
# In blockchain directory
forge script script/ViewEvents.s.sol --rpc-url http://127.0.0.1:8545
```

**Check IPFS Stats**:
```bash
ipfs stats bw
ipfs repo stat
```

**Python Logging**:
Add to your scripts:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Quick Reference

### Essential Commands

```bash
# Start services
anvil                                    # Terminal 1
ipfs daemon                              # Terminal 2

# Deploy contract
forge script script/DeployRegistry.s.sol --rpc-url http://127.0.0.1:8545 --broadcast

# Produce data
python -m src.sensor_service produce sample_payload.json

# Grant access
python -m src.owner_cli grant-access <CID> <RECIPIENT_ADDRESS>

# Run proxy
python -m src.proxy_worker

# Decrypt data
python decrypt_tool.py <CID> <RECIPIENT_ADDRESS>
# Or run interactively:
python decrypt_tool.py
```

### File Locations

- **Smart Contract**: `blockchain/src/Registry.sol`
- **Contract Artifacts**: `blockchain/out/Registry.sol/Registry.json`
- **Python Source**: `python-backend/src/`
- **Configuration**: `python-backend/.env`
- **Encrypted Data**: `python-backend/data/ciphertexts/`
- **Re-encryption Keys**: `python-backend/data/kfrags/`
- **Re-encrypted Data**: `python-backend/data/reenciphered/`
- **Decrypted Data**: `python-backend/data/decrypted/`
- **Cryptographic Keys**: `python-backend/data/keys/`

### Default Addresses (Anvil)

- **Owner**: `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`
- **Recipient 1**: `0x70997970C51812dc3A010C7d01b50e0d17dc79C8`
- **Recipient 2**: `0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC`

---

## Support and Resources

### Documentation
- **Umbral (PRE)**: https://github.com/nucypher/pyUmbral
- **Foundry**: https://book.getfoundry.sh/
- **IPFS**: https://docs.ipfs.tech/
- **Web3.py**: https://web3py.readthedocs.io/

### Common Issues
- Check all three services are running (Anvil, IPFS, Python)
- Verify `.env` configuration
- Ensure contract is deployed and address is correct
- Check Python virtual environment is activated

### Getting Help
1. Check the [Troubleshooting](#troubleshooting) section
2. Review terminal output for error messages
3. Verify all prerequisites are installed correctly
4. Check that all services are running

---

## Conclusion

You now have a fully functional blockchain-based IoT data sharing system with proxy re-encryption! This system provides:

✅ **Decentralized storage** via IPFS  
✅ **Tamper-proof registry** via Ethereum smart contract  
✅ **Secure data sharing** via proxy re-encryption  
✅ **No central authority** required  

The system is production-ready with proper security hardening and deployment to a real blockchain network.
