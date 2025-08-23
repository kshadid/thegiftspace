import React from "react";
import { useParams, Link } from "react-router-dom";
import { adminMe, adminUserDetail } from "../lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";

export default function AdminUserDetail() {
  const { id } = useParams();
  const [authorized, setAuthorized] = React.useState(false);
  const [data, setData] = React.useState(null);

  React.useEffect(() => {
    adminMe().then((m) => setAuthorized(!!m.is_admin)).catch(() => setAuthorized(false));
  }, []);
  React.useEffect(() => {
    if (!authorized) return;
    adminUserDetail(id).then(setData).catch(() => setData(null));
  }, [authorized, id]);

  if (!authorized) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-24 text-center">
        <h1 className="text-2xl font-semibold">Not authorized</h1>
        <Link className="inline-block mt-6 underline" to="/">Back to home</Link>
      </div>
    );
  }

  if (!data) return <div className="p-10 text-center">Loading…</div>;
  const { user, registries_owned = [], registries_collab = [], recent_audit = [] } = data;

  return (
    <div className="min-h-screen">
      <div className="max-w-6xl mx-auto px-4 py-6 flex items-center justify-between">
        <Link to="/admin" className="text-sm text-muted-foreground hover:text-foreground">← Back</Link>
        <div className="font-medium">Admin • User • {user.name} ({user.email})</div>
      </div>

      <div className="max-w-6xl mx-auto px-4">
        <div className="grid md:grid-cols-3 gap-6">
          <Card>
            <CardHeader><CardTitle>User</CardTitle></CardHeader>
            <CardContent className="text-sm space-y-1">
              <div>ID: {user.id}</div>
              <div>Email: {user.email}</div>
              <div>Admin: {String(user.is_admin)}</div>
              <div>Created: {user.created_at ? new Date(user.created_at).toLocaleString() : "-"}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Owned events ({registries_owned.length})</CardTitle></CardHeader>
            <CardContent>
              <ul className="text-sm space-y-2">
                {registries_owned.map((r) => (
                  <li key={r.id} className="rounded border p-2 flex items-center justify-between">
                    <span>{r.couple_names} <span className="text-xs text-muted-foreground">({r.slug})</span></span>
                    <span className="text-xs flex items-center gap-2">
                      <Link className="underline" to={`/r/${r.slug}`} target="_blank" rel="noreferrer">Public</Link>
                      <Link className="underline" to={`/admin/r/${r.id}`}>Manage</Link>
                    </span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Collaborated events ({registries_collab.length})</CardTitle></CardHeader>
            <CardContent>
              <ul className="text-sm space-y-2">
                {registries_collab.map((r) => (
                  <li key={r.id} className="rounded border p-2 flex items-center justify-between">
                    <span>{r.couple_names} <span className="text-xs text-muted-foreground">({r.slug})</span></span>
                    <span className="text-xs flex items-center gap-2">
                      <Link className="underline" to={`/r/${r.slug}`} target="_blank" rel="noreferrer">Public</Link>
                      <Link className="underline" to={`/admin/r/${r.id}`}>Manage</Link>
                    </span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mt-6">
          <Card>
            <CardHeader><CardTitle>Recent audit</CardTitle></CardHeader>
            <CardContent>
              <ul className="text-sm space-y-2 max-h-80 overflow-auto">
                {recent_audit.length === 0 ? (
                  <li className="text-muted-foreground">No activity</li>
                ) : recent_audit.map((a) => (
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
    </div>
  );
}
