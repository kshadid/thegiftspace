import React from "react";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { Button } from "../components/ui/button";
import { Label } from "../components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Switch } from "../components/ui/switch";
import { Checkbox } from "../components/ui/checkbox";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "../components/ui/dialog";
import { useToast } from "../hooks/use-toast";
import { Link, useNavigate, useLocation } from "react-router-dom";
import {
  loadRegistry,
  saveRegistry,
  loadFunds,
  saveFunds,
  DEFAULT_CURRENCY,
} from "../mock/mock";
import { getAccessToken } from "../lib/api";
import { Plus, Trash2, Eye, EyeOff, ArrowDownToLine, GripVertical, UserPlus, X, Upload as UploadIcon, Copy, Pin, ChevronUp, ChevronDown, Cog } from "lucide-react";
import { createRegistry as apiCreateRegistry, updateRegistry as apiUpdateRegistry, bulkUpsertFunds, getRegistryAnalytics, exportRegistryCSV, getRegistryById, addCollaborator, removeCollaborator } from "../lib/api";
import { uploadFileChunked } from "../lib/uploads";
import { PROFESSIONAL_COPY, getRandomFundSuggestion } from "../utils/professionalCopy";
import { DEFAULT_REGISTRY_IMAGES, getRandomImageByCategory, getRandomRegistryImage } from "../utils/defaultImages";
import ImageSelector from "../components/ImageSelector";

// Use our beautiful curated images instead of random ones
const heroPresets = DEFAULT_REGISTRY_IMAGES.map(img => img.url);

