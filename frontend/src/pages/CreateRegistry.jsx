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
import { Plus, Trash2, Eye } from "lucide-react";

export default function CreateRegistry() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [registry, setRegistry] = React.useState(loadRegistry());
  const [funds, setFunds] = React.useState(loadFunds());
  const [publishing, setPublishing] = React.useState(false);

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
          "https://images.unsplash.com/photo-1518684079-3c830dcef090?q=80&amp;w=1200&amp;auto=format&amp;fit=crop",
        category: "Experience",
      },
    ]);
  };

  const removeFund = (id) => setFunds((f) => f.filter((x) => x.id !== id));

  const saveAll = () => {
    saveRegistry(registry);
    saveFunds(funds);
    toast({
      title: "Saved",
      description: "Your registry has been saved locally (mock).",
    });
  };

  const publish = async () => {
    setPublishing(true);
    saveAll();
    setTimeout(() => {
      setPublishing(false);
      navigate(`/r/${registry.slug || "amir-leila"}`);
    }, 400);
  };

  return (
    <div className="min-h-screen">
      <div className="max-w-6xl mx-auto px-4 py-6 flex items-center justify-between">
        <Link to="/" className="text-sm text-muted-foreground hover:text-foreground">← Back</Link>
        <div className="flex items-center gap-2">
          <Button variant="secondary" onClick={saveAll}>Save</Button>
          <Button onClick={publish} disabled={publishing}>{publishing ? "Publishing…" : "Preview"}</Button>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 pb-16 grid lg:grid-cols-[1.2fr_.8fr] gap-8">
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
                placeholder="Amir &amp; Leila"
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
                  {[
                    "AED",
                    "USD",
                    "EUR",
                    "GBP",
                    "SAR",
                    "QAR",
                  ].map((c) => (
                    <SelectItem key={c} value={c}>
                      {c}
                    </SelectItem>
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

        <div className="lg:col-span-2">
          <Tabs defaultValue="list">
            <TabsList>
              <TabsTrigger value="list">Gifts</TabsTrigger>
              <TabsTrigger value="add">Add Gift</TabsTrigger>
            </TabsList>
            <TabsContent value="list" className="mt-4">
              <div className="grid md:grid-cols-3 gap-4">
                {funds.map((f) => (
                  <Card key={f.id}>
                    <CardContent className="p-0">
                      <img src={f.coverUrl} alt={f.title} className="w-full h-32 object-cover rounded-t-lg" />
                      <div className="p-4 space-y-3">
                        <div>
                          <Label className="text-xs">Title</Label>
                          <Input
                            value={f.title}
                            onChange={(e) =>
                              setFunds((all) => all.map((x) => (x.id === f.id ? { ...x, title: e.target.value } : x)))
                            }
                          />
                        </div>
                        <div>
                          <Label className="text-xs">Description</Label>
                          <Textarea
                            value={f.description}
                            onChange={(e) =>
                              setFunds((all) => all.map((x) => (x.id === f.id ? { ...x, description: e.target.value } : x)))
                            }
                          />
                        </div>
                        <div className="grid grid-cols-2 gap-3">
                          <div>
                            <Label className="text-xs">Goal ({registry.currency || DEFAULT_CURRENCY})</Label>
                            <Input
                              type="number"
                              value={f.goal}
                              onChange={(e) =>
                                setFunds((all) => all.map((x) => (x.id === f.id ? { ...x, goal: Number(e.target.value || 0) } : x)))
                              }
                            />
                          </div>
                          <div>
                            <Label className="text-xs">Category</Label>
                            <Input
                              value={f.category}
                              onChange={(e) =>
                                setFunds((all) => all.map((x) => (x.id === f.id ? { ...x, category: e.target.value } : x)))
                              }
                            />
                          </div>
                        </div>
                        <div>
                          <Label className="text-xs">Image URL</Label>
                          <Input
                            value={f.coverUrl}
                            onChange={(e) =>
                              setFunds((all) => all.map((x) => (x.id === f.id ? { ...x, coverUrl: e.target.value } : x)))
                            }
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
          </Tabs>
        </div>
      </div>
    </div>
  );
}