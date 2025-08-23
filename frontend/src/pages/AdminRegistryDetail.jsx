import React from "react";
import { useParams, Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Label } from "../components/ui/label";
import { Input } from "../components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "../components/ui/dialog";
import { adminMe, getRegistryById, adminRegistryFunds, adminSetRegistryLock } from "../lib/api";
import api from "../lib/api";

export default function AdminRegistryDetail() {
  const { id } = useParams();
  const [authorized, setAuthorized] = React.useState(false);
  const [registry, setRegistry] = React.useState(null);
  const [funds, setFunds] = React.useState([]);
  const [contribs, setContribs] = React.useState([]);
  const [audit, setAudit] = React.useState([]);
  const [lockOpen, setLockOpen] = React.useState(false);
  const [reason, setReason] = React.useState("");

  React.useEffect(() => {
    adminMe().then((m) => setAuthorized(!!m.is_admin)).catch(() => setAuthorized(false));
  }, []);

  React.useEffect(() => {
    if (!authorized) return;
    const load = async () => {
      try {
        const [r, f] = await Promise.all([
          getRegistryById(id),
          adminRegistryFunds(id)
        ]);
        setRegistry(r);
        setFunds(f);
        const contribResp = await api.get(`/registries/${id}/contributions`);
        setContribs(contribResp.data || []);
        const auditResp = await api.get(`/registries/${id}/audit`);
        setAudit(auditResp.data || []);
      } catch (e) {
        // ignore
      }
    };
    load();
  }, [authorized, id]);

  if (!authorized) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-24 text-center">
        <h1 className="text-2xl font-semibold">Not authorized</h1>
        <Link className="inline-block mt-6 underline" to="/">Back to home</Link>
      </div>
    );
  }

  if (!registry) return <div className="p-10 text-center">Loading…</div>;

  return (
    <div className="min-h-screen">
      <div className="max-w-6xl mx-auto px-4 py-6 flex items-center justify-between">
        <Link to="/admin" className="text-sm text-muted-foreground hover:text-foreground">← Back</Link>
        <div className="font-medium">Admin • {registry.couple_names} ({registry.slug})</div>
      </div>

      <div className="max-w-6xl mx-auto px-4">
        <div className="grid md:grid-cols-3 gap-6">
          <Card>
            <CardHeader><CardTitle>Event</CardTitle></CardHeader>
            <CardContent className="text-sm space-y-1">
              <div>Owner ID: {registry.owner_id}</div>
              <div>Collaborators: {(registry.collaborators || []).length}</div>
              <div>Status: {registry.locked ? "Locked" : "Active"}</div>
              {registry.lock_reason ? <div className="text-xs text-muted-foreground">Reason: {registry.lock_reason}</div> : null}
              <div className="pt-2 flex gap-2">
                <Button onClick={() => { setLockOpen(true); setReason(registry.lock_reason || ""); }}>Lock / Unlock</Button>
                <a className="underline text-sm" href={`/r/${registry.slug}`} target="_blank" rel="noreferrer">View public</a>
              </div>
            </CardContent>
          </Card>
          <Card className="md:col-span-2">
            <CardHeader><CardTitle>Funds ({funds.length})</CardTitle></CardHeader>
            <CardContent>
              <ul className="text-sm grid md:grid-cols-2 gap-2">
                {funds.map((f) => (
                  <li key={f.id} className="rounded border p-2">
                    <div className="font-medium">{f.title}</div>
                    <div className="text-xs text-muted-foreground">{f.category} • Goal {formatCurrency(f.goal, registry.currency)} • {f.visible !== false ? 'Visible' : 'Hidden'}</div>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mt-6">
          <Card>
            <CardHeader><CardTitle>Latest contributions</CardTitle></CardHeader>
            <CardContent>
              <ul className="text-sm space-y-2">
                {(contribs || []).slice(0, 20).map((c) => (
                  <li key={c.id} className="rounded border p-2 flex items-center justify-between">
                    <span>{c.name || 'Guest'} — {formatCurrency(c.amount, registry.currency)}</span>
                    <span className="text-xs text-muted-foreground">{new Date(c.created_at).toLocaleString()}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Audit log</CardTitle></CardHeader>
            <CardContent>
              <ul className="text-sm space-y-2 max-h-80 overflow-auto">
                {(audit || []).map((a) => (
                  <li key={a.id} className="rounded border p-2">
                    <div className="flex items-center justify-between">
                      <div className="font-medium text-xs">{a.action}</div>
                      <div className="text-xs text-muted-foreground">{new Date(a.created_at).toLocaleString()}</div>
                    </div>
                    <pre className="text-xs mt-1 text-muted-foreground">{JSON.stringify(a.meta || {}, null, 0)}</pre>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>

      <Dialog open={lockOpen} onOpenChange={setLockOpen}>
        <DialogContent className="sm:max-w-[520px]">
          <DialogHeader><DialogTitle>Set event lock</DialogTitle></DialogHeader>
          <div className="space-y-3">
            <div className="text-sm">Event: <b>{registry.couple_names}</b> ({registry.slug})</div>
            <div className="flex items-center gap-2">
              <Label className="text-xs">Reason</Label>
              <Input value={reason} onChange={(e) => setReason(e.target.value)} placeholder="Optional" />
            </div>
            <div className="flex items-center gap-2">
              <Button onClick={async () => { await adminSetRegistryLock(id, { locked: true, reason }); setLockOpen(false); window.location.reload(); }}>Lock</Button>
              <Button variant="secondary" onClick={async () => { await adminSetRegistryLock(id, { locked: false }); setLockOpen(false); window.location.reload(); }}>Unlock</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

function formatCurrency(amount, currency = "AED") {
  try { return new Intl.NumberFormat("en-US", { style: "currency", currency }).format(amount || 0); }
  catch { return `${currency} ${Number(amount || 0).toFixed(2)}`; }
}