export default function CreateRegistry() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const location = useLocation();

  const [registry, setRegistry] = React.useState(loadRegistry());
  const [funds, setFunds] = React.useState(loadFunds());
  const [analytics, setAnalytics] = React.useState(null);
  const [publishing, setPublishing] = React.useState(false);

  const [collaborators, setCollaborators] = React.useState([]);
  const [collabEmail, setCollabEmail] = React.useState("");

  const [selected, setSelected] = React.useState({});
  const dragId = React.useRef(null);
  const lastAddedId = React.useRef(null);

  const [editingGoalId, setEditingGoalId] = React.useState(null);
  const [goalDraft, setGoalDraft] = React.useState("");

  // If authenticated, do not use sample defaults; start clean in LS
  React.useEffect(() => {
    if (getAccessToken()) {
      // Only reset to empty if we are seeing sample data
      const reg = loadRegistry();
      if (reg && reg.coupleNames === "Amir & Leila") {
        saveRegistry({ coupleNames: "", eventDate: "", location: "", slug: "", heroImage: "", currency: DEFAULT_CURRENCY });
        saveFunds([]);
      }
    }
  }, []);

  const [manageOpen, setManageOpen] = React.useState(false);

  // Helpers
  const updateRegistry = (patch) => setRegistry((r) => ({ ...r, ...patch }));
  const toggleSelect = (id, v) => setSelected((s) => ({ ...s, [id]: v }));
  const selectedIds = Object.keys(selected).filter((k) => selected[k]);
  const getRegId = () => localStorage.getItem("registry_id");

  // Pick up ?rid= and fetch analytics/registry
  React.useEffect(() => {
    const params = new URLSearchParams(location.search);
    const rid = params.get("rid");
    if (rid) localStorage.setItem("registry_id", rid);
  }, [location.search]);

  React.useEffect(() => {
    const regId = getRegId();
    if (!regId) return;
    getRegistryAnalytics(regId).then(setAnalytics).catch(() => setAnalytics(null));
    getRegistryById(regId)
      .then((r) => {
        setRegistry((cur) => ({ ...cur, theme: r.theme || cur.theme, coupleNames: r.couple_names, eventDate: r.event_date, location: r.location, currency: r.currency, slug: r.slug, heroImage: r.hero_image }));
        setCollaborators(r.collaborators || []);
      })
      .catch(() => setCollaborators([]));
  }, []);

  const saveAllLocal = () => { saveRegistry(registry); saveFunds(funds); };
  const silentCloudSave = async () => { try { await syncToBackend(); } catch (_) {} };

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
          theme: registry.theme || "modern",
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
          theme: registry.theme || "modern",
        });
      }
      const payloadFunds = (funds || []).map((f) => ({
        id: f.id,
        title: f.title,
        description: f.description,
        goal: Number(f.goal || 0),
        cover_url: f.coverUrl,
        category: f.category,
        visible: f.visible !== false,
        order: typeof f.order === "number" ? f.order : 0,
        pinned: !!f.pinned,
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
    toast({ title: ok ? "Saved to cloud" : "Saved locally", description: ok ? "Registry synced to backend." : "Backend not reachable, kept local (mock)." });
  };

  const exportCsv = async () => {
    const regId = getRegId();
    if (!regId) return toast({ title: "Create registry first", description: "Please save your registry to enable exports." });
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

  const publish = async () => { setPublishing(true); await saveAll(); setPublishing(false); navigate(`/r/${registry.slug || "amir-leila"}#gifts`); };

  const addFund = () => {
    const id = `fund_${Date.now()}`;
    const nextOrder = funds.length;
    lastAddedId.current = id;
    setFunds((f) => [
      ...f,
      { id, title: "New Gift", description: "", goal: 1000, coverUrl: "https://images.unsplash.com/photo-1518684079-3c830dcef090?q=80&w=1200&auto=format&fit=crop", category: "Experience", visible: true, order: nextOrder, pinned: false },
    ]);
    setTimeout(() => { const el = document.getElementById(`fund-${id}`); if (el) el.scrollIntoView({ behavior: "smooth", block: "center" }); }, 50);
  };

  const duplicateFund = (f) => { const id = `fund_${Date.now()}`; const nextOrder = funds.length; lastAddedId.current = id; setFunds((all) => [...all, { ...f, id, title: `${f.title} (Copy)`, order: nextOrder }]); };
  const removeFund = (id) => setFunds((f) => f.filter((x) => x.id !== id).map((x, i) => ({ ...x, order: i })));

  const onDragStart = (id) => (e) => { dragId.current = id; e.dataTransfer.effectAllowed = "move"; };
  const onDragOver = (id) => (e) => { e.preventDefault(); const from = funds.findIndex((x) => x.id === dragId.current); const to = funds.findIndex((x) => x.id === id); if (from === -1 || to === -1 || from === to) return; const clone = [...funds]; const [moved] = clone.splice(from, 1); clone.splice(to, 0, moved); setFunds(clone.map((x, i) => ({ ...x, order: i }))); };

  const moveFund = (id, delta) => { setFunds((all) => { const idx = all.findIndex((x) => x.id === id); if (idx === -1) return all; const to = Math.max(0, Math.min(all.length - 1, idx + delta)); if (to === idx) return all; const clone = [...all]; const [moved] = clone.splice(idx, 1); clone.splice(to, 0, moved); return clone.map((x, i) => ({ ...x, order: i })); }); };
  const moveFundUp = (id) => moveFund(id, -1);
  const moveFundDown = (id) => moveFund(id, 1);

  const togglePinQuick = (id) => { setFunds((all) => all.map((x) => (x.id === id ? { ...x, pinned: !x.pinned } : x))); silentCloudSave(); };
  const toggleVisibleQuick = (id) => { setFunds((all) => all.map((x) => (x.id === id ? { ...x, visible: !(x.visible !== false ? true : false) } : x))); silentCloudSave(); };

  const startEditGoal = (fund) => { setEditingGoalId(fund.id); setGoalDraft(String(fund.goal ?? 0)); };
  const commitGoal = (id) => { setFunds((all) => all.map((x) => (x.id === id ? { ...x, goal: Number(goalDraft || 0) } : x))); setEditingGoalId(null); silentCloudSave(); };
  const cancelGoal = () => setEditingGoalId(null);

  const addCollab = async () => { const regId = getRegId(); if (!regId || !collabEmail) return; try { await addCollaborator(regId, collabEmail); setCollabEmail(""); toast({ title: "Collaborator added" }); } catch (e) { toast({ title: "Failed to add", description: e?.response?.data?.detail || e?.message }); } };
  const removeCollab = async (userId) => { const regId = getRegId(); try { await removeCollaborator(regId, userId); setCollaborators((list) => list.filter((id) => id !== userId)); toast({ title: "Removed" }); } catch (e) { toast({ title: "Failed to remove", description: e?.response?.data?.detail || e?.message }); } };

  // Simple sparkline SVG
  const Sparkline = ({ values = [], height = 28 }) => {
    if (!values || values.length === 0) return null;
    const max = Math.max(...values, 1);
    const pts = values.map((v, i) => `${(i / (values.length - 1)) * 100},${100 - (v / max) * 100}`).join(" ");
    return (
      <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="w-full" style={{ height }}>
        <polyline fill="none" stroke="currentColor" strokeWidth="2" points={pts} className="text-primary" />
      </svg>
    );
  };

  const dailyVals = (analytics?.daily || []).map((d) => d.sum);

  return (
    <div className="min-h-screen">
      {/* Header */}
      <div className="max-w-6xl mx-auto px-4 py-6 flex items-center justify-between">
        <Link to="/dashboard" className="text-sm text-muted-foreground hover:text-foreground">← Back</Link>
        <div className="flex items-center gap-2">
          <Button variant="secondary" onClick={exportCsv}><ArrowDownToLine className="size-4 mr-2"/>Export CSV</Button>
          <Button variant="secondary" onClick={saveAll}>Save</Button>
          <Button onClick={publish} disabled={publishing}>{publishing ? "Publishing…" : "Preview"}</Button>
        </div>
      </div>

      {/* Top controls + analytics */}
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Button onClick={addFund}><Plus className="size-4 mr-2"/>Add gift</Button>
            <Dialog open={manageOpen} onOpenChange={setManageOpen}>
              <DialogTrigger asChild>
                <Button variant="secondary"><Cog className="size-4 mr-2"/>Manage event</Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[760px]">
                <DialogHeader><DialogTitle>Manage event</DialogTitle></DialogHeader>
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-3">
                    <div>
                      <Label>Couple names</Label>
                      <Input value={registry.coupleNames || ""} onChange={(e) => updateRegistry({ coupleNames: e.target.value })} placeholder="Amir & Leila" />
                    </div>
                    <div>
                      <Label>Wedding date</Label>
                      <Input type="date" value={registry.eventDate || ""} onChange={(e) => updateRegistry({ eventDate: e.target.value })} />
                    </div>
                    <div>
                      <Label>Location</Label>
                      <Input value={registry.location || ""} onChange={(e) => updateRegistry({ location: e.target.value })} placeholder="Dubai, UAE" />
                    </div>
                    <div>
                      <Label>Public URL slug</Label>
                      <Input value={registry.slug || ""} onChange={(e) => updateRegistry({ slug: e.target.value.replace(/\s+/g, "-").toLowerCase() })} placeholder="amir-leila" />
                    </div>
                    <div>
                      <Label>Currency</Label>
                      <Select value={registry.currency || DEFAULT_CURRENCY} onValueChange={(v) => updateRegistry({ currency: v })}>
                        <SelectTrigger><SelectValue placeholder="Currency" /></SelectTrigger>
                        <SelectContent>
                          { ["AED","USD","EUR","GBP","SAR","QAR"].map((c) => (<SelectItem key={c} value={c}>{c}</SelectItem>)) }
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <div>
                      <Label>Hero image</Label>
                      <div className="flex items-center gap-2 mt-1">
                        <Input value={registry.heroImage || ""} onChange={(e) => updateRegistry({ heroImage: e.target.value })} placeholder="https://…" />
                        <label className="inline-flex items-center gap-2 border rounded px-3 py-2 cursor-pointer">
                          <UploadIcon className="size-4" /> Upload
                          <input type="file" accept="image/*" className="hidden" onChange={(e) => e.target.files && uploadFileChunked && uploadFileChunked(e.target.files[0])} />
                        </label>
                      </div>
                      <div className="grid grid-cols-4 gap-2 mt-3">
                        {heroPresets.map((u) => (
                          <button key={u} className="border rounded overflow-hidden hover:opacity-90" onClick={() => updateRegistry({ heroImage: u })}>
                            <img src={u} alt="preset" className="w-full h-16 object-cover" />
                          </button>
                        ))}
                      </div>
                    </div>
                    <div className="pt-2">
                      <div className="font-medium mb-2">Collaborators</div>
                      <div className="flex gap-2">
                        <Input placeholder="email@example.com" value={collabEmail} onChange={(e) => setCollabEmail(e.target.value)} />
                        <Button onClick={addCollab}><UserPlus className="size-4 mr-2"/>Add</Button>
                      </div>
                      <div className="mt-3 space-y-2">
                        { (collaborators || []).length === 0 ? (
                          <p className="text-sm text-muted-foreground">No collaborators yet</p>
                        ) : (
                          collaborators.map((uid) => (
                            <div key={uid} className="flex items-center justify-between text-sm border rounded px-3 py-2">
                              <span className="text-muted-foreground">User ID: {uid}</span>
                              <Button size="icon" variant="destructive" onClick={() => removeCollab(uid)}><X className="size-4"/></Button>
                            </div>
                          ))
                        ) }
                      </div>
                    </div>
                    <div className="pt-2">
                      <Button variant="secondary" onClick={() => { saveAll(); setManageOpen(false); }}>Save changes</Button>
                    </div>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        {/* Analytics strip */}
        <div className="grid md:grid-cols-3 gap-4 mt-6">
          <Card className="hover:shadow-sm transition-shadow">
            <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Total raised</CardTitle></CardHeader>
            <CardContent>
              <div className="text-2xl font-semibold">{formatCurrency(analytics?.total || 0, registry.currency)}</div>
              <div className="mt-2 text-muted-foreground"><Sparkline values={dailyVals} /></div>
            </CardContent>
          </Card>
          <Card className="hover:shadow-sm transition-shadow">
            <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Contributions</CardTitle></CardHeader>
            <CardContent>
              <div className="text-2xl font-semibold">{String(analytics?.count || 0)}</div>
            </CardContent>
          </Card>
          <Card className="hover:shadow-sm transition-shadow">
            <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Average gift</CardTitle></CardHeader>
            <CardContent>
              <div className="text-2xl font-semibold">{formatCurrency(analytics?.average || 0, registry.currency)}</div>
            </CardContent>
          </Card>
        </div>

        <div className="mt-8 border-t" />
      </div>

      {/* Gifts grid */}
      <div className="max-w-6xl mx-auto px-4 pb-20">
        <div className="mt-6 flex items-center justify-between">
          <h2 className="text-xl font-semibold tracking-tight">Gifts</h2>
          <div className="flex items-center gap-2">
            <Button variant="secondary" onClick={() => setFunds((all) => all.map((f) => (selectedIds.includes(f.id) ? { ...f, visible: true } : f)))} disabled={selectedIds.length === 0}>Show selected</Button>
            <Button variant="secondary" onClick={() => setFunds((all) => all.map((f) => (selectedIds.includes(f.id) ? { ...f, visible: false } : f)))} disabled={selectedIds.length === 0}>Hide selected</Button>
            <Button variant="destructive" onClick={() => setFunds((all) => all.filter((f) => !selectedIds.includes(f.id)).map((x, i) => ({ ...x, order: i })))} disabled={selectedIds.length === 0}>Delete selected</Button>
          </div>
        </div>

        <div className="mt-4 grid md:grid-cols-3 gap-6">
          {funds.length === 0 ? (
            <div className="md:col-span-3 p-10 rounded-lg border text-center text-muted-foreground">No gifts yet. Click "Add gift" to begin.</div>
          ) : (
            funds.map((f) => (
              <div key={f.id} id={`fund-${f.id}`} draggable onDragStart={onDragStart(f.id)} onDragOver={onDragOver(f.id)}>
                <Card className="hover:shadow-sm transition-shadow">
                  <CardContent className="p-0">
                    <div className="relative">
                      <img src={f.coverUrl} alt={f.title} className="w-full h-40 object-cover rounded-t-lg" />
                      <div className="absolute top-2 left-2 text-xs bg-black/50 text-white px-2 py-1 rounded flex items-center gap-1"><GripVertical className="size-3"/>Drag</div>
                      <div className="absolute top-2 right-2 flex items-center gap-2">
                        <button className={`text-[10px] px-2 py-1 rounded-full border backdrop-blur ${f.pinned ? 'bg-primary text-primary-foreground border-primary' : 'bg-white/80 text-foreground'}`} onClick={() => togglePinQuick(f.id)} title={f.pinned ? 'Unpin' : 'Pin'}>
                          <span className="inline-flex items-center gap-1"><Pin className="size-3"/> Pin</span>
                        </button>
                        <button className={`text-[10px] px-2 py-1 rounded-full border backdrop-blur ${f.visible !== false ? 'bg-white/80 text-foreground' : 'bg-destructive text-destructive-foreground border-destructive'}`} onClick={() => toggleVisibleQuick(f.id)} title={f.visible !== false ? 'Hide' : 'Show'}>
                          <span className="inline-flex items-center gap-1">{f.visible !== false ? <Eye className="size-3"/> : <EyeOff className="size-3"/>} {f.visible !== false ? 'Visible' : 'Hidden'}</span>
                        </button>
                      </div>
                    </div>
                    <div className="p-4 space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Checkbox id={`sel-${f.id}`} checked={!!selected[f.id]} onCheckedChange={(v) => toggleSelect(f.id, v)} />
                          <Label htmlFor={`sel-${f.id}`} className="text-xs">Select</Label>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button size="icon" variant="secondary" onClick={() => moveFundUp(f.id)} title="Move up"><ChevronUp className="size-4"/></Button>
                          <Button size="icon" variant="secondary" onClick={() => moveFundDown(f.id)} title="Move down"><ChevronDown className="size-4"/></Button>
                          <Button size="icon" variant="secondary" onClick={() => duplicateFund(f)} title="Duplicate"><Copy className="size-4"/></Button>
                          <Button size="icon" variant="destructive" onClick={() => removeFund(f.id)} title="Delete"><Trash2 className="size-4" /></Button>
                        </div>
                      </div>
                      <div className="flex items-center justify-between gap-2">
                        <div className="flex-1">
                          <Label className="text-xs">Title</Label>
                          <Input value={f.title} onChange={(e) => setFunds((all) => all.map((x) => (x.id === f.id ? { ...x, title: e.target.value } : x)))} />
                        </div>
                        <div className="mt-5">
                          {editingGoalId === f.id ? (
                            <div className="flex items-center gap-2">
                              <Input type="number" value={goalDraft} onChange={(e) => setGoalDraft(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter') commitGoal(f.id); if (e.key === 'Escape') cancelGoal(); }} onBlur={() => commitGoal(f.id)} className="w-28 h-8 text-xs" />
                            </div>
                          ) : (
                            <button className="text-xs border rounded px-2 py-1 hover:bg-accent" onClick={() => startEditGoal(f)} title="Edit goal">
                              Goal: {registry.currency || DEFAULT_CURRENCY} {Number(f.goal || 0).toLocaleString()}
                            </button>
                          )}
                        </div>
                      </div>
                      <div>
                        <Label className="text-xs">Description</Label>
                        <Textarea value={f.description} onChange={(e) => setFunds((all) => all.map((x) => (x.id === f.id ? { ...x, description: e.target.value } : x)))} />
                      </div>
                      <div className="grid grid-cols-3 gap-3">
                        <div>
                          <Label className="text-xs">Category</Label>
                          <Input value={f.category} onChange={(e) => setFunds((all) => all.map((x) => (x.id === f.id ? { ...x, category: e.target.value } : x)))} />
                        </div>
                        <div className="col-span-2 flex items-center gap-3 justify-end">
                          <label className="inline-flex items-center gap-1 text-xs border rounded px-2 py-1 cursor-pointer ml-auto">
                            <UploadIcon className="size-3"/> Image
                            <input type="file" accept="image/*" className="hidden" onChange={(e) => e.target.files && uploadFileChunked && uploadFileChunked(e.target.files[0])} />
                          </label>
                        </div>
                      </div>
                      <div className="flex items-center justify-between pt-2">
                        <div className="text-xs text-muted-foreground">Order: {f.order ?? 0}</div>
                        <Button variant="secondary" onClick={saveAll}>Save</Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

function formatCurrency(amount, currency = "AED") {
  try { return new Intl.NumberFormat("en-US", { style: "currency", currency }).format(amount); }
  catch { return `${currency} ${Number(amount || 0).toFixed(2)}`; }
}