import requests
from web3 import Web3

print("Checking Anvil...")
try:
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    print(f"Anvil connected: {w3.is_connected()}")
    print(f"Block number: {w3.eth.block_number}")
except Exception as e:
    print(f"Anvil error: {e}")

print("Checking IPFS...")
try:
    # IPFS API usually requires POST for some endpoints, but id is safe
    r = requests.post("http://127.0.0.1:5001/api/v0/id")
    print(f"IPFS status: {r.status_code}")
    print(f"IPFS response: {r.text[:100]}")
except Exception as e:
    print(f"IPFS error: {e}")
