/*
  Mock data and localStorage helpers for the Hitchd-style cash registry clone.
  All data is mocked. No backend calls yet.
*/

export const DEFAULT_CURRENCY = "AED";

export const sampleRegistry = {
  coupleNames: "Amir & Leila",
  eventDate: "2025-12-20",
  location: "Dubai, UAE",
  slug: "amir-leila",
  heroImage:
    "https://images.unsplash.com/photo-1520440718111-45fe694b330a?q=80&amp;w=1920&amp;auto=format&amp;fit=crop",
  currency: DEFAULT_CURRENCY,
};

export const sampleFunds = [
  {
    id: "fund-general",
    title: "Our Honeymoon Fund",
    description:
      "Help us create unforgettable memories on our first trip as a married couple.",
    goal: 20000,
    coverUrl:
      "https://images.unsplash.com/photo-1545048702-79362596cdc7?q=80&amp;w=1200&amp;auto=format&amp;fit=crop",
    category: "General",
  },
  {
    id: "fund-desert",
    title: "Desert Safari & Dinner",
    description: "An evening under the stars with dune bashing and a private dinner.",
    goal: 2500,
    coverUrl:
      "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?q=80&amp;w=1200&amp;auto=format&amp;fit=crop",
    category: "Experience",
  },
  {
    id: "fund-maldives",
    title: "Maldives Overwater Villa Night",
    description: "One dreamy night in an overwater villa to remember forever.",
    goal: 3500,
    coverUrl:
      "https://images.unsplash.com/photo-1518780664697-55e3ad937233?q=80&amp;w=1200&amp;auto=format&amp;fit=crop",
    category: "Stay",
  },
];

export const sampleContributions = [
  {
    id: "c1",
    fundId: "fund-general",
    name: "Sara A.",
    amount: 500,
    message: "Wishing you a lifetime of adventures!",
    public: true,
    createdAt: new Date().toISOString(),
  },
  {
    id: "c2",
    fundId: "fund-desert",
    name: "Omar",
    amount: 300,
    message: "Enjoy the dunes!",
    public: true,
    createdAt: new Date().toISOString(),
  },
];

// localStorage keys
const LS_KEYS = {
  registry: "registryData",
  funds: "registryFunds",
  contributions: "registryContributions",
};

export function loadRegistry() {
  const raw = localStorage.getItem(LS_KEYS.registry);
  return raw ? JSON.parse(raw) : sampleRegistry;
}
export function saveRegistry(data) {
  localStorage.setItem(LS_KEYS.registry, JSON.stringify(data));
}

export function loadFunds() {
  const raw = localStorage.getItem(LS_KEYS.funds);
  return raw ? JSON.parse(raw) : sampleFunds;
}
export function saveFunds(funds) {
  localStorage.setItem(LS_KEYS.funds, JSON.stringify(funds));
}

export function loadContributions() {
  const raw = localStorage.getItem(LS_KEYS.contributions);
  return raw ? JSON.parse(raw) : sampleContributions;
}
export function saveContributions(list) {
  localStorage.setItem(LS_KEYS.contributions, JSON.stringify(list));
}

export function addContribution(contrib) {
  const list = loadContributions();
  const withId = { ...contrib, id: `c_${Date.now()}` };
  list.unshift(withId);
  saveContributions(list);
  return withId;
}

export function sumForFund(fundId) {
  return loadContributions()
    .filter((c) => c.fundId === fundId)
    .reduce((acc, c) => acc + Number(c.amount || 0), 0);
}

export function totalReceived() {
  return loadContributions().reduce((acc, c) => acc + Number(c.amount || 0), 0);
}

export function ensureDefaults() {
  // Initialize LS on first load
  if (!localStorage.getItem(LS_KEYS.registry)) saveRegistry(sampleRegistry);
  if (!localStorage.getItem(LS_KEYS.funds)) saveFunds(sampleFunds);
  if (!localStorage.getItem(LS_KEYS.contributions))
    saveContributions(sampleContributions);
}