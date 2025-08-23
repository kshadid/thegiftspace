# API Contracts – Cash Registry (Updated)

Entities
- User: id, name, email, password_hash, created_at
- Registry: id, owner_id, collaborators: string[], couple_names, event_date (YYYY-MM-DD), location, currency, hero_image, slug, theme, created_at, updated_at
- Fund: id, registry_id, title, description, goal, cover_url, category, visible, order, created_at, updated_at
- Contribution: id, fund_id, name, amount, message, public, method, guest_email, created_at

Auth
- POST /api/auth/register {name,email,password} -> {access_token, token_type, user}
- POST /api/auth/login {email,password} -> {access_token, token_type, user}
- GET /api/auth/me -> user

Registries (auth: owner or collaborator unless public)
- POST /api/registries {couple_names,event_date,location,currency,hero_image,slug,theme} -> Registry (owner_id=current)
- PUT /api/registries/{registry_id} partial -> Registry
- GET /api/registries/{registry_id} -> Registry (owner/collaborator)
- GET /api/registries/{slug}/public -> PublicRegistryResponse

Funds (auth: owner/collaborator)
- POST /api/registries/{registry_id}/funds/bulk_upsert {funds:[{id?,title,description,goal,cover_url,category,visible,order?}]} -> {created,updated}
- GET /api/registries/{registry_id}/funds -> Fund[] (sorted by order asc)

Contributions (public)
- POST /api/contributions {fund_id,name,amount,message,public,method,guest_email?} -> Contribution
- GET /api/funds/{fund_id}/contributions -> Contribution[] (owner/collaborator)

Analytics & Export (auth: owner/collaborator)
- GET /api/registries/{registry_id}/analytics -> { total, count, average, by_fund:[{fund_id,title,sum,count}], daily:[{date,sum}] }
- GET /api/registries/{registry_id}/contributions/export/csv -> CSV

Collaborators (auth: owner only)
- POST /api/registries/{registry_id}/collaborators {email}
- DELETE /api/registries/{registry_id}/collaborators/{user_id}

Frontend Integration
- CreateRegistry: tabs: Gifts (drag reorder), Add Gift, Analytics, Settings (theme preset, collaborators add/remove). Save triggers registry update + bulk upsert (order persisted). Export CSV button.
- PublicRegistry: applies theme preset to hero overlay/text, sorts funds by order.

Notes
- Payments remain mocked. Emails deferred.
- All routes prefixed /api; backend on 0.0.0.0:8001; frontend uses REACT_APP_BACKEND_URL; DB uses MONGO_URL.