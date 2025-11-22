"""
Flask API Backend for IoT PRE Blockchain Web UI

This provides REST API endpoints for the web interface to interact with
the blockchain-based IoT PRE system.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.sensor_service import _store_blob_locally, REGISTRY, CIPHERS_DIR
from src.owner_cli import grant_access as cli_grant_access
from src.proxy_worker import process_grant
from src.recipient_cli import decrypt
from src.config import settings
from src.utils.crypto_utils import (
    encrypt_payload,
    load_or_create_owner_keys,
    sha256_digest,
)
from src.utils.ipfs_client import get_ipfs_client
from src.models import DataRecord
from base64 import b64encode

app = Flask(__name__)
CORS(app)  # Enable CORS for web UI

@app.route('/api/status', methods=['GET'])
def check_status():
    """Check if all services are running"""
    try:
        # Check blockchain
        blockchain_ok = REGISTRY is not None
        
        # Check IPFS
        ipfs_ok = False
        try:
            ipfs_client = get_ipfs_client()
            ipfs_client.id()
            ipfs_ok = True
        except:
            pass
        
        return jsonify({
            'blockchain': blockchain_ok,
            'ipfs': ipfs_ok,
            'contract_address': settings.contract_address if hasattr(settings, 'contract_address') else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/produce', methods=['POST'])
def produce_data():
    """Encrypt sensor data and register on blockchain"""
    try:
        data = request.json
        sensor_data = data.get('data')
        sensor_id = data.get('sensor_id', 'sensor-1')
        
        # Parse JSON if string
        if isinstance(sensor_data, str):
            sensor_data = json.loads(sensor_data)
        
        # Encrypt data
        payload_bytes = json.dumps(sensor_data).encode()
        owner_keys = load_or_create_owner_keys()
        ciphertext, capsule = encrypt_payload(payload_bytes, owner_keys.public_key)
        
        # Create blob
        blob = {
            "sensor_id": sensor_id,
            "ciphertext": b64encode(ciphertext).decode("ascii"),
            "capsule": b64encode(capsule).decode("ascii"),
            "note": "ciphertext + capsule for re-encryption"
        }
        blob_bytes = json.dumps(blob, indent=2).encode()
        
        # Store locally
        local_path = _store_blob_locally(blob_bytes, sensor_id)
        
        # Upload to IPFS
        ipfs_client = get_ipfs_client()
        cid = ipfs_client.add_bytes(blob_bytes)
        
        # Register on blockchain
        data_hash = sha256_digest(blob_bytes)
        receipt = REGISTRY.client.register_data(cid, data_hash, sensor_id)
        
        return jsonify({
            'success': True,
            'cid': cid,
            'data_hash': data_hash,
            'tx_hash': receipt.tx_hash,
            'block_number': receipt.block_number,
            'local_path': str(local_path)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/grant-access', methods=['POST'])
def grant_access_api():
    """Grant access to a recipient"""
    try:
        data = request.json
        cid = data.get('cid')
        recipient = data.get('recipient')
        
        if not cid or not recipient:
            return jsonify({'error': 'CID and recipient are required'}), 400
        
        # Load keys
        owner_keys = load_or_create_owner_keys()
        
        # Import necessary functions
        from src.utils.crypto_utils import load_or_create_recipient_keys, generate_reencryption_keys
        from pathlib import Path
        import time
        
        # Load recipient keys
        recipient_keys = load_or_create_recipient_keys(recipient)
        
        # Generate kfrags
        kfrags = generate_reencryption_keys(
            owner_keys=owner_keys,
            recipient_pubkey=recipient_keys.public_key,
            threshold=1,
            shares=1
        )
        
        # Save kfrags
        kfrags_dir = settings.data_dir / "kfrags"
        kfrags_dir.mkdir(parents=True, exist_ok=True)
        
        import hashlib
        kfrag_id = hashlib.sha256(f"{cid}{recipient}".encode()).hexdigest()[:16]
        kfrag_path = kfrags_dir / f"{kfrag_id}.json"
        
        # kfrags are VerifiedKeyFrag objects, need to access .kfrag attribute
        kfrag_data = {"kfrags": [b64encode(bytes(kf.kfrag)).decode('ascii') for kf in kfrags]}
        kfrag_path.write_text(json.dumps(kfrag_data))
        
        # Grant access on blockchain
        kfrag_uri = f"file:///{kfrag_path.as_posix()}"
        recipient_pk_b64 = b64encode(bytes(recipient_keys.public_key)).decode('ascii')
        
        receipt = REGISTRY.client.grant_access(
            cid=cid,
            recipient=recipient,
            recipient_public_key=recipient_pk_b64,
            kfrag_uri=kfrag_uri
        )
        
        return jsonify({
            'success': True,
            'recipient': recipient,
            'kfrag_path': str(kfrag_path),
            'tx_hash': receipt.tx_hash,
            'block_number': receipt.block_number
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/run-proxy', methods=['POST'])
def run_proxy_api():
    """Run proxy worker to process grants"""
    try:
        # Get unprocessed grants
        all_grants = REGISTRY.list_grants()
        unprocessed = [g for g in all_grants if not g.processed]
        
        if not unprocessed:
            return jsonify({
                'success': True,
                'processed_count': 0,
                'message': 'No unprocessed grants found'
            })
        
        # Process first grant
        grant = unprocessed[0]
        success = process_grant(grant)
        
        if success:
            # Get the re-encrypted CID
            updated_grant = REGISTRY.get_grant(grant.cid, grant.recipient_address)
            
            return jsonify({
                'success': True,
                'processed_count': 1,
                'cid': grant.cid,
                'recipient': grant.recipient_address,
                'reencrypted_cid': updated_grant.reencrypted_cid if updated_grant else None
            })
        else:
            return jsonify({'error': 'Failed to process grant'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/decrypt', methods=['POST'])
def decrypt_api():
    """Decrypt data for recipient"""
    try:
        data = request.json
        cid = data.get('cid')
        recipient_id = data.get('recipient_id')
        
        if not cid or not recipient_id:
            return jsonify({'error': 'CID and recipient_id are required'}), 400
        
        # Get grant
        grant = REGISTRY.get_grant(cid, recipient_id)
        if not grant:
            return jsonify({'error': 'No access grant found'}), 404
        
        if not grant.processed:
            return jsonify({'error': 'Grant not yet processed by proxy'}), 400
        
        if not grant.reencrypted_cid:
            return jsonify({'error': 'Re-encrypted CID not found'}), 404
        
        # Fetch re-encrypted blob
        ipfs_client = get_ipfs_client()
        reencrypted_blob_bytes = ipfs_client.cat(grant.reencrypted_cid)
        reencrypted_blob = json.loads(reencrypted_blob_bytes)
        
        # Parse components
        from base64 import b64decode
        from umbral.capsule import Capsule
        from umbral.capsule_frag import CapsuleFrag, VerifiedCapsuleFrag
        from src.utils.crypto_utils import decrypt_reencrypted, load_or_create_recipient_keys, load_or_create_owner_keys
        
        ciphertext = b64decode(reencrypted_blob["ciphertext"])
        original_capsule = Capsule.from_bytes(b64decode(reencrypted_blob["original_capsule"]))
        cfrag = CapsuleFrag.from_bytes(b64decode(reencrypted_blob["cfrag"]))
        verified_cfrag = VerifiedCapsuleFrag(cfrag)
        
        # Load keys
        recipient_keys = load_or_create_recipient_keys(recipient_id)
        owner_keys = load_or_create_owner_keys()
        
        # Decrypt
        plaintext = decrypt_reencrypted(
            recipient_keys=recipient_keys,
            owner_pubkey=owner_keys.public_key,
            capsule=original_capsule,
            cfrags=[verified_cfrag],
            ciphertext=ciphertext,
        )
        
        # Parse decrypted data
        decrypted_data = json.loads(plaintext)
        
        return jsonify({
            'success': True,
            'data': decrypted_data,
            'cid': cid,
            'recipient': recipient_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/list-records', methods=['GET'])
def list_records_api():
    """List all registered data records"""
    try:
        records = REGISTRY.list_records()
        return jsonify({
            'success': True,
            'records': [
                {
                    'cid': r.cid,
                    'sensor_id': r.sensor_id,
                    'data_hash': r.data_hash,
                    'owner': r.owner_address,
                    'created_at': r.created_at.isoformat()
                }
                for r in records
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/list-grants', methods=['GET'])
def list_grants_api():
    """List all access grants"""
    try:
        grants = REGISTRY.list_grants()
        return jsonify({
            'success': True,
            'grants': [
                {
                    'cid': g.cid,
                    'recipient': g.recipient_address,
                    'processed': g.processed,
                    'reencrypted_cid': g.reencrypted_cid,
                    'created_at': g.created_at.isoformat()
                }
                for g in grants
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting IoT PRE Blockchain API Server...")
    print("📍 API running at: http://localhost:5000")
    print("🌐 Open web UI at: file:///path/to/web-ui/index.html")
    print("\nMake sure Anvil and IPFS are running!")
    app.run(debug=True, port=5000)
