import axios from "axios";

const BASE = (process.env.REACT_APP_BACKEND_URL || "") + "/api";

const api = axios.create({ baseURL: BASE, timeout: 15000 });

export async function createRegistry(registry) {
  const { data } = await api.post(`/registries`, registry);
  return data;
}

export async function updateRegistry(registryId, patch) {
  const { data } = await api.put(`/registries/${registryId}`, patch);
  return data;
}

export async function bulkUpsertFunds(registryId, funds) {
  const { data } = await api.post(`/registries/${registryId}/funds/bulk_upsert`, { funds });
  return data;
}

export async function getPublicRegistry(slug) {
  const { data } = await api.get(`/registries/${slug}/public`);
  return data;
}

export async function createContribution(contrib) {
  const { data } = await api.post(`/contributions`, contrib);
  return data;
}

export default api;