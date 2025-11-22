import re
try:
    with open("records.txt", "r", encoding="utf-16") as f:
        content = f.read()
        match = re.search(r"CID:\s*(\w+)", content)
        if match:
            cid = match.group(1)
            print(f"Found CID: {cid} (len={len(cid)})")
            with open("cid.txt", "w") as out:
                out.write(cid)
        else:
            print("CID not found")
except Exception as e:
    print(f"Error: {e}")
