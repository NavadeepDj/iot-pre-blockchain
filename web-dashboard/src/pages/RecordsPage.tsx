import { useEffect, useState, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { api, RecordItem, GrantItem } from "@/lib/api";
import {
  Database,
  Shield,
  RefreshCw,
  ExternalLink,
  Copy,
  ChevronDown,
  ChevronUp,
  Loader2,
} from "lucide-react";

export default function RecordsPage() {
  const [records, setRecords] = useState<RecordItem[]>([]);
  const [grants, setGrants] = useState<GrantItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [tab, setTab] = useState<"records" | "grants">("records");
  const [expandedRow, setExpandedRow] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [r, g] = await Promise.all([api.listRecords(), api.listGrants()]);
      setRecords(r);
      setGrants(g);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to fetch");
    }
    setLoading(false);
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  function truncate(s: string, len = 16) {
    if (!s) return "—";
    return s.length > len ? s.slice(0, len / 2) + "..." + s.slice(-len / 2) : s;
  }

  function copyToClipboard(text: string) {
    navigator.clipboard.writeText(text);
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Records & Grants</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Browse all registered data records and access grants on the blockchain
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={refresh} disabled={loading}>
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
          <span className="ml-2">Refresh</span>
        </Button>
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-300 text-sm">{error}</div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 bg-muted/50 p-1 rounded-lg w-fit">
        <button
          onClick={() => setTab("records")}
          className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            tab === "records" ? "bg-background text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"
          }`}
        >
          <Database className="w-4 h-4" />
          Data Records
          <Badge variant={tab === "records" ? "default" : "outline"} className="ml-1">{records.length}</Badge>
        </button>
        <button
          onClick={() => setTab("grants")}
          className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            tab === "grants" ? "bg-background text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"
          }`}
        >
          <Shield className="w-4 h-4" />
          Access Grants
          <Badge variant={tab === "grants" ? "default" : "outline"} className="ml-1">{grants.length}</Badge>
        </button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      ) : tab === "records" ? (
        <RecordsList records={records} expandedRow={expandedRow} setExpandedRow={setExpandedRow} truncate={truncate} copyToClipboard={copyToClipboard} />
      ) : (
        <GrantsList grants={grants} expandedRow={expandedRow} setExpandedRow={setExpandedRow} truncate={truncate} copyToClipboard={copyToClipboard} />
      )}
    </div>
  );
}

function RecordsList({
  records,
  expandedRow,
  setExpandedRow,
  truncate,
  copyToClipboard,
}: {
  records: RecordItem[];
  expandedRow: string | null;
  setExpandedRow: (r: string | null) => void;
  truncate: (s: string, len?: number) => string;
  copyToClipboard: (t: string) => void;
}) {
  if (records.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center text-muted-foreground">
          <Database className="w-12 h-12 mx-auto mb-4 opacity-30" />
          <p className="text-lg font-medium">No data records yet</p>
          <p className="text-sm">Use the Workflow page to produce encrypted data</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-2">
      {records.map((r, i) => {
        const key = `record-${i}`;
        const isExpanded = expandedRow === key;
        return (
          <Card key={key} className="overflow-hidden">
            <div
              className="flex items-center gap-4 p-4 cursor-pointer hover:bg-secondary/30 transition-colors"
              onClick={() => setExpandedRow(isExpanded ? null : key)}
            >
              <div className="w-8 h-8 rounded-full bg-primary/10 text-primary flex items-center justify-center text-xs font-bold">
                {i + 1}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium font-mono">{truncate(r.cid || r.data_hash, 24)}</span>
                  <Badge variant="outline" className="text-xs">{r.sensor_id || "unknown"}</Badge>
                </div>
                <div className="text-xs text-muted-foreground mt-0.5">
                  Owner: {truncate(r.owner)}
                  {r.created_at && <span className="ml-3">{new Date(r.created_at).toLocaleString()}</span>}
                </div>
              </div>
              {isExpanded ? <ChevronUp className="w-4 h-4 text-muted-foreground" /> : <ChevronDown className="w-4 h-4 text-muted-foreground" />}
            </div>
            {isExpanded && (
              <div className="px-4 pb-4 border-t border-border pt-3">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                  <DetailRow label="CID" value={r.cid} onCopy={copyToClipboard} />
                  <DetailRow label="Data Hash" value={r.data_hash} onCopy={copyToClipboard} />
                  <DetailRow label="Owner" value={r.owner} onCopy={copyToClipboard} />
                  <DetailRow label="Sensor ID" value={r.sensor_id || "—"} />
                  <DetailRow label="Created" value={r.created_at ? new Date(r.created_at).toLocaleString() : "—"} />
                </div>
                {r.cid && (
                  <a
                    href={`http://127.0.0.1:8080/ipfs/${r.cid}`}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 text-xs text-primary hover:underline mt-3"
                  >
                    <ExternalLink className="w-3 h-3" /> View on IPFS Gateway
                  </a>
                )}
              </div>
            )}
          </Card>
        );
      })}
    </div>
  );
}

