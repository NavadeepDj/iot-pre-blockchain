import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import {
  BookOpen,
  Rocket,
  FileText,
  Shield,
  Layers,
  Terminal,
  Cpu,
  ArrowRight,
} from "lucide-react";

const DOCS = [
  {
    id: "overview",
    title: "Project Overview",
    icon: BookOpen,
    content: `
# Proxy Re-Encryption for Secure IoT Data Sharing

## Abstract

This project enhances the security of Internet of Things (IoT) data sharing using **Proxy Re-Encryption (PRE)** integrated with **blockchain**. 

In IoT environments, vast amounts of sensitive data are continuously generated and need to be shared securely across multiple entities such as healthcare providers, smart cities, or industrial systems.

Proxy Re-Encryption solves this by allowing data encrypted by one party (e.g., an IoT device owner) to be securely re-encrypted for another party **without exposing private keys or data to intermediaries**.

Blockchain is leveraged as a decentralized and tamper-proof control plane to manage access permissions, store data integrity proofs, and maintain audit logs.

## Problem Statement

IoT devices generate vast amounts of sensitive data that is often transferred to centralized servers, creating:

- Single points of failure  
- Limited visibility and auditability  
- High risk of key leakage  
- Poor scalability in multi-user environments  

## Objectives

- IoT data is encrypted **only once**
- Data is stored securely and is tamper-proof
- Access is controlled and logged via blockchain smart contracts
- Proxy Re-Encryption allows safe sharing without exposing private keys
- Unauthorized access and data tampering are prevented
`,
  },
  {
    id: "architecture",
    title: "Architecture",
    icon: Layers,
    content: `
# System Architecture

## Core Components

### 1. IoT Data Producer (Sensor / Owner)
Encrypts data locally using the owner's public key and uploads encrypted files to IPFS.

### 2. Owner Application
Manages who can access the IoT data by generating secure sharing permissions (re-encryption keys).

### 3. Proxy Re-Encryption Worker
Converts the owner's encrypted data into a form that only the selected recipient can decrypt — **without ever seeing the plaintext**.

### 4. Recipient Application
Fetches re-encrypted IoT data from IPFS and decrypts it using the recipient's own private key.

### 5. Decentralized Storage (IPFS)
Stores encrypted data and re-encrypted data, ensuring decentralization and tamper resistance.

### 6. Blockchain (Smart Contract)
Stores metadata, access permissions, and audit logs in a tamper-proof way. Events drive proxy automation.

## Execution Environment

| Component | Technology |
|-----------|-----------|
| Python Backend | Encryption, PRE logic, IPFS upload/download |
| IPFS Daemon | Local decentralized file storage |
| Foundry / Anvil | Local Ethereum blockchain for testing |
| Smart Contract | Solidity Registry.sol on Anvil |

## Data Structures

### Data Record
- **CID** — IPFS content address
- **Hash** — SHA-256 integrity hash
- **Owner Address** — Ethereum address
- **Sensor ID** — Device identifier
- **Timestamp** — Block number

### Access Grant
- **Recipient Address**
- **Re-encryption Key** (kfrag)
- **Re-encrypted CID** (after proxy)
- **Status** — Processed or Pending
`,
  },
  {
    id: "dataflow",
    title: "Data Flow",
    icon: ArrowRight,
    content: `
# Data Flow

## Step-by-Step

### 1. IoT Sensor → Encrypt & Store
\`\`\`
Sensor Data (JSON)
    ↓ Encrypt with owner's public key (pyUmbral)
    ↓ Upload ciphertext + capsule to IPFS
    ↓ Get CID (content address)
    ↓ Register on blockchain (CID + hash)
\`\`\`

### 2. Owner → Grant Access
\`\`\`
Owner decides to share with Recipient
    ↓ Generate re-encryption key (kfrag)
    ↓ Store kfrag locally
    ↓ Record grant on blockchain
    ↓ Status: "Pending"
\`\`\`

### 3. Proxy Worker → Re-Encrypt
\`\`\`
Proxy polls blockchain for pending grants
    ↓ Fetch encrypted data from IPFS
    ↓ Apply PRE transformation (cfrag)
    ↓ Upload re-encrypted capsule to IPFS
    ↓ Mark grant as "Processed"
\`\`\`

### 4. Recipient → Decrypt
\`\`\`
Recipient fetches re-encrypted data from IPFS
    ↓ Decrypt using their private key
    ↓ Verify hash integrity
    ↓ Receive original sensor data
\`\`\`

## Security Guarantees

- **Proxy never sees plaintext** — only transforms the ciphertext
- **No private key sharing** — each party keeps their own keys
- **Blockchain auditability** — all grants and access events are logged on-chain
- **IPFS integrity** — CID is derived from content hash, making tampering detectable
`,
  },
  {
    id: "pre",
    title: "Why PRE?",
    icon: Shield,
    content: `
# Why Proxy Re-Encryption?

## The Problem with Traditional Approaches

### Direct Key Sharing
Sharing private keys with recipients is inherently dangerous — if one recipient is compromised, all data is exposed.

### Re-encryption for Each Recipient
Re-encrypting data for each new recipient is computationally expensive and requires the data owner to be online and involved in every share.

### Centralized Access Control
Trust in a central server creates a single point of failure and requires the server to see plaintext data.

## How PRE Solves This

Proxy Re-Encryption is a cryptographic technique where:

1. **Data is encrypted once** with the owner's public key
2. **A re-encryption key** is generated that transforms ciphertext from owner → recipient
3. **A proxy (untrusted)** applies the transformation — it **never sees the plaintext**
4. **The recipient** decrypts with their own private key

### Key Properties

| Property | Description |
|----------|-------------|
| **Unidirectional** | Owner → Recipient only (recipient can't re-share) |
| **Non-interactive** | Recipient doesn't need to be online during encryption |
| **Non-transitive** | Proxy can't chain keys to gain access |
| **Scalable** | One encryption, unlimited authorized recipients |

## pyUmbral Library

This project uses **pyUmbral**, the reference implementation of Umbral PRE by NuCypher:

- Generates key pairs (signing + encryption)
- Creates capsules for each encryption
- Generates key fragments (kfrags) for re-encryption
- Produces capsule fragments (cfrags) for recipients
- Supports threshold re-encryption (M-of-N)
`,
  },
  {
    id: "tech",
    title: "Technology Stack",
    icon: Cpu,
    content: `
# Technology Stack

## Python Backend

| Library | Purpose |
|---------|---------|
| **pyUmbral** | Proxy Re-Encryption (encrypt, re-encrypt, decrypt) |
| **Flask** | REST API for the web dashboard |
| **Web3.py** | Interaction with the Ethereum blockchain |
| **ipfshttpclient** | Upload/download encrypted files from IPFS |
| **Typer** | Command-line interface |
| **Pydantic** | Data validation and models |
| **Rich** | Colored terminal output |

## Blockchain

| Tool | Purpose |
|------|---------|
| **Foundry** | Smart contract development framework |
| **Anvil** | Local Ethereum blockchain simulator |
| **Solidity** | Smart contract language |
| **forge** | Contract compilation, testing, and deployment |

## Storage

| Tool | Purpose |
|------|---------|
| **IPFS** | InterPlanetary File System for decentralized encrypted data storage |
| **Content Addressing** | CIDs ensure data integrity — any change produces a different CID |

## Frontend

| Tool | Purpose |
|------|---------|
| **React 18** | UI framework |
| **TypeScript** | Type-safe JavaScript |
| **Vite** | Fast build tool and dev server |
| **Tailwind CSS** | Utility-first styling |
| **React Router** | Client-side routing |
| **Lucide React** | Icon library |

## Smart Contract: Registry.sol

The Registry contract handles:
- \`registerData(cid, dataHash)\` — Register encrypted data on-chain
- \`grantAccess(dataHash, recipient)\` — Grant access to a recipient
- \`completeAccess(dataHash, recipient)\` — Mark a grant as processed
- Events: \`DataRegistered\`, \`AccessGranted\`, \`AccessCompleted\`
`,
  },
  {
    id: "quickstart",
    title: "Quick Start",
    icon: Rocket,
    content: `
# Quick Start Guide

## Prerequisites

- **Python 3.10+** with \`venv\`
- **Node.js 18+** with \`npm\`
- **IPFS** installed and initialized (\`ipfs init\`)
- **Foundry** installed (\`curl -L https://foundry.paradigm.xyz | bash && foundryup\`)

## Terminal 1 — Start Anvil (Local Blockchain)

\`\`\`bash
cd blockchain
anvil
\`\`\`

Keep this running. You should see \`Listening on 127.0.0.1:8545\`.

## Terminal 2 — Start IPFS Daemon

\`\`\`bash
ipfs daemon
\`\`\`

Keep this running. You should see \`Daemon is ready\`.

## Terminal 3 — Deploy Smart Contract

\`\`\`bash
cd blockchain
forge script script/DeployRegistry.s.sol --rpc-url http://127.0.0.1:8545 --broadcast
\`\`\`

Expected output: \`Contract Address: 0x5FbDB2315678afecb367f032d93F642f64180aa3\`

> **Important:** Always deploy immediately after starting fresh Anvil, before any other commands.

## Terminal 3 — Run Backend & Dashboard

\`\`\`bash
cd python-backend
.\\venv\\Scripts\\activate
python app.py
\`\`\`

\`\`\`bash
cd web-dashboard
npm run dev
\`\`\`

Open **http://localhost:3000** and use the Workflow page to:
1. **Produce** — Encrypt sensor data
2. **Grant** — Authorize a recipient
3. **Proxy** — Re-encrypt for the recipient
4. **Decrypt** — Recipient decrypts data

## CLI Alternative

\`\`\`bash
# Produce
python -m src.sensor_service produce sample_payload.json

# Grant access (replace CID)
python -m src.owner_cli grant-access <CID> 0x70997970C51812dc3A010C7d01b50e0d17dc79C8

# Run proxy
python -m src.proxy_worker

# Decrypt
python -m src.recipient_cli decrypt <CID> --recipient 0x70997970C51812dc3A010C7d01b50e0d17dc79C8
\`\`\`
`,
  },
  {
    id: "troubleshooting",
    title: "Troubleshooting",
    icon: Terminal,
    content: `
# Troubleshooting

## "No unprocessed grants"

**Cause:** The smart contract has no code at the configured address. This happens when Anvil is restarted (all state is lost).

**Fix:**
1. Stop Anvil and restart it
2. Deploy the contract **immediately** (before any other commands):
   \`\`\`bash
   cd blockchain
   forge script script/DeployRegistry.s.sol --rpc-url http://127.0.0.1:8545 --broadcast
   \`\`\`
3. Verify the contract address in \`python-backend/.env\` matches the deploy output

## Contract address changed

**Cause:** The contract address is deterministic based on: \`deployer_address + nonce\`. If other transactions were sent before deployment, the nonce is different, producing a different address.

**Fix:** Always deploy first on a fresh Anvil. The expected address is:
\`\`\`
0x5FbDB2315678afecb367f032d93F642f64180aa3
\`\`\`

## IPFS connection error

**Cause:** IPFS daemon is not running.

**Fix:**
\`\`\`bash
ipfs daemon
\`\`\`

Ensure port 5001 (API) and 8080 (Gateway) are available.

## Flask API not responding

**Fix:** Make sure the Python backend is running:
\`\`\`bash
cd python-backend
.\\venv\\Scripts\\activate
python app.py
\`\`\`

The API runs on http://localhost:5000.

## "Transaction reverted" errors

**Possible causes:**
- Contract not deployed at the configured address
- Trying to grant access for data that wasn't registered
- Trying to complete access for a grant that doesn't exist

**Debug:** Check the contract address has code:
\`\`\`bash
cast code 0x5FbDB2315678afecb367f032d93F642f64180aa3 --rpc-url http://127.0.0.1:8545
\`\`\`
If the output is \`0x\`, the contract is not deployed.
`,
  },
];

