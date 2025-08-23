import React from "react";
import { useParams, Link } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Progress } from "../components/ui/progress";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "../components/ui/dialog";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { RadioGroup, RadioGroupItem } from "../components/ui/radio-group";
import { Label } from "../components/ui/label";
import { useToast } from "../hooks/use-toast";
import { getPublicRegistry, createContribution } from "../lib/api";
import { loadRegistry as loadLocalRegistry, loadFunds as loadLocalFunds, sumForFund as sumLocal, totalReceived as totalLocal } from "../mock/mock";

export default function PublicRegistry() {
  const { slug } = useParams();
  const [registry, setRegistry] = React.useState(loadLocalRegistry());
  const [funds, setFunds] = React.useState(loadLocalFunds());

  React.useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getPublicRegistry(slug);
        setRegistry({
          coupleNames: data.registry.couple_names,
          eventDate: data.registry.event_date,
          location: data.registry.location,
          currency: data.registry.currency,
          heroImage: data.registry.hero_image,
          slug: data.registry.slug,
        });
        setFunds(
          data.funds.map((f) => ({
            id: f.id,
            title: f.title,
            description: f.description,
            goal: f.goal,
            coverUrl: f.cover_url,
            category: f.category,
            raised: f.raised,
            progress: f.progress,
          }))
        );
      } catch (e) {
        // fallback to local mock
        console.log("Public page using local mock due to backend error", e?.message);
      }
    };
    fetchData();
  }, [slug]);

  const receivedAll = funds.every((f) => typeof f.raised === "number")
    ? funds.reduce((acc, f) => acc + (f.raised || 0), 0)
    : totalLocal();

  return (
    <div className="min-h-screen">
      <div className="relative">
        <img src={registry.heroImage} alt="Hero" className="w-full h-[360px] object-cover" />
        <div className="absolute inset-0 bg-black/40" />
        <div className="absolute inset-0 flex items-end">
          <div className="max-w-6xl mx-auto px-4 pb-6 w-full flex flex-col md:flex-row md:items-end md:justify-between gap-4">
            <div>
              <h1 className="text-white text-3xl md:text-4xl font-semibold">{registry.coupleNames}</h1>
              <p className="text-white/90">{registry.eventDate} — {registry.location}</p>
            </div>
            <div className="text-right">
              <div className="text-white text-sm">Raised</div>
              <div className="text-white text-2xl font-semibold">{formatCurrency(receivedAll, registry.currency)}</div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 py-10">
        <div className="grid md:grid-cols-3 gap-6">
          {funds.map((f) => (
            <FundCard key={f.id} fund={f} currency={registry.currency} slug={slug} />
          ))}
        </div>

        <div className="mt-12 p-6 rounded-lg border bg-muted/30">
          <h2 className="text-xl font-medium">Share</h2>
          <p className="text-sm text-muted-foreground mt-1">Send this link to your guests so they can contribute with ease.</p>
          <div className="mt-3 flex gap-2">
            <Input readOnly value={window.location.href} />
            <Button onClick={() => navigator.clipboard.writeText(window.location.href)}>Copy</Button>
          </div>
        </div>

        <div className="mt-12">
          <Link to="/create" className="text-sm text-muted-foreground hover:text-foreground">Edit registry →</Link>
        </div>
      </div>
    </div>
  );
}

