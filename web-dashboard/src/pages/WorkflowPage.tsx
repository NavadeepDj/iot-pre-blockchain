import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input, Textarea, Select, Label } from "@/components/ui/form";
import { api } from "@/lib/api";
import {
  Upload,
  UserCheck,
  RefreshCw,
  Unlock,
  CheckCircle2,
  XCircle,
  Loader2,
  Copy,
  ChevronDown,
  ChevronUp,
  ExternalLink,
} from "lucide-react";

type StepStatus = "idle" | "loading" | "success" | "error";

interface StepState {
  status: StepStatus;
  message: string;
  data?: Record<string, unknown>;
}

const DEFAULT_DATA = JSON.stringify(
  { temperature: 100.0, humidity: 55.2, sensor: "demoNK-station-1", timestamp: "2025-11-17T00:00:00Z" },
  null,
  2
);

export default function WorkflowPage() {
  const [sensorData, setSensorData] = useState(DEFAULT_DATA);
  const [sensorId, setSensorId] = useState("sensor-1");
  const [cid, setCid] = useState("");
  const [recipient, setRecipient] = useState("0x70997970C51812dc3A010C7d01b50e0d17dc79C8");
  const [decryptCid, setDecryptCid] = useState("");
  const [decryptRecipient, setDecryptRecipient] = useState("0x70997970C51812dc3A010C7d01b50e0d17dc79C8");

  const [step1, setStep1] = useState<StepState>({ status: "idle", message: "" });
  const [step2, setStep2] = useState<StepState>({ status: "idle", message: "" });
  const [step3, setStep3] = useState<StepState>({ status: "idle", message: "" });
  const [step4, setStep4] = useState<StepState>({ status: "idle", message: "" });

  const [expandedStep, setExpandedStep] = useState<number | null>(1);

  async function handleProduce() {
    setStep1({ status: "loading", message: "Encrypting and registering data..." });
    try {
      const result = await api.produce(sensorData, sensorId);
      setCid(result.cid);
      setDecryptCid(result.cid);
      setStep1({
        status: "success",
        message: `Data registered on-chain (Block ${result.block_number})`,
        data: { cid: result.cid, hash: result.data_hash, tx: result.tx_hash },
      });
      setExpandedStep(2);
    } catch (e: unknown) {
      setStep1({ status: "error", message: e instanceof Error ? e.message : "Failed" });
    }
  }

  async function handleGrant() {
    if (!cid) { setStep2({ status: "error", message: "Enter a CID first" }); return; }
    setStep2({ status: "loading", message: "Granting access on blockchain..." });
    try {
      const result = await api.grantAccess(cid, recipient);
      setStep2({
        status: "success",
        message: `Access granted (Block ${result.block_number})`,
        data: { recipient: result.recipient, tx: result.tx_hash },
      });
      setExpandedStep(3);
    } catch (e: unknown) {
      setStep2({ status: "error", message: e instanceof Error ? e.message : "Failed" });
    }
  }

  async function handleProxy() {
    setStep3({ status: "loading", message: "Proxy re-encrypting data..." });
    try {
      const result = await api.runProxy();
      if (result.processed_count === 0) {
        setStep3({ status: "error", message: "No unprocessed grants found" });
      } else {
        setStep3({
          status: "success",
          message: `Re-encrypted ${result.processed_count} grant(s)`,
          data: { reencrypted_cid: result.reencrypted_cid, cid: result.cid },
        });
        setExpandedStep(4);
      }
    } catch (e: unknown) {
      setStep3({ status: "error", message: e instanceof Error ? e.message : "Failed" });
    }
  }

  async function handleDecrypt() {
    if (!decryptCid) { setStep4({ status: "error", message: "Enter a CID" }); return; }
    setStep4({ status: "loading", message: "Decrypting data..." });
    try {
      const result = await api.decrypt(decryptCid, decryptRecipient);
      setStep4({
        status: "success",
        message: "Successfully decrypted!",
        data: { decrypted: result.data },
      });
    } catch (e: unknown) {
      setStep4({ status: "error", message: e instanceof Error ? e.message : "Failed" });
    }
  }

  function copyToClipboard(text: string) {
    navigator.clipboard.writeText(text);
  }

  const steps = [
    { num: 1, icon: Upload, title: "Produce Data", desc: "Encrypt sensor data and register on blockchain", state: step1 },
    { num: 2, icon: UserCheck, title: "Grant Access", desc: "Authorize a recipient to access the data", state: step2 },
    { num: 3, icon: RefreshCw, title: "Proxy Re-Encrypt", desc: "Re-encrypt data for the recipient without seeing plaintext", state: step3 },
    { num: 4, icon: Unlock, title: "Decrypt Data", desc: "Recipient decrypts and views original data", state: step4 },
  ];

  return (
    <div className="space-y-6 animate-fade-in max-w-3xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold">Workflow</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Follow the 4-step process to encrypt, share, and decrypt IoT data
        </p>
      </div>

      {/* Progress bar */}
      <div className="flex items-center gap-1">
        {steps.map((s, i) => (
          <div key={s.num} className="flex items-center flex-1">
            <div className={`flex-1 h-1.5 rounded-full transition-colors ${
              s.state.status === "success" ? "bg-emerald-500" :
              s.state.status === "loading" ? "bg-primary animate-pulse" :
              s.state.status === "error" ? "bg-red-500" : "bg-muted"
            }`} />
            {i < steps.length - 1 && <div className="w-1" />}
          </div>
        ))}
      </div>

      {/* Step 1: Produce */}
      <StepCard
        step={steps[0]}
        expanded={expandedStep === 1}
        onToggle={() => setExpandedStep(expandedStep === 1 ? null : 1)}
      >
        <div className="space-y-4">
          <div>
            <Label>Sensor Data (JSON)</Label>
            <Textarea value={sensorData} onChange={(e) => setSensorData(e.target.value)} rows={5} />
          </div>
          <div>
            <Label>Sensor ID</Label>
            <Input value={sensorId} onChange={(e) => setSensorId(e.target.value)} placeholder="sensor-1" />
          </div>
          <Button onClick={handleProduce} disabled={step1.status === "loading"} className="w-full">
            {step1.status === "loading" ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Upload className="w-4 h-4 mr-2" />}
            Encrypt & Register
          </Button>
          <StepResult state={step1} onCopy={copyToClipboard} />
        </div>
      </StepCard>

      {/* Step 2: Grant Access */}
      <StepCard
        step={steps[1]}
        expanded={expandedStep === 2}
        onToggle={() => setExpandedStep(expandedStep === 2 ? null : 2)}
      >
        <div className="space-y-4">
          <div>
            <Label>Data CID</Label>
            <div className="flex gap-2">
              <Input value={cid} onChange={(e) => setCid(e.target.value)} placeholder="QmXXX..." className="flex-1" />
              {Boolean(step1.data?.cid) && (
                <Button variant="outline" size="sm" onClick={() => setCid(step1.data!.cid as string)}>
                  <Copy className="w-4 h-4" />
                </Button>
              )}
            </div>
          </div>
          <div>
            <Label>Recipient Address</Label>
            <Select value={recipient} onChange={(e) => setRecipient(e.target.value)}>
              <option value="0x70997970C51812dc3A010C7d01b50e0d17dc79C8">Recipient 1 (0x7099...79C8)</option>
              <option value="0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC">Recipient 2 (0x3C44...93BC)</option>
            </Select>
          </div>
          <Button onClick={handleGrant} disabled={step2.status === "loading"} className="w-full">
            {step2.status === "loading" ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <UserCheck className="w-4 h-4 mr-2" />}
            Grant Access
          </Button>
          <StepResult state={step2} onCopy={copyToClipboard} />
        </div>
      </StepCard>

      {/* Step 3: Proxy */}
      <StepCard
        step={steps[2]}
        expanded={expandedStep === 3}
        onToggle={() => setExpandedStep(expandedStep === 3 ? null : 3)}
      >
        <div className="space-y-4">
          <div className="p-3 rounded-lg bg-primary/5 border border-primary/10 text-sm text-muted-foreground">
            The proxy worker finds unprocessed grants on the blockchain, re-encrypts the ciphertext,
            and stores the result on IPFS — all without ever seeing the plaintext data.
          </div>
          <Button onClick={handleProxy} disabled={step3.status === "loading"} className="w-full">
            {step3.status === "loading" ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <RefreshCw className="w-4 h-4 mr-2" />}
            Run Proxy Worker
          </Button>
          <StepResult state={step3} onCopy={copyToClipboard} />
        </div>
      </StepCard>

      {/* Step 4: Decrypt */}
      <StepCard
        step={steps[3]}
        expanded={expandedStep === 4}
        onToggle={() => setExpandedStep(expandedStep === 4 ? null : 4)}
      >
        <div className="space-y-4">
          <div>
            <Label>Data CID</Label>
            <div className="flex gap-2">
              <Input value={decryptCid} onChange={(e) => setDecryptCid(e.target.value)} placeholder="QmXXX..." className="flex-1" />
              {Boolean(step1.data?.cid) && (
                <Button variant="outline" size="sm" onClick={() => setDecryptCid(step1.data!.cid as string)}>
                  <Copy className="w-4 h-4" />
                </Button>
              )}
            </div>
          </div>
          <div>
            <Label>Recipient Address</Label>
            <Select value={decryptRecipient} onChange={(e) => setDecryptRecipient(e.target.value)}>
              <option value="0x70997970C51812dc3A010C7d01b50e0d17dc79C8">Recipient 1 (0x7099...79C8)</option>
              <option value="0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC">Recipient 2 (0x3C44...93BC)</option>
            </Select>
          </div>
          <Button onClick={handleDecrypt} disabled={step4.status === "loading"} className="w-full">
            {step4.status === "loading" ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Unlock className="w-4 h-4 mr-2" />}
            Decrypt Data
          </Button>
          <StepResult state={step4} onCopy={copyToClipboard} />
        </div>
      </StepCard>
    </div>
  );
}

