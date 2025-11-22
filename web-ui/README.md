# Web UI for IoT PRE Blockchain System

A modern, interactive web interface for the IoT Proxy Re-Encryption blockchain system.

## Features

✨ **Beautiful Modern UI** - Clean, gradient-based design with smooth animations  
🔄 **4-Step Workflow** - Visual representation of the complete data sharing process  
📊 **Real-time Status** - Live system status indicators for blockchain and IPFS  
🎯 **Interactive Forms** - Easy-to-use forms with validation and helpful hints  
📋 **Auto-fill** - Copy CIDs between steps with one click  
🎨 **Responsive Design** - Works on desktop, tablet, and mobile devices  

## Architecture

```
┌─────────────────┐
│   Web Browser   │  ← User interacts with HTML/CSS/JS interface
└────────┬────────┘
         │ HTTP/REST API
┌────────▼────────┐
│  Flask Backend  │  ← Python API server (app.py)
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    │         │          │          │
┌───▼───┐ ┌──▼──┐  ┌────▼────┐ ┌──▼──┐
│Sensor │ │Owner│  │  Proxy  │ │Recip│
│Service│ │ CLI │  │ Worker  │ │ CLI │
└───┬───┘ └──┬──┘  └────┬────┘ └──┬──┘
    │        │           │         │
    └────────┴───────────┴─────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
   ┌────▼────┐          ┌────▼────┐
   │Blockchain│          │  IPFS   │
   │ (Anvil) │          │ Daemon  │
   └─────────┘          └─────────┘
```

## Setup Instructions

### 1. Install Additional Dependencies

```bash
cd python-backend
pip install -r requirements-api.txt
```

This installs:
- `flask` - Web framework for the API
- `flask-cors` - Enable cross-origin requests from the browser

### 2. Start the Services

You need **4 terminals** running:

#### Terminal 1: Anvil Blockchain
```bash
cd blockchain
anvil
```

#### Terminal 2: IPFS Daemon
```bash
ipfs daemon
```

#### Terminal 3: Flask API Server
```bash
cd python-backend
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
python app.py
```

You should see:
```
🚀 Starting IoT PRE Blockchain API Server...
📍 API running at: http://localhost:5000
🌐 Open web UI at: file:///path/to/web-ui/index.html

Make sure Anvil and IPFS are running!
 * Running on http://127.0.0.1:5000
```

#### Terminal 4: Web Server (Optional)

For better security, serve the HTML file via HTTP:

```bash
cd web-ui
python -m http.server 8080
```

Then open: http://localhost:8080

### 3. Open the Web UI

**Option 1: Direct File Access**
- Open `web-ui/index.html` in your browser
- File path: `file:///C:/Users/navad/iot-pre-blockchain/web-ui/index.html`

**Option 2: HTTP Server (Recommended)**
- Start the Python HTTP server (see Terminal 4 above)
- Navigate to: http://localhost:8080

## Using the Web UI

### Step 1: Produce Sensor Data

1. Edit the sensor data JSON (or use the default)
2. Set the sensor ID
3. Click **🚀 Encrypt & Register**
4. Wait for confirmation with CID and transaction hash
5. **Copy the CID** - you'll need it for Step 2

### Step 2: Grant Access

1. Paste the CID from Step 1 (or click **📋 Copy from Step 1**)
2. Select a recipient address from the dropdown
3. Click **✅ Grant Access**
4. Wait for confirmation with transaction details

### Step 3: Run Proxy Worker

1. Click **⚙️ Run Proxy Worker**
2. The proxy will automatically detect and process unprocessed grants
3. Wait for confirmation showing the re-encrypted CID

### Step 4: Decrypt Data

1. Paste the CID from Step 2 (or click **📋 Copy from Step 2**)
2. Select the same recipient address used in Step 2
3. Click **🔓 Decrypt Data**
4. View the original decrypted sensor data!

## API Endpoints

The Flask backend provides the following REST API endpoints:

### `GET /api/status`
Check if blockchain and IPFS are running

**Response:**
```json
{
  "blockchain": true,
  "ipfs": true,
  "contract_address": "0x5FbDB2315678afecb367f032d93F642f64180aa3"
}
```

### `POST /api/produce`
Encrypt and register sensor data

