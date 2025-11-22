"""
Test recipient decryption by modifying the default recipient_id in the code
"""
import sys
sys.path.insert(0, 'src')

from src.recipient_cli import decrypt

# Call decrypt with just the CID, using the modified default
decrypt(
    cid="QmSfcmbbzYFQBYzkLrQM3AQwgUbbap2u7gfyhX6BfUW2Ks",
    recipient_id="0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
)
