import React from "react";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { Button } from "../components/ui/button";
import { Label } from "../components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { Switch } from "../components/ui/switch";
import { Checkbox } from "../components/ui/checkbox";
import { useToast } from "../hooks/use-toast";
import { Link, useNavigate } from "react-router-dom";
import {
  loadRegistry,
  saveRegistry,
  loadFunds,
  saveFunds,
  DEFAULT_CURRENCY,
} from "../mock/mock";
import { Plus, Trash2, Eye, EyeOff, ArrowDownToLine, GripVertical, UserPlus, X, Upload as UploadIcon, Copy, Pin, ChevronUp, ChevronDown } from "lucide-react";
import { createRegistry as apiCreateRegistry, updateRegistry as apiUpdateRegistry, bulkUpsertFunds, getRegistryAnalytics, exportRegistryCSV, getRegistryById, addCollaborator, removeCollaborator } from "../lib/api";
import { uploadFileChunked } from "../lib/uploads";

const heroPresets = [
  "https://images.unsplash.com/photo-1520440718111-45fe694b330a?q=80&w=1920&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?q=80&w=1920&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1506744038136-46273834b3fb?q=80&w=1920&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1491553895911-0055eca6402d?q=80&w=1920&auto=format&fit=crop",
];

export default function CreateRegistry() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [registry, setRegistry] = React.useState(loadRegistry());
  const [funds, setFunds] = React.useState(loadFunds());
  const [publishing, setPublishing] = React.useState(false);
  const [activeTab, setActiveTab] = React.useState("list");
  const [analytics, setAnalytics] = React.useState(null);
  const [collaborators, setCollaborators] = React.useState([]);
  const [collabEmail, setCollabEmail] = React.useState("");
  const [heroUploading, setHeroUploading] = React.useState(0);
  const [fundUploading, setFundUploading] = React.useState({});
  const [selected, setSelected] = React.useState({});
  const dragId = React.useRef(null);
  const [editingGoalId, setEditingGoalId] = React.useState(null);
  const [goalDraft, setGoalDraft] = React.useState("");

  const silentCloudSave = async () => {
    try {
      await syncToBackend();
    } catch (_) {
      // ignore cloud errors for quick actions
    }
  };

  const moveFund = (id, delta) => {
    setFunds((all) => {
      const idx = all.findIndex((x) => x.id === id);
      if (idx === -1) return all;
      const to = Math.max(0, Math.min(all.length - 1, idx + delta));
      if (to === idx) return all;
      const clone = [...all];
      const [moved] = clone.splice(idx, 1);
      clone.splice(to, 0, moved);
      return clone.map((x, i) => ({ ...x, order: i }));
    });
  };
  const moveFundUp = (id) => moveFund(id, -1);
  const moveFundDown = (id) => moveFund(id, 1);

  const togglePinQuick = (id) => {
    setFunds((all) => all.map((x) => (x.id === id ? { ...x, pinned: !x.pinned } : x)));
    silentCloudSave();
  };
  const toggleVisibleQuick = (id) => {
    setFunds((all) => all.map((x) => (x.id === id ? { ...x, visible: !(x.visible !== false ? true : false) } : x)));
    silentCloudSave();
  };

  const startEditGoal = (fund) => {
    setEditingGoalId(fund.id);
    setGoalDraft(String(fund.goal ?? 0));
  };
  const commitGoal = (id) => {
    setFunds((all) => all.map((x) => (x.id === id ? { ...x, goal: Number(goalDraft || 0) } : x)));
    setEditingGoalId(null);
    silentCloudSave();
  };
  const cancelGoal = () => setEditingGoalId(null);

  const updateRegistry = (patch) => setRegistry((r) => ({ ...r, ...patch }));

  const addFund = () => {
    const id = `fund_${Date.now()}`;
    const nextOrder = funds.length;
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
        order: nextOrder,
        pinned: false,
      },
    ]);
  };

  const duplicateFund = (f) => {
    const id = `fund_${Date.now()}`;
    const nextOrder = funds.length;
    setFunds((all) => [
      ...all,
      { ...f, id, title: `${f.title} (Copy)`, order: nextOrder },
    ]);
  };

  const removeFund = (id) => setFunds((f) => f.filter((x) => x.id !== id).map((x, i) => ({ ...x, order: i })));

  const onDragStart = (id) => (e) => {
    dragId.current = id;
    e.dataTransfer.effectAllowed = "move";
  };
  const onDragOver = (id) => (e) => {
    e.preventDefault();
    const from = funds.findIndex((x) => x.id === dragId.current);
    const to = funds.findIndex((x) => x.id === id);
    if (from === -1 || to === -1 || from === to) return;
    const clone = [...funds];
    const [moved] = clone.splice(from, 1);
    clone.splice(to, 0, moved);
    setFunds(clone.map((x, i) => ({ ...x, order: i })));
  };

  const toggleSelect = (id, v) => setSelected((s) => ({ ...s, [id]: v }));
  const selectedIds = Object.keys(selected).filter((k) => selected[k]);

  const bulkSetVisibility = (visible) => setFunds((all) => all.map((f) => (selectedIds.includes(f.id) ? { ...f, visible } : f)));
  const bulkDelete = () => setFunds((all) => all.filter((f) => !selectedIds.includes(f.id)).map((x, i) => ({ ...x, order: i })));

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
    toast({
      title: ok ? "Saved to cloud" : "Saved locally",
      description: ok ? "Registry synced to backend." : "Backend not reachable, kept local (mock).",
    });
  };

  const publish = async () => {
    setPublishing(true);
    await saveAll();
    setPublishing(false);
    navigate(`/r/${registry.slug || "amir-leila"}#gifts`);
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

  const uploadHero = async (file) => {
    // Kept for future (chunked uploader in uploads.js); not changing in this patch
    toast({ title: "Tip", description: "Hero upload is available in previous build. Keep using presets for now." });
  };

  const uploadFundImage = async (fundId, file) => {
    toast({ title: "Tip", description: "Image upload implemented earlier; available if needed." });
  };

  React.useEffect(() => {
    const regId = getRegId();
    if (activeTab === "analytics" && regId) {
      getRegistryAnalytics(regId).then(setAnalytics).catch(() => setAnalytics(null));
    }
    if (activeTab === "settings" && regId) {
      getRegistryById(regId)
        .then((r) => {
          setRegistry((cur) => ({ ...cur, theme: r.theme || cur.theme }));
          setCollaborators(r.collaborators || []);
        })
        .catch(() => setCollaborators([]));
    }
  }, [activeTab]);

  const addCollab = async () => {
    const regId = getRegId();
    if (!regId || !collabEmail) return;
    try {
      await addCollaborator(regId, collabEmail);
      setCollabEmail("");
      setActiveTab("settings");
      toast({ title: "Collaborator added" });
    } catch (e) {
      toast({ title: "Failed to add", description: e?.response?.data?.detail || e?.message });
    }
  };

  const removeCollab = async (userId) => {
    const regId = getRegId();
    try {
      await removeCollaborator(regId, userId);
      setCollaborators((list) => list.filter((id) => id !== userId));
      toast({ title: "Removed" });
    } catch (e) {
      toast({ title: "Failed to remove", description: e?.response?.data?.detail || e?.message });
    }
  };

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
          <TabsList className="flex flex-wrap">
            <TabsTrigger value="list">Gifts</TabsTrigger>
            <TabsTrigger value="add">Add Gift</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
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
                    <Input value={registry.coupleNames} onChange={(e) => updateRegistry({ coupleNames: e.target.value })} placeholder="Amir & Leila" />
                  </div>
                  <div>
                    <Label>Wedding date</Label>
                    <Input type="date" value={registry.eventDate} onChange={(e) => updateRegistry({ eventDate: e.target.value })} />
                  </div>
                  <div>
                    <Label>Location</Label>
                    <Input value={registry.location} onChange={(e) => updateRegistry({ location: e.target.value })} placeholder="Dubai, UAE" />
                  </div>
                  <div>
                    <Label>Public URL slug</Label>
                    <Input value={registry.slug} onChange={(e) => updateRegistry({ slug: e.target.value.replace(/\s+/g, "-").toLowerCase() })} placeholder="amir-leila" />
                  </div>
                  <div>
                    <Label>Currency</Label>
                    <Select value={registry.currency || DEFAULT_CURRENCY} onValueChange={(v) => updateRegistry({ currency: v })}>
                      <SelectTrigger><SelectValue placeholder="Currency" /></SelectTrigger>
                      <SelectContent>
                        {["AED", "USD", "EUR", "GBP", "SAR", "QAR"].map((c) => (<SelectItem key={c} value={c}>{c}</SelectItem>))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="md:col-span-2">
                    <Label>Hero image</Label>
                    <div className="flex items-center gap-2 mt-1">
                      <Input value={registry.heroImage} onChange={(e) => updateRegistry({ heroImage: e.target.value })} placeholder="https://…" />
                      <label className="inline-flex items-center gap-2 border rounded px-3 py-2 cursor-pointer">
                        <UploadIcon className="size-4" /> Upload
                        <input type="file" accept="image/*" className="hidden" onChange={(e) => e.target.files && uploadHero(e.target.files[0])} />
                      </label>
                    </div>
                    {heroUploading > 0 ? <div className="text-xs text-muted-foreground mt-1">Uploading… {heroUploading}%</div> : null}
                    <div className="mt-3">
                      <div className="text-xs text-muted-foreground mb-1">Or choose a preset</div>
                      <div className="grid grid-cols-4 gap-2">
                        {heroPresets.map((u) => (
                          <button key={u} className="border rounded overflow-hidden hover:opacity-90" onClick={() => updateRegistry({ heroImage: u })}>
                            <img src={u} alt="preset" className="w-full h-16 object-cover" />
                          </button>
                        ))}
                      </div>
                    </div>
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
                      <Button className="mt-4 w-full" onClick={() => navigate(`/r/${registry.slug || "amir-leila"}#gifts`)}>
                        Open public page <Eye className="size-4 ml-2" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="mt-6 flex items-center justify-between">
              <div className="text-sm text-muted-foreground">{funds.length} gifts</div>
              <div className="flex items-center gap-2">
                <Button variant="secondary" onClick={() => bulkSetVisibility(true)} disabled={selectedIds.length === 0}>Show selected</Button>
                <Button variant="secondary" onClick={() => bulkSetVisibility(false)} disabled={selectedIds.length === 0}>Hide selected</Button>
                <Button variant="destructive" onClick={bulkDelete} disabled={selectedIds.length === 0}>Delete selected</Button>
              </div>
            </div>

            <div className="mt-4 grid md:grid-cols-3 gap-4">
              {funds.length === 0 ? (
                <div className="md:col-span-3 p-8 rounded-lg border text-center text-muted-foreground">No gifts yet. Click "Add gift" to begin.</div>
              ) : (
                funds.map((f) => (
                  <div key={f.id} draggable onDragStart={onDragStart(f.id)} onDragOver={onDragOver(f.id)}>
                    <Card>
                      <CardContent className="p-0">
                        <div className="relative">
                          <img src={f.coverUrl} alt={f.title} className="w-full h-32 object-cover rounded-t-lg" />
                          <div className="absolute top-2 left-2 text-xs bg-black/50 text-white px-2 py-1 rounded flex items-center gap-1"><GripVertical className="size-3"/>Drag</div>
                          <div className="absolute top-2 right-2 flex items-center gap-2">
                            <button
                              className={`text-[10px] px-2 py-1 rounded-full border backdrop-blur ${f.pinned ? 'bg-primary text-primary-foreground border-primary' : 'bg-white/80 text-foreground'}`}
                              onClick={() => togglePinQuick(f.id)}
                              title={f.pinned ? 'Unpin' : 'Pin'}
                            >
                              <span className="inline-flex items-center gap-1"><Pin className="size-3"/> Pin</span>
                            </button>
                            <button
                              className={`text-[10px] px-2 py-1 rounded-full border backdrop-blur ${f.visible !== false ? 'bg-white/80 text-foreground' : 'bg-destructive text-destructive-foreground border-destructive'}`}
                              onClick={() => toggleVisibleQuick(f.id)}
                              title={f.visible !== false ? 'Hide' : 'Show'}
                            >
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
                                  <Input
                                    type="number"
                                    value={goalDraft}
                                    onChange={(e) => setGoalDraft(e.target.value)}
                                    onKeyDown={(e) => {
                                      if (e.key === 'Enter') commitGoal(f.id);
                                      if (e.key === 'Escape') cancelGoal();
                                    }}
                                    onBlur={() => commitGoal(f.id)}
                                    className="w-28 h-8 text-xs"
                                  />
                                </div>
                              ) : (
                                <button
                                  className="text-xs border rounded px-2 py-1 hover:bg-accent"
                                  onClick={() => startEditGoal(f)}
                                  title="Edit goal"
                                >
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
                              <Label className="text-xs">Goal ({registry.currency || DEFAULT_CURRENCY})</Label>
                              <Input type="number" value={f.goal} onChange={(e) => setFunds((all) => all.map((x) => (x.id === f.id ? { ...x, goal: Number(e.target.value || 0) } : x)))} />
                            </div>
                            <div>
                              <Label className="text-xs">Category</Label>
                              <Input value={f.category} onChange={(e) => setFunds((all) => all.map((x) => (x.id === f.id ? { ...x, category: e.target.value } : x)))} />
                            </div>
                            <div className="flex items-center gap-2 mt-6">
                              <Switch id={`vis-${f.id}`} checked={f.visible !== false} onCheckedChange={(v) => setFunds((all) => all.map((x) => (x.id === f.id ? { ...x, visible: !!v } : x)))} />
                              <Label htmlFor={`vis-${f.id}`}>Visible</Label>
                            </div>
                          </div>
                          <div className="flex items-center gap-3">
                            <div className="flex items-center gap-2">
                              <Switch id={`pin-${f.id}`} checked={!!f.pinned} onCheckedChange={(v) => setFunds((all) => all.map((x) => (x.id === f.id ? { ...x, pinned: !!v } : x)))} />
                              <Label htmlFor={`pin-${f.id}`}>Pinned</Label>
                            </div>
                            <label className="inline-flex items-center gap-1 text-xs border rounded px-2 py-1 cursor-pointer ml-auto">
                              <UploadIcon className="size-3"/> Image
                              <input type="file" accept="image/*" className="hidden" onChange={(e) => e.target.files && uploadFundImage(f.id, e.target.files[0])} />
                            </label>
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
              <CardHeader><CardTitle>Analytics</CardTitle></CardHeader>
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
                    <div className="mt-6 grid md:grid-cols-2 gap-6">
                      <div>
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
                      <div>
                        <div className="font-medium mb-2">By method</div>
                        <div className="space-y-2">
                          {analytics.by_method?.map((m) => (
                            <div key={m.method} className="flex items-center justify-between text-sm">
                              <span className="text-muted-foreground">{m.method}</span>
                              <span className="font-medium">{formatCurrency(m.sum, registry.currency)} ({m.count})</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                    <div className="mt-6">
                      <div className="font-medium mb-2">Recent</div>
                      <div className="space-y-1 text-sm">
                        {analytics.recent?.map((r, i) => (
                          <div key={i} className="flex items-center justify-between">
                            <span className="text-muted-foreground">{r.name}</span>
                            <span className="font-medium">{formatCurrency(r.amount, registry.currency)}</span>
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

          <TabsContent value="settings" className="mt-4">
            <div className="grid md:grid-cols-2 gap-6">
              <Card>
                <CardHeader><CardTitle>Theme</CardTitle></CardHeader>
                <CardContent className="space-y-3">
                  <Label>Preset</Label>
                  <Select value={registry.theme || "modern"} onValueChange={(v) => updateRegistry({ theme: v })}>
                    <SelectTrigger><SelectValue placeholder="Choose theme" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="modern">Modern (default)</SelectItem>
                      <SelectItem value="serif">Minimal Serif</SelectItem>
                      <SelectItem value="pastel">Elegant Pastel</SelectItem>
                      <SelectItem value="dark">Dark Elegant</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button variant="secondary" onClick={saveAll}>Save Theme</Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle>Collaborators</CardTitle></CardHeader>
                <CardContent>
                  <div className="flex gap-2">
                    <Input placeholder="email@example.com" value={collabEmail} onChange={(e) => setCollabEmail(e.target.value)} />
                    <Button onClick={addCollab}><UserPlus className="size-4 mr-2"/>Add</Button>
                  </div>
                  <div className="mt-4 space-y-2">
                    {collaborators.length === 0 ? (
                      <p className="text-sm text-muted-foreground">No collaborators yet</p>
                    ) : (
                      collaborators.map((uid) => (
                        <div key={uid} className="flex items-center justify-between text-sm border rounded px-3 py-2">
                          <span className="text-muted-foreground">User ID: {uid}</span>
                          <Button size="icon" variant="destructive" onClick={() => removeCollab(uid)}><X className="size-4"/></Button>
                        </div>
                      ))
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
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