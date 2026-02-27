const API_BASE = "/api";

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`);
  return data;
}

export interface StatusResponse {
  blockchain: boolean;
  ipfs: boolean;
  contract_address: string | null;
}

export interface ProduceResponse {
  success: boolean;
  cid: string;
  data_hash: string;
  tx_hash: string;
  block_number: number;
  local_path: string;
}

export interface GrantResponse {
  success: boolean;
  recipient: string;
  kfrag_path: string;
  tx_hash: string;
  block_number: number;
}

export interface ProxyResponse {
  success: boolean;
  processed_count: number;
  message?: string;
  cid?: string;
  recipient?: string;
  reencrypted_cid?: string;
}

export interface DecryptResponse {
  success: boolean;
  data: Record<string, unknown>;
  cid: string;
  recipient: string;
}

export interface RecordItem {
  cid: string;
  sensor_id: string;
  data_hash: string;
  owner: string;
  created_at: string;
  timestamp?: string;
}

export interface GrantItem {
  cid: string;
  recipient: string;
  processed: boolean;
  reencrypted_cid: string | null;
  created_at: string;
  data_hash?: string;
}

export const api = {
  getStatus: () => request<StatusResponse>("/status"),

  produce: (data: string, sensor_id: string) =>
    request<ProduceResponse>("/produce", {
      method: "POST",
      body: JSON.stringify({ data, sensor_id }),
    }),

  grantAccess: (cid: string, recipient: string) =>
    request<GrantResponse>("/grant-access", {
      method: "POST",
      body: JSON.stringify({ cid, recipient }),
    }),

  runProxy: () =>
    request<ProxyResponse>("/run-proxy", { method: "POST" }),

  decrypt: (cid: string, recipient_id: string) =>
    request<DecryptResponse>("/decrypt", {
      method: "POST",
      body: JSON.stringify({ cid, recipient_id }),
    }),

  listRecords: () =>
    request<{ success: boolean; records: RecordItem[] }>("/list-records").then(r => r.records),

  listGrants: () =>
    request<{ success: boolean; grants: GrantItem[] }>("/list-grants").then(r => r.grants),
};