function StepCard({
  step,
  expanded,
  onToggle,
  children,
}: {
  step: { num: number; icon: React.ElementType; title: string; desc: string; state: StepState };
  expanded: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}) {
  const Icon = step.icon;
  return (
    <Card className={step.state.status === "success" ? "border-emerald-500/30" : step.state.status === "error" ? "border-red-500/30" : ""}>
      <div className="flex items-center gap-4 p-4 cursor-pointer hover:bg-secondary/30 rounded-t-xl transition-colors" onClick={onToggle}>
        <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm ${
          step.state.status === "success" ? "bg-emerald-500/20 text-emerald-400" :
          step.state.status === "error" ? "bg-red-500/20 text-red-400" :
          step.state.status === "loading" ? "bg-primary/20 text-primary animate-pulse-glow" :
          "bg-muted text-muted-foreground"
        }`}>
          {step.state.status === "success" ? (
            <CheckCircle2 className="w-5 h-5" />
          ) : step.state.status === "loading" ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            step.num
          )}
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-sm">{step.title}</h3>
            {step.state.status === "success" && <Badge variant="success">Done</Badge>}
            {step.state.status === "error" && <Badge variant="destructive">Error</Badge>}
          </div>
          <p className="text-xs text-muted-foreground">{step.desc}</p>
        </div>
        <Icon className="w-4 h-4 text-muted-foreground" />
        {expanded ? <ChevronUp className="w-4 h-4 text-muted-foreground" /> : <ChevronDown className="w-4 h-4 text-muted-foreground" />}
      </div>
      {expanded && <CardContent className="pt-0 border-t border-border">{children}</CardContent>}
    </Card>
  );
}

function StepResult({ state, onCopy }: { state: StepState; onCopy: (t: string) => void }) {
  if (state.status === "idle") return null;

  return (
    <div className={`rounded-lg p-3 text-sm font-mono ${
      state.status === "success" ? "bg-emerald-500/10 border border-emerald-500/20 text-emerald-300" :
      state.status === "error" ? "bg-red-500/10 border border-red-500/20 text-red-300" :
      "bg-muted text-muted-foreground"
    }`}>
      <p className="mb-2">{state.status === "success" ? "✓" : state.status === "error" ? "✗" : "⏳"} {state.message}</p>
      {state.data && (
        <div className="space-y-1 text-xs">
          {Object.entries(state.data).map(([key, value]) => (
            <div key={key} className="flex items-start gap-2">
              <span className="text-muted-foreground shrink-0">{key}:</span>
              {key === "decrypted" ? (
                <pre className="whitespace-pre-wrap break-all">{JSON.stringify(value, null, 2)}</pre>
              ) : (
                <div className="flex items-center gap-1 min-w-0">
                  <span className="truncate">{String(value)}</span>
                  <button
                    onClick={(e) => { e.stopPropagation(); onCopy(String(value)); }}
                    className="shrink-0 hover:text-foreground transition-colors"
                    title="Copy"
                  >
                    <Copy className="w-3 h-3" />
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
