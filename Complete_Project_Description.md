
#  ** System Architecture (High-Level View)**

### **Core Components**

- **IoT Data Producer (Sensor / Owner app)**  
    Encrypts data locally and uploads encrypted files to IPFS.
    
- **Owner Application**  
    Manages who can access the IoT data by generating secure sharing permissions.
    
- **Proxy Re-Encryption (PRE) Worker**  
    Converts the owner’s encrypted data into a form that only the selected recipient can decrypt — **without ever seeing the plaintext**.
    
- **Recipient Application**  
    Fetches re-encrypted IoT data and decrypts it using the recipient’s own private key.
    
- **Decentralized Storage (IPFS)**  
    Stores encrypted data and re-encrypted data, ensuring decentralization and tamper resistance.
    
- **Blockchain (Future Integration)**  
    Stores metadata, access permissions, and audit logs in a tamper-proof way.
    

### **Execution Environment**

- **Python Backend** → Encryption, PRE logic, upload/download from IPFS.
    
- **IPFS Daemon** → Runs locally to store encrypted data pieces.
    
- **Foundry / Anvil Blockchain** → Local blockchain for testing smart contracts.
    
- **JSON Registry (Temporary)** → Holds data records until blockchain is fully integrated.
    

---

# Data Flow Overview (Simple & Visual)**

### **1. IoT Sensor → Owner**

- Sensor data (JSON) is encrypted using the owner’s public key.
    
- Encrypted packet + capsule uploaded to IPFS.
    
- A record (CID + hash + timestamp) is stored locally.
    

### **2. Owner → Proxy**

- Owner decides to share data with a recipient.
    
- Owner generates a **re-encryption key** (kfrag) for the recipient.
    
- This permission is stored in the registry.
    

### **3. Proxy → IPFS**

- Proxy detects the access request.
    
- It fetches encrypted data from IPFS.
    
- Performs PRE transformation.
    
- Uploads re-encrypted data back to IPFS.
    
- Updates registry with new CID.
    

### **4. Recipient → IoT Data**

- Recipient fetches re-encrypted CID from registry/IPFS.
    
- Uses their private key to decrypt.
    
- Receives original IoT data securely.
    

### **5. Blockchain (Planned)**

- Replace JSON registry with blockchain contract.
    
- Events drive proxy automation.
    
- Permanent audit trail.
    

---

#  Data Structures **

### **Data Stored Per IoT Record**

- **CID (IPFS Address)**
    
- **Hash** for integrity
    
- **Owner Address**
    
- **Sensor ID**
    
- **Timestamp**
    

### **Access Grant Structure**

- Recipient ID / Address
    
- Path to re-encryption key (kfrag)
    
- Re-encrypted CID (after proxy processes)
    
- Status (Processed or Pending)
    
    

---

# Platforms, Libraries & Technologies Used**

### **1. Python Backend**

Used for encryption, re-encryption, and data processing.

- **pyUmbral** → Performs encryption & proxy re-encryption
    
- **Typer** → Builds clean command-line tools
    
- **ipfshttpclient** → Stores & retrieves encrypted data from IPFS
    
- **Pydantic** → Data validation (DataRecord, AccessGrant)
    
- **Rich** → Colored terminal output
    
- **dotenv** → Loads environment configuration
    
- **SHA-256** → Ensures integrity of payload
    

---

### **2. IPFS (InterPlanetary File System)**

- Stores ciphertexts in decentralized chunks
    
- Returns a **CID** (like a permanent content address)
    
- Prevents data tampering & central server dependency
    

---

### **3. Blockchain (Solidity + Foundry + Anvil)**

Later used for:

- Storing metadata
    
- Storing access permissions
    
- Generating tamper-proof event logs
    
- Making sharing auditable
    

_Currently local but ready for integration._

---

### **4. System Processes**

- **Owner encrypts data**
    
- **Proxy re-encrypts without seeing plaintext**
    
- **Recipient decrypts**
    
- **IPFS stores encrypted data only**
    
- **Blockchain stores permissions (future)**
    

---

# **Slide 5: Module-to-Module Relationships**

### **Sensor Service**

- Encrypts IoT data
    
- Uploads ciphertext to IPFS
    
- Creates DataRecord entry
    

### **Owner CLI**

- Generates re-encryption (kfrag) keys
    
- Writes AccessGrant → consumed by proxy
    

### **Proxy Worker**

- Reads pending grants
    
- Downloads from IPFS
    
- Performs re-encryption
    
- Uploads new encrypted data
    
- Updates grant state
    

### **Recipient CLI**

- Fetches re-encrypted CID
    
- Decrypts using private key
    
- Retrieves the original IoT data
    

### **Registry (Temporary DB)**

- Stores both DataRecords & AccessGrants
    
- Will be replaced by blockchain smart contract
    

### **Smart Contract (Future)**

- Single point of truth for:
    
    - Records
        
    - Permissions
        
    - Events powering proxy automation
        

---

# High-Level Summary (Non-Technical)**

- IoT data is **encrypted at the source**.
    
- Data is stored on **IPFS**, not on any company server.
    
- Owner can securely share data **without sending private keys or decrypting anything**.
    
- A proxy converts the encrypted file so only the chosen recipient can read it.
    
- Recipient decrypts using their own private key.
    
- Blockchain will provide future **audit logs, permission control, and trust**.
    
- Entire system is **secure, decentralized, and scalable**.
    

---

