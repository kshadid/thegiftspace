# API Contracts – Cash Registry (Uploads & Analytics Expanded)

New Uploads (auth: owner or collaborator)
- POST /api/uploads/initiate
  - body: { filename, size, mime?, registry_id }
  - 200 -> { upload_id, chunk_size }
- POST /api/uploads/chunk (multipart)
  - form: upload_id, index, chunk (binary)
  - 200 -> { ok: true }
- POST /api/uploads/complete
  - body: { upload_id }
  - 200 -> { url: "/api/files/registry/{registry_id}/{filename}" }
- Static served at /api/files/** (mounted)

Analytics Extended
- GET /api/registries/{registry_id}/analytics ->
  - { total, count, average, by_fund:[{fund_id,title,sum,count}], daily:[{date,sum}], by_method:[{method,sum,count}], recent:[{name,amount,message?,created_at}] }

Collaborators
- POST /api/registries/{registry_id}/collaborators { email }
- DELETE /api/registries/{registry_id}/collaborators/{user_id }

Frontend integration
- src/lib/uploads.js uploadFileChunked(file, registryId, onProgress) -> { url }
- CreateRegistry: hero upload + fund image upload with inline progress; hero presets; drag reorder; analytics; collaborators; theme presets.

Notes
- Payments still mocked; emails deferred.
- All backend routes under /api; frontend uses REACT_APP_BACKEND_URL; DB via MONGO_URL.