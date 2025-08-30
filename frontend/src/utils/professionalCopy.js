// Professional copy and messaging for The giftspace platform

export const PROFESSIONAL_COPY = {
  // Landing page
  hero: {
    title: "Your Perfect Wedding Gift Registry",
    subtitle: "Create beautiful gift funds for your special day. Let friends and family give meaningful gifts toward what matters most.",
    cta: "Create Your Registry"
  },
  
  // Features
  features: {
    easy: {
      title: "Effortlessly Simple",
      description: "Create your registry in minutes with our intuitive design"
    },
    secure: {
      title: "Safe & Secure", 
      description: "Your data and contributions are protected with enterprise-grade security"
    },
    beautiful: {
      title: "Beautifully Designed",
      description: "Stunning themes and layouts that reflect your unique style"
    },
    mobile: {
      title: "Mobile Perfect",
      description: "Works flawlessly on all devices for you and your guests"
    }
  },
  
  // Registry creation
  registry: {
    welcome: "Welcome to your wedding registry!",
    subtitle: "Let's create something beautiful for your special day",
    placeholders: {
      coupleNames: "John & Jane Smith",
      eventDate: "Select your wedding date",
      location: "Wedding venue or city",
      slug: "john-and-jane-2025"
    },
    themes: {
      modern: "Clean and contemporary",
      romantic: "Elegant and timeless", 
      rustic: "Warm and natural",
      luxury: "Sophisticated and refined"
    }
  },
  
  // Fund creation
  funds: {
    welcome: "Create Your First Fund",
    subtitle: "What would you like friends and family to contribute towards?",
    categories: {
      honeymoon: "Honeymoon & Travel",
      home: "Home & Living",
      experience: "Experiences & Activities", 
      general: "General Contribution"
    },
    placeholders: {
      title: "Romantic Honeymoon in Paris",
      description: "Help us create unforgettable memories on our dream honeymoon",
      goal: "5000"
    },
    suggestions: {
      honeymoon: [
        "Dream Honeymoon in Bali",
        "Romantic Getaway to Paris", 
        "Adventure in New Zealand",
        "Luxury Resort Escape"
      ],
      home: [
        "Our First Home Together",
        "Dream Kitchen Renovation",
        "Cozy Living Room Setup",
        "Master Bedroom Makeover"
      ],
      experience: [
        "Cooking Classes for Two",
        "Wine Tasting Adventures",
        "Concert & Theater Tickets",
        "Anniversary Celebrations"
      ]
    }
  },
  
  // Contribution flow
  contribute: {
    title: "Contribute to Their Special Day",
    subtitle: "Your generosity will help make their dreams come true",
    anonymous: "Contribute anonymously",
    messagePlaceholder: "Write a heartfelt message for the couple...",
    thankYou: "Thank you for your generous contribution!",
    emailReceipt: "A receipt will be sent to your email"
  },
  
  // Admin and management
  admin: {
    dashboard: "Registry Dashboard",
    analytics: "Contribution Analytics", 
    export: "Export Data",
    settings: "Registry Settings"
  },
  
  // Email templates
  email: {
    receiptSubject: "Thank you for your contribution",
    receiptGreeting: "Dear {guestName}",
    receiptMessage: "Thank you for your generous contribution to {coupleNames}'s special day.",
    ownerSubject: "New contribution received!",
    ownerGreeting: "Hello {ownerName}",
    ownerMessage: "Great news! You've received a new contribution for your registry."
  },
  
  // Navigation and buttons
  navigation: {
    dashboard: "Dashboard",
    registry: "My Registry", 
    analytics: "Analytics",
    settings: "Settings",
    logout: "Sign Out"
  },
  
  buttons: {
    create: "Create Registry",
    save: "Save Changes",
    publish: "Publish Registry",
    contribute: "Make Contribution",
    addFund: "Add New Fund",
    viewRegistry: "View Public Registry",
    editFund: "Edit Fund",
    deleteFund: "Remove Fund"
  },
  
  // Status messages
  messages: {
    success: {
      registryCreated: "Your registry has been created successfully!",
      fundAdded: "Fund added to your registry",
      contributionReceived: "Contribution received - thank you!",
      settingsSaved: "Settings updated successfully"
    },
    errors: {
      generic: "Something went wrong. Please try again.",
      network: "Unable to connect. Please check your internet connection.",
      validation: "Please check all required fields."
    },
    loading: {
      creating: "Creating your registry...",
      saving: "Saving changes...",
      loading: "Loading..."
    }
  }
};

// Helper functions
export const getRandomFundSuggestion = (category) => {
  const suggestions = PROFESSIONAL_COPY.funds.suggestions[category];
  if (!suggestions) return "";
  return suggestions[Math.floor(Math.random() * suggestions.length)];
};

export const formatCurrency = (amount, currency = "AED") => {
  return new Intl.NumberFormat('en-AE', {
    style: 'currency',
    currency: currency
  }).format(amount);
};