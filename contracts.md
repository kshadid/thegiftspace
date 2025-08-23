# API Contracts – Cash Registry (Hitchd-style)

Scope
- Minimal productizable backend for honeymoon cash registry with public registry pages and contributions.
- All routes are prefixed with /api per ingress rules.
- DB: MongoDB (use MONGO_URL and DB_NAME from backend/.env). IDs are UUID strings, not ObjectIds.

Core Entities
- User: id, name, email, password_hash, created_at
- Registry: id, owner_id, couple_names, event_date (YYYY-MM-DD), location, currency, hero_image, slug, created_at, updated_at
- Fund: id, registry_id, title, description, goal, cover_url, category, created_at, updated_at
- Contribution: id, fund_id, name, amount, message, public, method, created_at

Public Responses
- PublicRegistryResponse { registry: Registry, funds: Array<Fund & { raised:number, progress:number }>, totals: { raised:number } }

Auth Endpoints
- POST /api/auth/register
  - body: { name, email, password }
  - 201 -> { access_token, token_type: "bearer", user: { id, name, email } }
- POST /api/auth/login
  - body: { email, password }
  - 200 -> { access_token, token_type: "bearer", user }
- GET /api/auth/me
  - 200 -> user

Registry & Funds (auth required)
- POST /api/registries
  - body: { couple_names, event_date, location, currency, hero_image, slug }
  - 201 -> Registry (owner_id = current user)
- PUT /api/registries/{registry_id}
  - body: partial registry
  - 200 -> Registry (owner only)
- POST /api/registries/{registry_id}/funds/bulk_upsert
  - body: { funds: Array<{ id?:string, title, description, goal, cover_url, category }> }
  - 200 -> { updated: number, created: number }
- GET /api/registries/{registry_id}/funds
  - 200 -> Fund[] (owner only)

Public
- GET /api/registries/{slug}/public -> PublicRegistryResponse
- POST /api/contributions -> Contribution (no auth)
- GET /api/funds/{fund_id}/contributions -> Contribution[] (owner only)

Frontend Integration Plan
- Add AuthContext to store token+user in localStorage; axios interceptor adds Authorization header.
- Create page /auth for login/register; gate /create by redirecting unauthenticated users.
- CreateRegistry: Save to backend when token present; otherwise redirect to /auth.
- PublicRegistry: read via GET /registries/:slug/public; Contribute posts to /contributions.

Data Initially Mocked (to replace)
- Registry/funds/contributions in src/mock/mock.js (used only as fallback during API outages).