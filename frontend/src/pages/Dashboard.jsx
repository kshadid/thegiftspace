import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "../components/ui/dialog";
import { listMyRegistries, createRegistry, getRegistryAnalytics, listFunds } from "../lib/api";
import { Plus, ExternalLink, TrendingUp } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Dashboard() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [registries, setRegistries] = React.useState([]);
  const [stats, setStats] = React.useState({ totalRaised: 0, totalContribs: 0 });
  const [byId, setById] = React.useState({});
  const [open, setOpen] = React.useState(false);
  const [form, setForm] = React.useState({ couple_names: "", event_date: "", location: "Dubai, UAE", currency: "AED", slug: "", theme: "modern" });
  const [loading, setLoading] = React.useState(false);

  React.useEffect(() => {
    const load = async () => {
      try {
        const items = await listMyRegistries();
        setRegistries(items || []);
        // fetch analytics and fund counts in parallel
        const results = await Promise.all((items || []).map(async (r) => {
          const [a, f] = await Promise.all([
            getRegistryAnalytics(r.id).catch(() => ({ total: 0, count: 0 })),
            listFunds(r.id).catch(() => []),
          ]);
          return { id: r.id, analytics: a, fundsCount: f.length };
        }));
        const map = {};
        let totalRaised = 0, totalContribs = 0;
        results.forEach((x) => { map[x.id] = x; totalRaised += x.analytics.total || 0; totalContribs += x.analytics.count || 0; });
        setById(map);
        setStats({ totalRaised, totalContribs });
      } catch (e) {
        setRegistries([]);
      }
    };
    load();
  }, []);

  const onCreate = async (e) => {
    e.preventDefault();
    if (!form.couple_names || !form.slug) return;
    try {
      setLoading(true);
      const created = await createRegistry({ ...form, slug: form.slug.toLowerCase() });
      // set current registry id for editor
      localStorage.setItem("registry_id", created.id);
      setOpen(false);
      navigate(`/create?rid=${created.id}`);
    } catch (e) {
      alert(e?.response?.data?.detail || e?.message || "Failed to create");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-40 bg-white/80 backdrop-blur border-b">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link to="/" className="font-semibold text-lg tracking-tight">The giftspace</Link>
          <div className="flex items-center gap-3 text-sm">
            <span className="text-muted-foreground">{user?.name}</span>
            <Button variant="secondary" onClick={() => navigate("/create")}>Manage</Button>
            <Button variant="destructive" onClick={logout}>Logout</Button>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="grid md:grid-cols-3 gap-4">
          <Card>
            <CardHeader><CardTitle>Total received in gifts</CardTitle></CardHeader>
            <CardContent className="text-2xl font-semibold">{formatCurrency(stats.totalRaised)}</CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Gifts received</CardTitle></CardHeader>
            <CardContent className="text-2xl font-semibold">{stats.totalContribs}</CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Gift registries</CardTitle></CardHeader>
            <CardContent className="text-2xl font-semibold">{registries.length}</CardContent>
          </Card>
        </div>

        <div className="flex items-center justify-between mt-8">
          <h2 className="text-xl font-semibold">Your gift registries</h2>
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
              <Button><Plus className="size-4 mr-2"/>New gift registry</Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[520px]">
              <DialogHeader>
                <DialogTitle>Create a new gift registry</DialogTitle>
              </DialogHeader>
              <form className="grid gap-3" onSubmit={onCreate}>
                <div>
                  <Label className="text-xs">Couple names</Label>
                  <Input value={form.couple_names} onChange={(e) => setForm({ ...form, couple_names: e.target.value })} placeholder="Sarah & Ahmed" required />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <Label className="text-xs">Wedding date</Label>
                    <Input type="date" value={form.event_date} onChange={(e) => setForm({ ...form, event_date: e.target.value })} />
                  </div>
                  <div>
                    <Label className="text-xs">Location</Label>
                    <Input value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} />
                  </div>
                </div>
                <div>
                  <Label className="text-xs">Public URL slug</Label>
                  <Input value={form.slug} onChange={(e) => setForm({ ...form, slug: e.target.value.replace(/\s+/g, "-").toLowerCase() })} placeholder="sarah-ahmed" required />
                </div>
                <div className="pt-2">
                  <Button type="submit" disabled={loading}>{loading ? "Creating…" : "Create gift registry"}</Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mt-4">
          {registries.length === 0 ? (
            <div className="md:col-span-3 p-8 rounded-lg border text-center text-muted-foreground">No events yet. Create your first one.</div>
          ) : (
            registries.map((r) => (
              <Card key={r.id} className="overflow-hidden">
                <CardContent className="p-0">
                  <div className="p-5 space-y-2">
                    <div className="text-sm text-muted-foreground">{r.event_date} — {r.location}</div>
                    <div className="text-lg font-semibold">{r.couple_names}</div>
                    <div className="text-sm text-muted-foreground">Slug: {r.slug}</div>
                    <div className="mt-3 grid grid-cols-3 gap-3 text-sm">
                      <div className="rounded-md border p-2">
                        <div className="text-xs text-muted-foreground">Funds</div>
                        <div className="font-medium">{byId[r.id]?.fundsCount ?? 0}</div>
                      </div>
                      <div className="rounded-md border p-2">
                        <div className="text-xs text-muted-foreground">Raised</div>
                        <div className="font-medium">{formatCurrency(byId[r.id]?.analytics?.total || 0, r.currency)}</div>
                      </div>
                      <div className="rounded-md border p-2">
                        <div className="text-xs text-muted-foreground">Gifts</div>
                        <div className="font-medium">{byId[r.id]?.analytics?.count || 0}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 pt-3">
                      <Button onClick={() => { localStorage.setItem("registry_id", r.id); navigate(`/create?rid=${r.id}`); }}>Manage</Button>
                      <Button variant="secondary" onClick={() => navigate(`/r/${r.slug}`)}>View public <ExternalLink className="size-4 ml-1"/></Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>

        <div className="mt-10 p-6 rounded-lg border bg-muted/30">
          <div className="flex items-center gap-2 font-medium"><TrendingUp className="size-4"/> Latest numbers</div>
          <div className="text-sm text-muted-foreground mt-1">Aggregated across your events.</div>
        </div>
      </div>
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