"""Quick debug script to find out why proxy_worker sees no grants."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from src.blockchain_client import get_data_registry_client
from web3 import Web3

client = get_data_registry_client()
print(f"Connected: {client.w3.is_connected()}")
print(f"Current block: {client.current_block()}")

# 1 - Check AccessGranted events directly
print("\n=== AccessGranted events ===")
events = client.fetch_access_granted_events(from_block=0)
print(f"Found {len(events)} event(s)")
for e in events:
    print(f"  grantId: {e['args']['grantId'].hex()}")
    print(f"  cid:     {e['args']['cid']}")
    print(f"  recipient: {e['args']['recipient']}")

# 2 - Try get_grant for each event
print("\n=== Fetching grant details ===")
for e in events:
    cid = e['args']['cid']
    recipient = e['args']['recipient']
    try:
        g = client.get_grant(cid, str(recipient))
        print(f"  Grant found: cid={g['cid']}, processed={g['processed']}, kfragUri={g['kfragUri'][:60]}...")
    except Exception as exc:
        print(f"  ERROR get_grant: {exc}")

    # Also check get_record
    try:
        r = client.get_record(cid)
        print(f"  Record found: cid={r['cid']}, owner={r['owner']}")
    except Exception as exc:
        print(f"  ERROR get_record: {exc}")

# 3 - Try list_grants from the registry
print("\n=== BlockchainRegistry.list_grants() ===")
from src.registry import BlockchainRegistry
reg = BlockchainRegistry()
grants = reg.list_grants()
print(f"Grants returned: {len(grants)}")
for g in grants:
    print(f"  cid={g.cid}, recipient={g.recipient_address}, processed={g.processed}")
