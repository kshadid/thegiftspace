import { PROFESSIONAL_COPY, getRandomFundSuggestion } from "../utils/copyContent";
import { getRandomRegistryImage, getRandomImageByCategory } from "../utils/defaultImages";

// Enhanced mock data with professional copy and beautiful images
export const DEFAULT_CURRENCY = "AED";

const THEME_PRESETS = [
  { value: "modern", label: "Modern", description: PROFESSIONAL_COPY.registry.themes.modern },
  { value: "romantic", label: "Romantic", description: PROFESSIONAL_COPY.registry.themes.romantic },
  { value: "rustic", label: "Rustic", description: PROFESSIONAL_COPY.registry.themes.rustic },
  { value: "luxury", label: "Luxury", description: PROFESSIONAL_COPY.registry.themes.luxury },
];

// Clear any existing sample data when user starts fresh
let hasLoggedInUser = false;

export function clearSampleDataOnLogin() {
  if (!hasLoggedInUser) {
    localStorage.removeItem('wedding_registry');
    localStorage.removeItem('wedding_funds');
    hasLoggedInUser = true;
  }
}

export function loadRegistry() {
  const stored = localStorage.getItem('wedding_registry');
  if (stored) {
    return JSON.parse(stored);
  }
  
  // Return empty registry instead of sample data
  return {
    couple_names: '',
    event_date: '',
    location: '', 
    currency: DEFAULT_CURRENCY,
    hero_image: '',
    slug: '',
    theme: 'modern'
  };
}

export function saveRegistry(registry) {
  localStorage.setItem('wedding_registry', JSON.stringify(registry));
}

export function loadFunds() {
  const stored = localStorage.getItem('wedding_funds');
  return stored ? JSON.parse(stored) : [];
}

export function saveFunds(funds) {
  localStorage.setItem('wedding_funds', JSON.stringify(funds));
}

// Professional fund suggestions based on category
export function getFundSuggestions(category = 'general') {
  const suggestions = PROFESSIONAL_COPY.funds.suggestions[category] || PROFESSIONAL_COPY.funds.suggestions.general;
  return suggestions.map((title, index) => ({
    id: `suggestion_${category}_${index}`,
    title,
    description: `${title} - help us create unforgettable memories together`,
    goal: category === 'honeymoon' ? 8000 : category === 'home' ? 5000 : 3000,
    category: category,
    cover_url: getRandomImageByCategory(category).url,
    visible: true,
    order: index + 1,
    pinned: false
  }));
}

// Create a new fund with professional defaults
export function createNewFund(category = 'general') {
  const suggestion = getRandomFundSuggestion(category);
  const image = getRandomImageByCategory(category);
  
  return {
    id: Date.now().toString(),
    title: suggestion || PROFESSIONAL_COPY.funds.placeholders.title,
    description: PROFESSIONAL_COPY.funds.placeholders.description,
    goal: parseFloat(PROFESSIONAL_COPY.funds.placeholders.goal),
    category: category,
    cover_url: image.url,
    visible: true,
    order: 1,
    pinned: false
  };
}

// Professional registry templates
export function getRegistryTemplate(type = 'modern') {
  const defaultImage = getRandomRegistryImage();
  
  const templates = {
    modern: {
      couple_names: '',
      event_date: '',
      location: '',
      currency: DEFAULT_CURRENCY,
      hero_image: defaultImage.url,
      theme: 'modern'
    },
    romantic: {
      couple_names: '',
      event_date: '',
      location: '', 
      currency: DEFAULT_CURRENCY,
      hero_image: defaultImage.url,
      theme: 'romantic'
    }
  };
  
  return templates[type] || templates.modern;
}

// Validation helpers
export function validateRegistry(registry) {
  const errors = {};
  
  if (!registry.couple_names?.trim()) {
    errors.couple_names = "Couple names are required";
  }
  
  if (!registry.slug?.trim()) {
    errors.slug = "Registry URL is required";
  } else if (!/^[a-z0-9-]+$/.test(registry.slug)) {
    errors.slug = "URL can only contain lowercase letters, numbers, and hyphens";
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
}

export function validateFund(fund) {
  const errors = {};
  
  if (!fund.title?.trim()) {
    errors.title = "Fund title is required";
  }
  
  if (fund.goal < 0) {
    errors.goal = "Goal must be a positive number";
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
}

// Professional messaging
export function getWelcomeMessage(user) {
  return `${PROFESSIONAL_COPY.registry.welcome} Let's create something beautiful for your special day.`;
}

export function getSuccessMessage(action) {
  const messages = {
    'registry_created': PROFESSIONAL_COPY.messages.success.registryCreated,
    'fund_added': PROFESSIONAL_COPY.messages.success.fundAdded,
    'settings_saved': PROFESSIONAL_COPY.messages.success.settingsSaved
  };
  
  return messages[action] || PROFESSIONAL_COPY.messages.success.registryCreated;
}

export { THEME_PRESETS };