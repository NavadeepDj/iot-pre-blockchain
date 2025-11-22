from src.utils.ipfs_client import get_ipfs_client
try:
    print("Connecting to IPFS...")
    client = get_ipfs_client()
    print("Connected. Fetching ID...")
    print(client.id())
except Exception as e:
    print(f"Error: {e}")
