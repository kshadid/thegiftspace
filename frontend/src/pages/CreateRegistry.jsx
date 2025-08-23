import React from "react";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { Button } from "../components/ui/button";
import { Label } from "../components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { Switch } from "../components/ui/switch";
import { useToast } from "../hooks/use-toast";
import { Link, useNavigate } from "react-router-dom";
import {
  loadRegistry,
  saveRegistry,
  loadFunds,
  saveFunds,
  DEFAULT_CURRENCY,
} from "../mock/mock";
import { Plus, Trash2, Eye, ArrowDownToLine } from "lucide-react";
import { createRegistry as apiCreateRegistry, updateRegistry as apiUpdateRegistry, bulkUpsertFunds, getRegistryAnalytics, exportRegistryCSV } from "../lib/api";

export default function CreateRegistry() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [registry, setRegistry] = React.useState(loadRegistry());
  const [funds, setFunds] = React.useState(loadFunds());
  const [publishing, setPublishing] = React.useState(false);
  const [activeTab, setActiveTab] = React.useState("list");
  const [analytics, setAnalytics] = React.useState(null);

  const updateRegistry = (patch) => setRegistry((r) => ({ ...r, ...patch }));

  const addFund = () => {
    const id = `fund_${Date.now()}`;
    setFunds((f) => [
      ...f,
      {
        id,
        title: "New Gift",
        description: "",
        goal: 1000,
        coverUrl:
          "https://images.unsplash.com/photo-1518684079-3c830dcef090?q=80&w=1200&auto=format&fit=crop",
        category: "Experience",
        visible: true,
      },
    ]);
  };

  const removeFund = (id) => setFunds((f) => f.filter((x) => x.id !== id));

  const saveAllLocal = () => {
    saveRegistry(registry);
    saveFunds(funds);
  };

  const getRegId = () => localStorage.getItem("registry_id");

  const syncToBackend = async () => {
    try {
      let regId = getRegId();
      if (!regId) {
        const created = await apiCreateRegistry({
          couple_names: registry.coupleNames,
          event_date: registry.eventDate,
          location: registry.location,
          currency: registry.currency || DEFAULT_CURRENCY,
          hero_image: registry.heroImage,
          slug: (registry.slug || "amir-leila").toLowerCase(),
        });
        regId = created.id;
        localStorage.setItem("registry_id", regId);
        saveRegistry({ ...registry, slug: created.slug });
      } else {
        await apiUpdateRegistry(regId, {
          couple_names: registry.coupleNames,
          event_date: registry.eventDate,
          location: registry.location,
          currency: registry.currency || DEFAULT_CURRENCY,
          hero_image: registry.heroImage,
          slug: registry.slug,
        });
      }
      const payloadFunds = (funds || []).map((f, idx) => ({
        id: f.id,
        title: f.title,
        description: f.description,
        goal: Number(f.goal || 0),
        cover_url: f.coverUrl,
        category: f.category,
        visible: f.visible !== false,
      }));
      await bulkUpsertFunds(regId, payloadFunds);
      return true;
    } catch (e) {
      console.log("Sync failed, staying local", e?.message);
      return false;
    }
  };

  const saveAll = async () => {
    saveAllLocal();
    const ok = await syncToBackend();
    toast({
      title: ok ? "Saved to cloud" : "Saved locally",
      description: ok ? "Registry synced to backend." : "Backend not reachable, kept local (mock).",
    });
  };

  const publish = async () => {
    setPublishing(true);
    await saveAll();
    setPublishing(false);
    navigate(`/r/${registry.slug || "amir-leila"}`);
  };

  const exportCsv = async () => {
    const regId = getRegId();
    if (!regId) {
      toast({ title: "Create registry first", description: "Please save your registry to enable exports." });
      return;
    }
    try {
      const blob = await exportRegistryCSV(regId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `contributions_${regId}.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      toast({ title: "Export failed", description: e?.message || "Try again." });
    }
  };

  React.useEffect(() => {
    const regId = getRegId();
    if (activeTab === "analytics" && regId) {
      getRegistryAnalytics(regId)
        .then(setAnalytics)
        .catch(() => setAnalytics(null));
    }
  }, [activeTab]);

  return (
    <div className="min-h-screen">
      <div className="max-w-6xl mx-auto px-4 py-6 flex items-center justify-between">
        <Link to="/" className="text-sm text-muted-foreground hover:text-foreground">← Back</Link>
        <div className="flex items-center gap-2">
          <Button variant="secondary" onClick={exportCsv}><ArrowDownToLine className="size-4 mr-2"/>Export CSV</Button>
          <Button variant="secondary" onClick={saveAll}>Save</Button>
          <Button onClick={publish} disabled={publishing}>{publishing ? "Publishing…" : "Preview"}</Button>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 pb-16">
        <Tabs defaultValue="list" value={activeTab} onValueChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="list">Gifts</TabsTrigger>
            <TabsTrigger value="add">Add Gift</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          <TabsContent value="list" className="mt-4">
            <div className="grid lg:grid-cols-[1.2fr_.8fr] gap-8">
              <Card>
                <CardHeader>
                  <CardTitle>Registry details</CardTitle>
                </CardHeader>
                <CardContent className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label>Couple names</Label>
                    <Input
                      value={registry.coupleNames}
                      onChange={(e) => updateRegistry({ coupleNames: e.target.value })}
                      placeholder="Amir & Leila"
                    />
                  </div>
                  <div>
                    <Label>Wedding date</Label>
                    <Input
                      type="date"
                      value={registry.eventDate}
                      onChange={(e) => updateRegistry({ eventDate: e.target.value })}
                    />
                  </div>
                  <div>
                    <Label>Location</Label>
                    <Input
                      value={registry.location}
                      onChange={(e) => updateRegistry({ location: e.target.value })}
                      placeholder="Dubai, UAE"
                    />
                  </div>
                  <div>
                    <Label>Public URL slug</Label>
                    <Input
                      value={registry.slug}
                      onChange={(e) => updateRegistry({ slug: e.target.value.replace(/\s+/g, "-").toLowerCase() })}
                      placeholder="amir-leila"
                    />
                  </div>
                  <div>
                    <Label>Currency</Label>
                    <Select
                      value={registry.currency || DEFAULT_CURRENCY}
                      onValueChange={(v) => updateRegistry({ currency: v })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Currency" />
                      </SelectTrigger>
                      <SelectContent>
                        {["AED", "USD", "EUR", "GBP", "SAR", "QAR"].map((c) => (
                          <SelectItem key={c} value={c}>{c}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="md:col-span-2">
                    <Label>Hero image URL</Label>
                    <Input
                      value={registry.heroImage}
                      onChange={(e) => updateRegistry({ heroImage: e.target.value })}
                      placeholder="https://…"
                    />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Preview</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="rounded-lg overflow-hidden border">
                    <img src={registry.heroImage} alt="Hero" className="w-full h-40 object-cover" />
                    <div className="p-4">
                      <div className="font-medium">{registry.coupleNames}</div>
                      <div className="text-sm text-muted-foreground">{registry.eventDate} — {registry.location}</div>
                      <Button className="mt-4 w-full" onClick={() => navigate(`/r/${registry.slug || "amir-leila"}`)}>
                        Open public page <Eye className="size-4 ml-2" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="mt-8 grid md:grid-cols-3 gap-4">
              {funds.map((f) => (
                <Card key={f.id}>
                  <CardContent className="p-0">
                    <img src={f.coverUrl} alt={f.title} className="w-full h-32 object-cover rounded-t-lg" />
                    <div className="p-4 space-y-3">
                      <div>
                        <Label className="text-xs">Title</Label>
                        <Input
                          value={f.title}
                          onChange={(e) => setFunds((all) => all.map((x) => (x.id === f.id ? { ...x, title: e.target.value } : x)))}
                        />
                      </div>
                      <div>
                        <Label className="text-xs">Description</Label>
                        <Textarea
                          value={f.description}
                          onChange={(e) => setFunds((all) => all.map((x) => (x.id === f.id ? { ...x, description: e.target.value } : x)))}
                        />
                      </div>
                      <div className="grid grid-cols-3 gap-3">
                        <div className="col-span-1">
                          <Label className="text-xs">Goal ({registry.currency || DEFAULT_CURRENCY})</Label>
                          <Input
                            type="number"
                            value={f.goal}
                            onChange={(e) => setFunds((all) => all.map((x) => (x.id === f.id ? { ...x, goal: Number(e.target.value || 0) } : x)))}
                          />
                        </div>
                        <div className="col-span-1">
                          <Label className="text-xs">Category</Label>
                          <Input
                            value={f.category}
                            onChange={(e) => setFunds((all) => all.map((x) => (x.id === f.id ? { ...x, category: e.target.value } : x)))}
                          />
                        </div>
                        <div className="col-span-1 flex items-center gap-2 mt-6">
                          <Switch id={`vis-${f.id}`} checked={f.visible !== false} onCheckedChange={(v) => setFunds((all) => all.map((x) => (x.id === f.id ? { ...x, visible: !!v } : x)))} />
                          <Label htmlFor={`vis-${f.id}`}>Visible</Label>
                        </div>
                      </div>
                      <div>
                        <Label className="text-xs">Image URL</Label>
                        <Input
                          value={f.coverUrl}
                          onChange={(e) => setFunds((all) => all.map((x) => (x.id === f.id ? { ...x, coverUrl: e.target.value } : x)))}
                        />
                      </div>
                      <div className="flex items-center justify-between pt-2">
                        <Button variant="destructive" size="icon" onClick={() => removeFund(f.id)}>
                          <Trash2 className="size-4" />
                        </Button>
                        <Button variant="secondary" onClick={saveAll}>Save</Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="add" className="mt-4">
            <div className="p-6 rounded-lg border">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">Add a new gift</div>
                  <p className="text-sm text-muted-foreground">Create a fund for an experience or a general cash fund.</p>
                </div>
                <Button onClick={addFund}><Plus className="size-4 mr-2"/> Add gift</Button>
              </div>
              <div className="mt-4 flex items-center gap-2">
                <Switch id="general" />
                <Label htmlFor="general">Mark as General Fund</Label>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="analytics" className="mt-4">
            <Card>
              <CardHeader>
                <CardTitle>Analytics</CardTitle>
              </CardHeader>
              <CardContent>
                {!analytics ? (
                  <p className="text-sm text-muted-foreground">No analytics yet or unable to fetch. Save your registry and come back.</p>
                ) : (
                  <div>
                    <div className="grid md:grid-cols-3 gap-4">
                      <Stat label="Total raised" value={formatCurrency(analytics.total, registry.currency)} />
                      <Stat label="Contributions" value={String(analytics.count)} />
                      <Stat label="Average gift" value={formatCurrency(analytics.average, registry.currency)} />
                    </div>
                    <div className="mt-6">
                      <div className="font-medium mb-2">By fund</div>
                      <div className="space-y-2">
                        {analytics.by_fund.map((f) => (
                          <div key={f.fund_id} className="flex items-center justify-between text-sm">
                            <span className="text-muted-foreground">{f.title}</span>
                            <span className="font-medium">{formatCurrency(f.sum, registry.currency)} ({f.count})</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div className="mt-6">
                      <div className="font-medium mb-2">Last 30 days</div>
                      <div className="h-24 flex items-end gap-1">
                        {analytics.daily.length === 0 ? (
                          <p className="text-sm text-muted-foreground">No recent activity</p>
                        ) : (
                          analytics.daily.map((d) => (
                            <div key={d.date} title={`${d.date}: ${d.sum}`} className="bg-primary/20" style={{ height: `${Math.min(100, Math.round((d.sum / (analytics.average * 2 || 1)) * 100))}%`, width: 8 }} />
                          ))
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div className="p-4 rounded-lg border bg-card">
      <div className="text-sm text-muted-foreground">{label}</div>
      <div className="text-xl font-semibold">{value}</div>
    </div>
  );
}

function formatCurrency(amount, currency = "AED") {
  try {
    return new Intl.NumberFormat("en-US", { style: "currency", currency }).format(amount);
  } catch {
    return `${currency} ${Number(amount || 0).toFixed(2)}`;
  }
}