function FundCard({ fund, currency, slug }) {
  const { toast } = useToast();
  const received = typeof fund.raised === "number" ? fund.raised : sumLocal(fund.id);
  const progress = typeof fund.progress === "number" ? fund.progress : Math.min(100, Math.round((received / (fund.goal || 1)) * 100));

  return (
    <Card className="overflow-hidden">
      <CardContent className="p-0">
        <img src={fund.coverUrl} alt={fund.title} className="w-full h-40 object-cover" />
        <div className="p-4 space-y-2">
          <div className="text-xs text-muted-foreground">{fund.category}</div>
          <div className="font-medium">{fund.title}</div>
          <p className="text-sm text-muted-foreground">{fund.description}</p>
          <div className="mt-2">
            <Progress value={progress} />
            <div className="mt-1 text-xs text-muted-foreground flex items-center justify-between">
              <span>{formatCurrency(received, currency)} raised</span>
              <span>Goal {formatCurrency(fund.goal, currency)}</span>
            </div>
          </div>

          <div className="pt-2">
            <ContributionDialog fund={fund} currency={currency} onComplete={() => {
              toast({ title: "Contribution recorded", description: "Thank you!" });
              // Quick refresh: try to reload public data (best-effort)
              window.location.reload();
            }} />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function ContributionDialog({ fund, currency, onComplete }) {
  const [open, setOpen] = React.useState(false);
  const [amount, setAmount] = React.useState(250);
  const [name, setName] = React.useState("");
  const [message, setMessage] = React.useState("");
  const [method, setMethod] = React.useState("card");
  const [isPublic, setIsPublic] = React.useState(true);

  const quick = [100, 250, 500, 1000];

  const submit = async () => {
    try {
      await createContribution({
        fund_id: fund.id,
        name: name || "Guest",
        amount: Number(amount || 0),
        message,
        public: isPublic,
        method,
      });
    } catch (e) {
      // if backend fails, fall back to local mock by writing to localStorage via window event
      console.log("Backend contribution failed, using local mock", e?.message);
      // Local mock add via dynamic import to avoid bundling cycles
      const { addContribution } = await import("../mock/mock");
      addContribution({
        fundId: fund.id,
        name: name || "Guest",
        amount: Number(amount || 0),
        message,
        public: isPublic,
        createdAt: new Date().toISOString(),
        method,
      });
    }
    setOpen(false);
    onComplete();
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button className="w-full">Contribute</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[520px]">
        <DialogHeader>
          <DialogTitle>Contribute to {fund.title}</DialogTitle>
        </DialogHeader>
        <div className="grid gap-4">
          <div>
            <Label className="text-xs">Amount ({currency})</Label>
            <div className="mt-1 grid grid-cols-4 gap-2">
              {quick.map((q) => (
                <button
                  key={q}
                  onClick={() => setAmount(q)}
                  className={`text-sm rounded-md border px-3 py-2 hover:bg-muted ${amount === q ? "bg-muted" : ""}`}
                >
                  {q}
                </button>
              ))}
            </div>
            <Input className="mt-2" type="number" value={amount} onChange={(e) => setAmount(e.target.value)} />
          </div>
          <div>
            <Label className="text-xs">Your name</Label>
            <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Optional" />
          </div>
          <div>
            <Label className="text-xs">Message</Label>
            <Textarea value={message} onChange={(e) => setMessage(e.target.value)} placeholder="Optional" />
          </div>
          <div>
            <Label className="text-xs mb-2 block">Payment method (mock)</Label>
            <RadioGroup value={method} onValueChange={setMethod} className="grid grid-cols-2 gap-2">
              {[
                { id: "card", label: "Credit/Debit Card" },
                { id: "paypal", label: "PayPal" },
                { id: "revolut", label: "Revolut" },
                { id: "bank", label: "Bank Transfer" },
              ].map((m) => (
                <div key={m.id} className="flex items-center space-x-2 rounded-md border p-2">
                  <RadioGroupItem id={m.id} value={m.id} />
                  <Label htmlFor={m.id}>{m.label}</Label>
                </div>
              ))}
            </RadioGroup>
          </div>
          <div className="flex items-center gap-2">
            <input id="public" type="checkbox" checked={isPublic} onChange={(e)=>setIsPublic(e.target.checked)} />
            <Label htmlFor="public">Show my name/message publicly</Label>
          </div>
          <Button onClick={submit}>Confirm contribution</Button>
          <p className="text-xs text-muted-foreground">This is a demo. Payments are mocked; contributions are recorded in the database.</p>
        </div>
      </DialogContent>
    </Dialog>
  );
}

function formatCurrency(amount, currency = "AED") {
  try {
    return new Intl.NumberFormat("en-US", { style: "currency", currency }).format(amount);
  } catch {
    return `${currency} ${Number(amount || 0).toFixed(2)}`;
  }
}