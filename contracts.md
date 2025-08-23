# API Contracts – Cash Registry (Pinned funds + validations)

Changes
- Fund: add pinned:boolean (default false). Public resolves pinned field.
- Bulk upsert accepts pinned, order persisted.
- Uploads: validate max 20MB; image/* only; CHUNK_SIZE=1MB; static served at /api/files/**.

Public
- GET /api/registries/{slug}/public -> funds sorted by order; includes pinned.

Frontend
- CreateRegistry: selection bulk actions (show/hide/delete), duplicate fund, pinned toggle, drag reorder, empty states.
- PublicRegistry: pinned fund highlighted as hero card; others in grid; smooth scroll via #gifts; og:image set from hero_image.

Notes
- Payments still mocked; emails deferred.
- All backend routes under /api; frontend uses REACT_APP_BACKEND_URL; DB via MONGO_URL.