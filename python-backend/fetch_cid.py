from src.registry import BlockchainRegistry
from src.blockchain_client import BlockchainUnavailable

try:
    registry = BlockchainRegistry()
    records = registry.list_records()
    if records:
        # Get the last record
        record = records[-1]
        print(f"Full CID: {record.cid}")
        with open("cid.txt", "w") as f:
            f.write(record.cid)
    else:
        print("No records found")
except Exception as e:
    print(f"Error: {e}")