function GrantsList({
  grants,
  expandedRow,
  setExpandedRow,
  truncate,
  copyToClipboard,
}: {
  grants: GrantItem[];
  expandedRow: string | null;
  setExpandedRow: (r: string | null) => void;
  truncate: (s: string, len?: number) => string;
  copyToClipboard: (t: string) => void;
}) {
  if (grants.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center text-muted-foreground">
          <Shield className="w-12 h-12 mx-auto mb-4 opacity-30" />
          <p className="text-lg font-medium">No access grants yet</p>
          <p className="text-sm">Grant access on the Workflow page after producing data</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-2">
      {grants.map((g, i) => {
        const key = `grant-${i}`;
        const isExpanded = expandedRow === key;
        return (
          <Card key={key} className="overflow-hidden">
            <div
              className="flex items-center gap-4 p-4 cursor-pointer hover:bg-secondary/30 transition-colors"
              onClick={() => setExpandedRow(isExpanded ? null : key)}
            >
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
                g.processed ? "bg-emerald-500/20 text-emerald-400" : "bg-amber-500/20 text-amber-400"
              }`}>
                {g.processed ? "✓" : i + 1}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium font-mono">{truncate(g.data_hash || g.cid || "—", 24)}</span>
                  <Badge variant={g.processed ? "success" : "warning"}>
                    {g.processed ? "Processed" : "Pending"}
                  </Badge>
                </div>
                <div className="text-xs text-muted-foreground mt-0.5">
                  To: {truncate(g.recipient)}
                </div>
              </div>
              {isExpanded ? <ChevronUp className="w-4 h-4 text-muted-foreground" /> : <ChevronDown className="w-4 h-4 text-muted-foreground" />}
            </div>
            {isExpanded && (
              <div className="px-4 pb-4 border-t border-border pt-3">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                  <DetailRow label="CID" value={g.cid || "—"} onCopy={g.cid ? copyToClipboard : undefined} />
                  <DetailRow label="Data Hash" value={g.data_hash || "—"} onCopy={g.data_hash ? copyToClipboard : undefined} />
                  <DetailRow label="Recipient" value={g.recipient} onCopy={copyToClipboard} />
                  <DetailRow label="Processed" value={g.processed ? "Yes" : "No"} />
                </div>
              </div>
            )}
          </Card>
        );
      })}
    </div>
  );
}

function DetailRow({ label, value, onCopy }: { label: string; value: string; onCopy?: (t: string) => void }) {
  return (
    <div className="flex items-start gap-2">
      <span className="text-muted-foreground text-xs w-20 shrink-0">{label}</span>
      <span className="text-xs font-mono break-all">{value}</span>
      {onCopy && value && value !== "—" && (
        <button onClick={() => onCopy(value)} className="shrink-0 text-muted-foreground hover:text-foreground transition-colors" title="Copy">
          <Copy className="w-3 h-3" />
        </button>
      )}
    </div>
  );
}
