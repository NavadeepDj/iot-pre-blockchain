import subprocess

with open("cid.txt", "r") as f:
    cid = f.read().strip()

recipient = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
print(f"Granting access for CID {cid} to {recipient}...")

cmd = [
    r".\venv\Scripts\python.exe",
    "-m", "src.owner_cli",
    "grant-access",
    cid,
    recipient
]

subprocess.run(cmd, check=True)
