from src.models import DataRecord
from datetime import datetime

print("Fields:", DataRecord.model_fields if hasattr(DataRecord, "model_fields") else DataRecord.__fields__)

try:
    r = DataRecord(
        cid="QmTest",
        data_hash="0x123",
        owner_address="0xOwner",
        sensor_id="sensor-1",
        created_at=datetime.now()
    )
    print("Success:", r)
except Exception as e:
    print("Error:", e)
