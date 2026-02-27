import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api, type StatusResponse, type RecordItem, type GrantItem } from "@/lib/api";
import {
  Shield,
  HardDrive,
  FileCheck,
  Users,
  ArrowRight,
  Lock,
  Unlock,
  RefreshCw,
  Database,
  Wifi,
  Server,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";

export default function DashboardPage() {
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [records, setRecords] = useState<RecordItem[]>([]);
  const [grants, setGrants] = useState<GrantItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function fetchAll() {
    setLoading(true);
    setError(null);
    try {
      const [s, r, g] = await Promise.all([
        api.getStatus(),
        api.listRecords().catch(() => [] as RecordItem[]),
        api.listGrants().catch(() => [] as GrantItem[]),
      ]);
      setStatus(s);
      setRecords(r);
      setGrants(g);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to connect to backend");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchAll();
  }, []);

  const processed = grants.filter((g) => g.processed).length;
  const pending = grants.filter((g) => !g.processed).length;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Monitor your IoT Proxy Re-Encryption system
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={fetchAll} disabled={loading}>
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {error && (
        <Card className="border-red-500/30 bg-red-500/5">
          <CardContent className="p-4 text-red-400 text-sm">
            {error} — Make sure the Flask API is running on port 5000.
          </CardContent>
        </Card>
      )}

      {/* System Status */}
      <div className="grid gap-4 md:grid-cols-3">
        <StatusCard
          icon={Server}
          title="Anvil Blockchain"
          ok={status?.blockchain ?? null}
          detail={status?.contract_address ? `Contract: ${status.contract_address.slice(0, 10)}...` : "Not deployed"}
        />
        <StatusCard
          icon={HardDrive}
          title="IPFS Daemon"
          ok={status?.ipfs ?? null}
          detail={status?.ipfs ? "Connected on port 5001" : "Not connected"}
        />
        <StatusCard
          icon={Wifi}
          title="Flask API"
          ok={status !== null}
          detail={status !== null ? "Running on port 5000" : "Offline"}
        />
      </div>

      {/* Stats cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <StatsCard icon={Database} label="Data Records" value={records.length} />
        <StatsCard icon={Users} label="Access Grants" value={grants.length} />
        <StatsCard icon={FileCheck} label="Processed" value={processed} color="text-emerald-400" />
        <StatsCard icon={Lock} label="Pending" value={pending} color="text-amber-400" />
      </div>

      {/* Architecture flow diagram */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-primary" />
            Proxy Re-Encryption Data Flow
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap items-center justify-center gap-3 py-4">
            <FlowStep icon={Wifi} label="IoT Sensor" sub="Produces data" />
            <ArrowRight className="w-5 h-5 text-muted-foreground hidden sm:block" />
            <FlowStep icon={Lock} label="Encrypt" sub="Owner's public key" />
            <ArrowRight className="w-5 h-5 text-muted-foreground hidden sm:block" />
            <FlowStep icon={HardDrive} label="IPFS" sub="Store ciphertext" />
            <ArrowRight className="w-5 h-5 text-muted-foreground hidden sm:block" />
            <FlowStep icon={RefreshCw} label="Proxy PRE" sub="Re-encrypt" />
            <ArrowRight className="w-5 h-5 text-muted-foreground hidden sm:block" />
            <FlowStep icon={Unlock} label="Decrypt" sub="Recipient's key" />
          </div>
          <p className="text-center text-xs text-muted-foreground mt-2">
            All operations are logged on the blockchain for a tamper-proof audit trail
          </p>
        </CardContent>
      </Card>

      {/* Quick actions */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Link to="/workflow">
              <Button className="w-full justify-start" variant="secondary">
                <Shield className="w-4 h-4 mr-2" />
                Start Full Workflow
                <ArrowRight className="w-4 h-4 ml-auto" />
              </Button>
            </Link>
            <Link to="/records">
              <Button className="w-full justify-start mt-2" variant="secondary">
                <Database className="w-4 h-4 mr-2" />
                View Records & Grants
                <ArrowRight className="w-4 h-4 ml-auto" />
              </Button>
            </Link>
            <Link to="/docs">
              <Button className="w-full justify-start mt-2" variant="secondary">
                <FileCheck className="w-4 h-4 mr-2" />
                Read Documentation
                <ArrowRight className="w-4 h-4 ml-auto" />
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* Recent activity */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            {records.length === 0 && grants.length === 0 ? (
              <p className="text-sm text-muted-foreground py-4 text-center">
                No activity yet. Start by producing sensor data.
              </p>
            ) : (
              <div className="space-y-3 max-h-[200px] overflow-y-auto">
                {[...records.slice(-3)].reverse().map((r) => (
                  <div key={r.cid} className="flex items-center gap-3 text-sm">
                    <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                      <Database className="w-4 h-4 text-primary" />
                    </div>
                    <div className="min-w-0">
                      <p className="font-medium truncate">{r.sensor_id}</p>
                      <p className="text-xs text-muted-foreground truncate font-mono">{r.cid}</p>
                    </div>
                    <Badge variant="success" className="ml-auto shrink-0">Registered</Badge>
                  </div>
                ))}
                {[...grants.slice(-3)].reverse().map((g) => (
                  <div key={`${g.cid}-${g.recipient}`} className="flex items-center gap-3 text-sm">
                    <div className="w-8 h-8 rounded-full bg-amber-500/10 flex items-center justify-center shrink-0">
                      <Users className="w-4 h-4 text-amber-400" />
                    </div>
                    <div className="min-w-0">
                      <p className="font-medium truncate">Grant → {g.recipient.slice(0, 8)}...</p>
                      <p className="text-xs text-muted-foreground truncate font-mono">{g.cid}</p>
                    </div>
                    <Badge variant={g.processed ? "success" : "warning"} className="ml-auto shrink-0">
                      {g.processed ? "Processed" : "Pending"}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function StatusCard({ icon: Icon, title, ok, detail }: { icon: React.ElementType; title: string; ok: boolean | null; detail: string }) {
  return (
    <Card className={ok ? "border-emerald-500/20" : ok === false ? "border-red-500/20" : ""}>
      <CardContent className="p-4 flex items-center gap-4">
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
          ok ? "bg-emerald-500/10" : ok === false ? "bg-red-500/10" : "bg-muted"
        }`}>
          <Icon className={`w-5 h-5 ${ok ? "text-emerald-400" : ok === false ? "text-red-400" : "text-muted-foreground"}`} />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <p className="font-medium text-sm">{title}</p>
            <div className={`w-2 h-2 rounded-full ${
              ok ? "bg-emerald-500" : ok === false ? "bg-red-500" : "bg-muted-foreground"
            }`} />
          </div>
          <p className="text-xs text-muted-foreground">{detail}</p>
        </div>
      </CardContent>
    </Card>
  );
}

function StatsCard({ icon: Icon, label, value, color }: { icon: React.ElementType; label: string; value: number; color?: string }) {
  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">{label}</p>
          <Icon className="w-4 h-4 text-muted-foreground" />
        </div>
        <p className={`text-2xl font-bold mt-1 ${color || ""}`}>{value}</p>
      </CardContent>
    </Card>
  );
}

function FlowStep({ icon: Icon, label, sub }: { icon: React.ElementType; label: string; sub: string }) {
  return (
    <div className="flex flex-col items-center gap-1.5 p-3 rounded-xl bg-secondary/50 min-w-[100px]">
      <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
        <Icon className="w-5 h-5 text-primary" />
      </div>
      <p className="text-xs font-medium">{label}</p>
      <p className="text-[10px] text-muted-foreground">{sub}</p>
    </div>
  );
}