export default function DocsPage() {
  const [activeDoc, setActiveDoc] = useState("overview");

  const current = DOCS.find((d) => d.id === activeDoc) || DOCS[0];

  return (
    <div className="animate-fade-in flex gap-6">
      {/* Sidebar nav */}
      <nav className="hidden lg:flex flex-col gap-1 w-48 shrink-0 sticky top-0 self-start">
        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2 px-3">
          Documentation
        </p>
        {DOCS.map((doc) => {
          const Icon = doc.icon;
          const isActive = doc.id === activeDoc;
          return (
            <button
              key={doc.id}
              onClick={() => setActiveDoc(doc.id)}
              className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm transition-colors text-left ${
                isActive
                  ? "bg-primary/10 text-primary font-medium"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
              }`}
            >
              <Icon className="w-4 h-4 shrink-0" />
              {doc.title}
            </button>
          );
        })}
      </nav>

      {/* Mobile dropdown */}
      <div className="lg:hidden w-full">
        <select
          value={activeDoc}
          onChange={(e) => setActiveDoc(e.target.value)}
          className="w-full mb-4 bg-secondary border border-border rounded-md px-3 py-2 text-sm"
        >
          {DOCS.map((doc) => (
            <option key={doc.id} value={doc.id}>
              {doc.title}
            </option>
          ))}
        </select>
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0 prose-docs">
        <div dangerouslySetInnerHTML={{ __html: "" }} />
        <MarkdownContent content={current.content} />
      </div>
    </div>
  );
}

function MarkdownContent({ content }: { content: string }) {
  // Simple markdown-to-HTML converter for the embedded docs
  // Handles: headers, bold, inline code, code blocks, tables, lists, blockquotes, horizontal rules
  const html = content
    .trim()
    .split("\n")
    .reduce(
      (acc, line) => {
        // Code blocks
        if (line.startsWith("```")) {
          if (acc.inCode) {
            acc.lines.push("</code></pre>");
            acc.inCode = false;
          } else {
            const lang = line.slice(3).trim();
            acc.lines.push(`<pre><code class="language-${lang}">`);
            acc.inCode = true;
          }
          return acc;
        }
        if (acc.inCode) {
          acc.lines.push(escapeHtml(line));
          return acc;
        }

        // Table
        if (line.startsWith("|")) {
          if (!acc.inTable) {
            acc.lines.push("<table>");
            acc.inTable = true;
            acc.tableRow = 0;
          }
          // Skip separator row
          if (line.match(/^\|[\s-|]+\|$/)) {
            acc.tableRow++;
            return acc;
          }
          const cells = line.split("|").filter(Boolean).map((c) => c.trim());
          const tag = acc.tableRow === 0 ? "th" : "td";
          const rowTag = acc.tableRow === 0 ? "thead" : "";
          if (acc.tableRow === 0) acc.lines.push("<thead>");
          if (acc.tableRow === 1 && !acc.tbodyOpen) {
            acc.lines.push("</thead><tbody>");
            acc.tbodyOpen = true;
          }
          acc.lines.push(`<tr>${cells.map((c) => `<${tag}>${inlineFormat(c)}</${tag}>`).join("")}</tr>`);
          acc.tableRow++;
          return acc;
        }
        if (acc.inTable && !line.startsWith("|")) {
          if (acc.tbodyOpen) acc.lines.push("</tbody>");
          acc.lines.push("</table>");
          acc.inTable = false;
          acc.tbodyOpen = false;
          acc.tableRow = 0;
        }

        // Blockquote
        if (line.startsWith("> ")) {
          acc.lines.push(`<blockquote><p>${inlineFormat(line.slice(2))}</p></blockquote>`);
          return acc;
        }

        // Headers
        const hMatch = line.match(/^(#{1,6})\s+(.*)/);
        if (hMatch) {
          const level = hMatch[1].length;
          acc.lines.push(`<h${level}>${inlineFormat(hMatch[2])}</h${level}>`);
          return acc;
        }

        // Horizontal rule
        if (line.match(/^---+$/)) {
          acc.lines.push("<hr />");
          return acc;
        }

        // List items
        if (line.match(/^[-*]\s/)) {
          if (!acc.inList) {
            acc.lines.push("<ul>");
            acc.inList = true;
          }
          acc.lines.push(`<li>${inlineFormat(line.replace(/^[-*]\s+/, ""))}</li>`);
          return acc;
        }
        const olMatch = line.match(/^(\d+)\.\s+(.*)/);
        if (olMatch) {
          if (!acc.inOl) {
            acc.lines.push("<ol>");
            acc.inOl = true;
          }
          acc.lines.push(`<li>${inlineFormat(olMatch[2])}</li>`);
          return acc;
        }

        // Close list if needed
        if (acc.inList && !line.match(/^[-*]\s/)) {
          acc.lines.push("</ul>");
          acc.inList = false;
        }
        if (acc.inOl && !olMatch) {
          acc.lines.push("</ol>");
          acc.inOl = false;
        }

        // Paragraph
        if (line.trim() === "") {
          acc.lines.push("");
          return acc;
        }
        acc.lines.push(`<p>${inlineFormat(line)}</p>`);
        return acc;
      },
      { lines: [] as string[], inCode: false, inTable: false, inList: false, inOl: false, tableRow: 0, tbodyOpen: false }
    );

  // Close unclosed tags
  if (html.inCode) html.lines.push("</code></pre>");
  if (html.inList) html.lines.push("</ul>");
  if (html.inOl) html.lines.push("</ol>");
  if (html.inTable) {
    if (html.tbodyOpen) html.lines.push("</tbody>");
    html.lines.push("</table>");
  }

  return (
    <div
      className="prose-docs"
      dangerouslySetInnerHTML={{ __html: html.lines.join("\n") }}
    />
  );
}

function escapeHtml(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function inlineFormat(s: string): string {
  return s
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/`(.+?)`/g, "<code>$1</code>")
    .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2">$1</a>');
}
