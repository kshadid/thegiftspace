# API Contracts – Cash Registry (Hitchd-style)

Scope
- Minimal productizable backend for honeymoon cash registry with public registry pages and contributions.
- All routes are prefixed with /api per ingress rules.
- DB: MongoDB (use MONGO_URL and DB_NAME from backend/.env). IDs are UUID strings, not ObjectIds.

Core Entities
- Registry: id, couple_names, event_date (ISO date string), location, currency, hero_image, slug, created_at, updated_at
- Fund: id, registry_id, title, description, goal (number), cover_url, category, created_at, updated_at
- Contribution: id, fund_id, name, amount, message, public (bool), method, created_at

Public Responses
- PublicRegistryResponse { registry: Registry, funds: Array<Fund & { raised:number, progress:number }>, totals: { raised:number } }

Endpoints
- GET /api/ -> { message: "Hello World" }

- POST /api/registries
  - body: { couple_names, event_date, location, currency, hero_image, slug }
  - 201 -> Registry

- PUT /api/registries/{registry_id}
  - body: partial(Registry fields except id, slug optional)
  - 200 -> Registry

- GET /api/registries/{slug}/public
  - 200 -> PublicRegistryResponse (includes funds with raised & progress, totals. No contributor PII aggregation)

- POST /api/registries/{registry_id}/funds/bulk_upsert
  - body: { funds: Array<{ id?:string, title, description, goal, cover_url, category }> }
  - 200 -> { updated: number, created: number }

- GET /api/registries/{registry_id}/funds
  - 200 -> Fund[]

- POST /api/contributions
  - body: { fund_id, name, amount, message, public, method }
  - 201 -> Contribution

- GET /api/funds/{fund_id}/contributions
  - 200 -> Contribution[]

Validation & Notes
- slug must be unique (enforced by check before insert; future: DB index).
- Monetary fields stored as numbers (AED default in FE). No currency conversion.
- event_date stored as string (YYYY-MM-DD) for simplicity.
- No auth in v1; future: couple auth & admin endpoints.

Frontend Mock Replacement Plan
- src/lib/api.js wraps axios with base `${REACT_APP_BACKEND_URL}/api`.
- CreateRegistry: on Save/Preview -> upsert registry, then bulk_upsert funds. Store registry_id & slug locally for quick access.
- PublicRegistry: load /registries/:slug/public, render funds with raised/progress. On contribute -> POST /contributions then refresh public data.
- Fallback: if API unavailable, fall back to localStorage mock (temporary during migration).

Data Initially Mocked (to replace)
- Registry/funds/contributions in src/mock/mock.js

Testing
- First run deep_testing_backend_v2 for backend routes. After pass, optionally run UI tests.