**Request:**
```json
{
  "data": "{\"temperature\": 25.5}",
  "sensor_id": "sensor-1"
}
```

**Response:**
```json
{
  "success": true,
  "cid": "QmXXX...",
  "data_hash": "0xabc...",
  "tx_hash": "0x123...",
  "block_number": 2
}
```

### `POST /api/grant-access`
Grant access to a recipient

**Request:**
```json
{
  "cid": "QmXXX...",
  "recipient": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
}
```

**Response:**
```json
{
  "success": true,
  "recipient": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
  "kfrag_path": "data/kfrags/abc123.json",
  "tx_hash": "0x456...",
  "block_number": 3
}
```

### `POST /api/run-proxy`
Process unprocessed grants

**Response:**
```json
{
  "success": true,
  "processed_count": 1,
  "cid": "QmXXX...",
  "recipient": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
  "reencrypted_cid": "QmYYY..."
}
```

### `POST /api/decrypt`
Decrypt data for recipient

**Request:**
```json
{
  "cid": "QmXXX...",
  "recipient_id": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "temperature": 100.0,
    "humidity": 55.2
  },
  "cid": "QmXXX...",
  "recipient": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
}
```

### `GET /api/list-records`
List all registered data records

### `GET /api/list-grants`
List all access grants

## Troubleshooting

### "Failed to fetch" Error

**Problem:** Browser shows network error when clicking buttons

**Solutions:**
1. Make sure Flask API is running: `python app.py`
2. Check the API is accessible: http://localhost:5000/api/status
3. Verify CORS is enabled (it should be by default)

### "Blockchain client unavailable"

**Problem:** API returns blockchain error

**Solutions:**
1. Ensure Anvil is running in a separate terminal
2. Check `.env` has correct `ETH_RPC_URL=http://127.0.0.1:8545`
3. Verify contract is deployed

### "Could not reach IPFS"

**Problem:** API returns IPFS error

**Solutions:**
1. Ensure IPFS daemon is running: `ipfs daemon`
2. Check IPFS is accessible: `ipfs id`
3. Verify `.env` has correct `IPFS_API_URL`

### Status Indicators Stay Yellow

**Problem:** System status doesn't turn green

**Solution:** The status check is currently simulated in the frontend. For real status checking, the `/api/status` endpoint needs to be called. You can modify the JavaScript to do this.

## Customization

### Changing Colors

Edit the CSS in `index.html`:

```css
/* Main gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Button gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Adding More Recipients

Edit the dropdown in `index.html`:

```html
<select id="recipient-address">
    <option value="0x70997970C51812dc3A010C7d01b50e0d17dc79C8">Recipient 1</option>
    <option value="0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC">Recipient 2</option>
    <option value="YOUR_ADDRESS_HERE">Your Custom Recipient</option>
</select>
```

### Modifying Default Sensor Data

Edit the textarea default value in `index.html`:

```html
<textarea id="sensor-data">{
  "temperature": 25.5,
  "humidity": 60.0,
  "pressure": 1013.25,
  "location": "Building A"
}</textarea>
```

## Security Notes

⚠️ **This UI is for demonstration purposes only**

For production use:
1. Add authentication/authorization
2. Use HTTPS for all connections
3. Implement rate limiting
4. Validate all inputs server-side
5. Use environment variables for sensitive data
6. Deploy to a proper web server (not file://)

## File Structure

```
web-ui/
├── index.html          # Main web interface
└── README.md          # This file

python-backend/
├── app.py             # Flask API server
└── requirements-api.txt  # Additional dependencies
```

## Next Steps

1. **Deploy to Production**: Use a real Ethereum network (Sepolia, Mainnet)
2. **Add Authentication**: Implement user login and session management
3. **Real-time Updates**: Use WebSockets for live status updates
4. **Data Visualization**: Add charts and graphs for sensor data
5. **Mobile App**: Create React Native or Flutter mobile version

## Support

For issues or questions:
1. Check the main [USER_GUIDE.md](../USER_GUIDE.md)
2. Review the [Troubleshooting](#troubleshooting) section above
3. Ensure all 4 services are running (Anvil, IPFS, Flask API, Web UI)

---

**Enjoy your blockchain-powered IoT data sharing system!** 🚀
