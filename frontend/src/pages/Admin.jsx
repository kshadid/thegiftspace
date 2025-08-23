import React from "react";
import { useNavigate, Link } from "react-router-dom";
import { adminMe, adminStats, adminUsers, adminRegistries, adminSetRegistryLock } from "../lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "../components/ui/dialog";

export default function AdminPage() {
  const [isAdmin, setIsAdmin] = React.useState(false);
  const [stats, setStats] = React.useState(null);
  const [uq, setUq] = React.useState("");
  const [rq, setRq] = React.useState("");
  const [users, setUsers] = React.useState([]);
  const [regs, setRegs] = React.useState([]);
  const [lockOpen, setLockOpen] = React.useState(false);
  const [lockReg, setLockReg] = React.useState(null);
  const [lockReason, setLockReason] = React.useState("");

  React.useEffect(() => {
    adminMe().then((m) => setIsAdmin(!!m.is_admin)).catch(() => setIsAdmin(false));
  }, []);
  React.useEffect(() => {
    if (!isAdmin) return;
    adminStats().then(setStats).catch(() => setStats(null));
  }, [isAdmin]);

  const searchUsers = async () => { setUsers(await adminUsers(uq)); };
  const searchRegs = async () => { setRegs(await adminRegistries(rq)); };

  if (!isAdmin) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-24 text-center">
        <h1 className="text-2xl font-semibold">Admin</h1>
        <p className="text-muted-foreground mt-2">You are not authorized to view this page.</p>
        <Link className="inline-block mt-6 underline" to="/">Back to home</Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <div className="max-w-6xl mx-auto px-4 py-6 flex items-center justify-between">
        <Link to="/" className="text-sm text-muted-foreground hover:text-foreground">← Back</Link>
        <div className="font-medium">Admin Console</div>
      </div>

      <div className="max-w-6xl mx-auto px-4">
        {/* Totals */}
        <div className="grid md:grid-cols-4 gap-4">
          <Stat label="Users" value={stats?.counts?.users} />
          <Stat label="Events" value={stats?.counts?.registries} />
          <Stat label="Funds" value={stats?.counts?.funds} />
          <Stat label="Contributions" value={stats?.counts?.contributions} />
        </div>

        {/* Recent */}
        <div className="grid md:grid-cols-2 gap-6 mt-8">
          <Card>
            <CardHeader><CardTitle>Recent signups</CardTitle></CardHeader>
            <CardContent>
              <ul className="text-sm space-y-2">
                {(stats?.last_users || []).map((u) => (
                  <li key={u.id} className="rounded border p-2 flex items-center justify-between">
                    <span>{u.name} — {u.email}</span>
                    <span className="text-xs text-muted-foreground">{new Date(u.created_at).toLocaleString()}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Recent events</CardTitle></CardHeader>
            <CardContent>
              <ul className="text-sm space-y-2">
                {(stats?.last_registries || []).map((r) => (
                  <li key={r.id} className="rounded border p-2">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium">{r.couple_names} <span className="text-xs text-muted-foreground">({r.slug})</span></div>
                        <div className="text-xs text-muted-foreground">Owner: {r.owner_email}</div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Link className="underline text-xs" to={`/r/${r.slug}`}>Public</Link>
                        <LockButton r={r} onOpen={(reg) => { setLockReg(reg); setLockReason(reg.lock_reason || ""); setLockOpen(true); }} />
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>

        {/* Search */}
        <div className="grid md:grid-cols-2 gap-6 mt-8">
          <Card>
            <CardHeader><CardTitle>Search users</CardTitle></CardHeader>
            <CardContent>
              <div className="flex gap-2">
                <Input value={uq} onChange={(e) => setUq(e.target.value)} placeholder="Email contains…" />
                <Button onClick={searchUsers}>Search</Button>
              </div>
              <ul className="text-sm space-y-2 mt-3">
                {users.map((u) => (
                  <li key={u.id} className="rounded border p-2 flex items-center justify-between">
                    <span>{u.name} — {u.email}</span>
                    <span className="text-xs text-muted-foreground">{new Date(u.created_at).toLocaleString()}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Search events</CardTitle></CardHeader>
            <CardContent>
              <div className="flex gap-2">
                <Input value={rq} onChange={(e) => setRq(e.target.value)} placeholder="Slug or names contain…" />
                <Button onClick={searchRegs}>Search</Button>
              </div>
              <ul className="text-sm space-y-2 mt-3">
                {regs.map((r) => (
                  <li key={r.id} className="rounded border p-2">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium">{r.couple_names} <span className="text-xs text-muted-foreground">({r.slug})</span></div>
                        <div className="text-xs text-muted-foreground">Owner: {r.owner_email}</div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Link className="underline text-xs" to={`/r/${r.slug}`}>Public</Link>
                        <LockButton r={r} onOpen={(reg) => { setLockReg(reg); setLockReason(reg.lock_reason || ""); setLockOpen(true); }} />
                      </div>
                    </div>
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
            <div className="text-sm">Event: <b>{lockReg?.couple_names}</b> ({lockReg?.slug})</div>
            <div className="flex items-center gap-2">
              <Label className="text-xs">Reason</Label>
              <Input value={lockReason} onChange={(e) => setLockReason(e.target.value)} placeholder="Optional" />
            </div>
            <div className="flex items-center gap-2">
              <Button onClick={async () => { await adminSetRegistryLock(lockReg.id, { locked: true, reason: lockReason }); setLockOpen(false); searchRegs(); }}>Lock</Button>
              <Button variant="secondary" onClick={async () => { await adminSetRegistryLock(lockReg.id, { locked: false }); setLockOpen(false); searchRegs(); }}>Unlock</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <Card>
      <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">{label}</CardTitle></CardHeader>
      <CardContent><div className="text-2xl font-semibold">{value ?? 0}</div></CardContent>
    </Card>
  );
}

function LockButton({ r, onOpen }) {
  return (
    <button className={`text-xs px-2 py-1 rounded border ${r.locked ? 'bg-destructive text-destructive-foreground border-destructive' : 'bg-white text-foreground'}`} onClick={() => onOpen(r)}>
      {r.locked ? 'Locked' : 'Lock'}
    </button>
  );
}