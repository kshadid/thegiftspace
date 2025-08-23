import axios from "axios";
const BASE = (process.env.REACT_APP_BACKEND_URL || "") + "/api";

export async function uploadFileChunked({ file, registryId, onProgress }) {
  // Step 1: initiate
  const init = await axios.post(`${BASE}/uploads/initiate`, {
    filename: file.name,
    size: file.size,
    mime: file.type,
    registry_id: registryId,
  }, { headers: authHeader() });
  const { upload_id, chunk_size } = init.data;

  // Step 2: chunks
  const total = file.size;
  let uploaded = 0;
  let index = 0;
  for (let start = 0; start < total; start += chunk_size) {
    const end = Math.min(start + chunk_size, total);
    const blob = file.slice(start, end);
    const form = new FormData();
    form.append("upload_id", upload_id);
    form.append("index", String(index));
    form.append("chunk", blob, `${file.name}.part`);
    await axios.post(`${BASE}/uploads/chunk`, form, { headers: authHeader() });
    uploaded = end;
    index += 1;
    if (onProgress) onProgress(Math.round((uploaded / total) * 100));
  }

  // Step 3: complete
  const done = await axios.post(`${BASE}/uploads/complete`, { upload_id }, { headers: authHeader() });
  const urlPath = done.data.url; // e.g., /api/files/registry/<id>/<name>
  const absoluteUrl = (process.env.REACT_APP_BACKEND_URL || "") + urlPath;
  return { url: absoluteUrl };
}

function authHeader() {
  const token = localStorage.getItem("access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}