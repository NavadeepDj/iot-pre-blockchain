(venv) PS C:\Users\navad\iot-pre-blockchain\python-backend> python -m src.sensor_service produce sample_payload.json
Loaded sample payload (126 bytes)
Stored encrypted blob locally at 
C:\Users\navad\iot-pre-blockchain\python-backend\data\ciphertexts\sensor-1_
1772198762.json
On-chain registration tx: 
94160f60ba1749d680954f07c562243b2182ff480f3a5d9322149e7e8d390586 (block 4) 
Success! Encrypted data is now in IPFS and tracked in the local registry.
CID: QmS2A5RpxrnCGgDY8byg9G4Yz6ZgX6JLB4ybdSj8YCM9DC
SHA-256: 7cd6eb421ff3cfc83e35f96522e61118d12af75cb7b4bef72be55383034fa849  
(venv) PS C:\Users\navad\iot-pre-blockchain\python-backend> python -m src.owner_cli grant-access QmS2A5RpxrnCGgDY8byg9G4Yz6ZgX6JLB4ybdSj8YCM9DC 0x70997970C51812dc3A010C7d01b50e0d17dc79C8
Loading owner keys...
Loading/creating recipient keys for 
0x70997970C51812dc3A010C7d01b50e0d17dc79C8...
Generating re-encryption keys...
Saved kfrags to
C:\Users\navad\iot-pre-blockchain\python-backend\data\kfrags\d762724010a15e
ae.json
Success! Access granted to 0x70997970C51812dc3A010C7d01b50e0d17dc79C8 for 
CID QmS2A5RpxrnCGgDY8byg9G4Yz6ZgX6JLB4ybdSj8YCM9DC
On-chain AccessGranted tx: 
d638cbd508162e84bb0f33ca0735fa00df389f207c758a5e50ddd89a8e6068f6 (block 5) 
Recipient can now use the proxy to decrypt this data.
(venv) PS C:\Users\navad\iot-pre-blockchain\python-backend> python -m src.proxy_worker
Proxy worker starting. Polling for access grants...
Found 1 unprocessed grant(s)
Processing grant: CID QmS2A5RpxrnCGgDY8byg9G4Yz6ZgX6JLB4ybdSj8YCM9DC for   
recipient 0x70997970C51812dc3A010C7d01b50e0d17dc79C8
Re-encrypting capsule...
Re-encrypted blob uploaded to IPFS: 
QmVnu6hHRxZEtExtwJJWctgiTY45s4eJNCZpYH7jpnLmhe
Updated grant on chain: 
394f5a6ea000af136290b6a6fd03596083296524bad4ed9e44092394d6baf0c5
Saved locally at
C:\Users\navad\iot-pre-blockchain\python-backend\data\reenciphered\0x709979
70C51812dc3A010C7d01b50e0d17dc79C8_QmS2A5RpxrnCGgDY.json
✓ Processed grant for 0x70997970C51812dc3A010C7d01b50e0d17dc79C8
No unprocessed grants. Waiting...
Proxy worker stopped.

(venv) PS C:\Users\navad\iot-pre-blockchain\python-backend> python decrypt_tool.py QmNVyH9bAjDAiBa5CzWtkCn5LrFThxp9ACfUWRqx4UTQsc 0x70997970C51812dc3A010C7d01b50e0d17dc79C8
Decrypting data...
  CID: QmNVyH9bAjDAiBa5CzWtkCn5LrFThxp9ACfUWRqx4UTQsc
  Recipient: 0x70997970C51812dc3A010C7d01b50e0d17dc79C8

Error: No access grant found for 0x70997970C51812dc3A010C7d01b50e0d17dc79C8
on CID QmNVyH9bAjDAiBa5CzWtkCn5LrFThxp9ACfUWRqx4UTQsc
Make sure the owner has granted you access first.

Error:
(venv) PS C:\Users\navad\iot-pre-blockchain\python-backend> python decrypt_tool.py QmS2A5RpxrnCGgDY8byg9G4Yz6ZgX6JLB4ybdSj8YCM9DC 0x70997970C51812dc3A010C7d01b50e0d17dc79C8
Decrypting data...
  CID: QmS2A5RpxrnCGgDY8byg9G4Yz6ZgX6JLB4ybdSj8YCM9DC
  Recipient: 0x70997970C51812dc3A010C7d01b50e0d17dc79C8

Fetching re-encrypted blob from IPFS (CID: 
QmVnu6hHRxZEtExtwJJWctgiTY45s4eJNCZpYH7jpnLmhe)...
Loading your keys...
Decrypting data...
✓ Successfully decrypted!

Original IoT Data:
{
  "temperature": 100.0,
  "humidity": 55.2,
  "sensor": "demoNK-station-1",
  "timestamp": "2025-11-17T00:00:00Z"
}

Saved to 
C:\Users\navad\iot-pre-blockchain\python-backend\data\decrypted\0x70997970C
51812dc3A010C7d01b50e0d17dc79C8_QmS2A5RpxrnCGgDY.json
(venv) PS C:\Users\navad\iot-pre-blockchain\python-backend> 

SO okay can you see that evrthing is working above...???

and can you tell me what is teh address you changed in the env?  and is that the cause of error? if so why? and do i have ti chnaage it again when i cahbge the anvil?
and what ist this anvil?




Everything is working perfectly now! Here are your answers:

---

### What address did I change?

I changed `CONTRACT_ADDRESS` in your .env from:
```
0x5FbDB2315678afecb367f032d93F642f64180aa3  →  0x9fe46736679d2d9a65f0992f2272de9f3c7fa6e0
```

### Why did it cause the error?

**Anvil is an in-memory blockchain** — it runs entirely in RAM. When you close/restart Anvil, **all data is wiped** (contracts, transactions, blocks — everything goes back to zero).

Here's what happened:

1. You deployed the contract **before** → it went to address `0x5FbDB...`
2. Anvil was restarted at some point → all state wiped
3. Your .env still pointed to `0x5FbDB...` — but **no contract existed there anymore**
4. Your `produce` and `grant-access` commands appeared to succeed, but they were sending transactions to an **empty address** — no actual contract logic ran, no events were emitted
5. When the proxy worker looked for `AccessGranted` events on-chain → it found **0 events** → "No unprocessed grants"

After I re-deployed, the contract landed at a **different address** (`0x9fe46...`) because the deployer account's nonce had already been incremented by those earlier (no-op) transactions.

### Do you need to change it every time you restart Anvil?

**Yes.** Every time you restart Anvil, you must:

1. **Re-deploy the contract**: `forge script script/DeployRegistry.s.sol --rpc-url http://127.0.0.1:8545 --broadcast`
2. **Check the new address** from the output (or from `broadcast/DeployRegistry.s.sol/31337/run-latest.json`)
3. **Update .env** with the new `CONTRACT_ADDRESS`

If it's a **fresh Anvil** (no prior transactions), the address will always be `0x5FbDB2315678afecb367f032d93F642f64180aa3` because the deployer nonce starts at 0. It only changes if the nonce is different.

### What is Anvil?

**Anvil** is a **local Ethereum blockchain simulator** that comes with the [Foundry](https://book.getfoundry.sh/) toolkit. Think of it as a fake blockchain running on your computer for development and testing:

- Runs locally at `http://127.0.0.1:8545`
- Gives you **10 pre-funded accounts** with 10,000 ETH each (fake ETH, obviously)
- Mines blocks instantly (no waiting)
- **In-memory only** — restarting it resets everything
- Free to use — no real money involved

It's the equivalent of a sandbox where you can deploy contracts, send transactions, and test your app without touching a real blockchain like Ethereum mainnet.