import axios from "axios";

const BASE = (process.env.REACT_APP_BACKEND_URL || "") + "/api";

const api = axios.create({ baseURL: BASE, timeout: 20000 });

export function setAccessToken(token) {
  if (token) localStorage.setItem("access_token", token);
  else localStorage.removeItem("access_token");
}
export function getAccessToken() {
  return localStorage.getItem("access_token");
}

api.interceptors.request.use((config) => {
  const t = getAccessToken();
  if (t) config.headers.Authorization = `Bearer ${t}`;
  return config;
});

// Auth
export async function apiRegister({ name, email, password }) {
  const { data } = await api.post(`/auth/register`, { name, email, password });
  return data;
}
export async function apiLogin({ email, password }) {
  const { data } = await api.post(`/auth/login`, { email, password });
  return data;
}
export async function apiMe() {
  const { data } = await api.get(`/auth/me`);
  return data;
}

// Registry
export async function createRegistry(registry) {
  const { data } = await api.post(`/registries`, registry);
  return data;
}
export async function updateRegistry(registryId, patch) {
  const { data } = await api.put(`/registries/${registryId}`, patch);
  return data;
}
export async function getRegistryById(registryId) {
  const { data } = await api.get(`/registries/${registryId}`);
  return data;
}
export async function listMyRegistries() {
  const { data } = await api.get(`/registries/mine`);
  return data;
}
export async function bulkUpsertFunds(registryId, funds) {
  const { data } = await api.post(`/registries/${registryId}/funds/bulk_upsert`, { funds });
  return data;
}
export async function listFunds(registryId) {
  const { data } = await api.get(`/registries/${registryId}/funds`);
  return data;
}
export async function getPublicRegistry(slug) {
  const { data } = await api.get(`/registries/${slug}/public`);
  return data;
}

// Contributions
export async function createContribution(contrib) {
  const { data } = await api.post(`/contributions`, contrib);
  return data;
}

// Analytics & Exports
export async function getRegistryAnalytics(registryId) {
  const { data } = await api.get(`/registries/${registryId}/analytics`);
  return data;
}
export async function exportRegistryCSV(registryId) {
  const response = await api.get(`/registries/${registryId}/contributions/export/csv`, { responseType: "blob" });
  return response.data;
}

// Collaborators
export async function addCollaborator(registryId, email) {
  const { data } = await api.post(`/registries/${registryId}/collaborators`, { email });
  return data;
}
export async function removeCollaborator(registryId, userId) {
  const { data } = await api.delete(`/registries/${registryId}/collaborators/${userId}`);
  return data;
}

// Admin
export async function adminMe() {
  const { data } = await api.get(`/admin/me`);
  return data;
}
export async function adminStats() {
  const { data } = await api.get(`/admin/stats`);
  return data;
}
export async function adminMetrics() {
  const { data } = await api.get(`/admin/metrics`);
  return data;
}
export async function adminUsers(query = "") {
  const { data } = await api.get(`/admin/users`, { params: { query } });
  return data;
}
export async function adminUsersLookup(idsCsv) {
  const { data } = await api.get(`/admin/users/lookup`, { params: { ids: idsCsv } });
  return data;
}
export async function adminRegistries(query = "") {
  const { data } = await api.get(`/admin/registries`, { params: { query } });
  return data;
}
export async function adminRegistryFunds(registryId) {
  const { data } = await api.get(`/admin/registries/${registryId}/funds`);
  return data;
}
export async function adminSetRegistryLock(registryId, { locked, reason }) {
  const { data } = await api.post(`/admin/registries/${registryId}/lock`, { locked, reason });
  return data;
}
export async function adminUserDetail(userId) {
  const { data } = await api.get(`/admin/users/${userId}/detail`);
  return data;
}

export default api;