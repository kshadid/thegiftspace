// Professional default images for The giftspace platform

// Wedding registry hero images
export const DEFAULT_REGISTRY_IMAGES = [
  {
    id: 'elegant-chandelier',
    url: 'https://images.unsplash.com/photo-1447434108058-49f9248d09a5?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njl8MHwxfHNlYXJjaHwxfHx3ZWRkaW5nJTIwZWxlZ2FudHxlbnwwfHx8fDE3NTY1MjgyMjh8MA&ixlib=rb-4.1.0&q=85',
    title: 'Elegant Crystal Chandelier',
    description: 'Sophisticated and luxurious'
  },
  {
    id: 'modern-reception',
    url: 'https://images.unsplash.com/photo-1680746217143-768e1e1d974c?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzZ8MHwxfHNlYXJjaHwxfHx3ZWRkaW5nJTIwbW9kZXJufGVufDB8fHx8MTc1NjUyODIzNXww&ixlib=rb-4.1.0&q=85',
    title: 'Modern Reception Venue',
    description: 'Contemporary celebration space'
  },
  {
    id: 'elegant-barn',
    url: 'https://images.unsplash.com/photo-1674924258890-f4a5d99bb28c?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njl8MHwxfHNlYXJjaHw0fHx3ZWRkaW5nJTIwZWxlZ2FudHxlbnwwfHx8fDE3NTY1MjgyMjh8MA&ixlib=rb-4.1.0&q=85',
    title: 'Rustic Elegance',
    description: 'Beautiful barn wedding venue'
  },
  {
    id: 'classic-couple',
    url: 'https://images.pexels.com/photos/33642046/pexels-photo-33642046.jpeg',
    title: 'Classic Wedding',
    description: 'Timeless romance'
  },
  {
    id: 'modern-couple',
    url: 'https://images.pexels.com/photos/33651783/pexels-photo-33651783.jpeg',
    title: 'Modern Romance',
    description: 'Contemporary love story'
  }
];

// Fund category images
export const DEFAULT_FUND_IMAGES = {
  honeymoon: [
    {
      id: 'maldives-aerial',
      url: 'https://images.unsplash.com/photo-1568727174680-7ae330b15345?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxfHxob25leW1vb24lMjB0cmF2ZWx8ZW58MHx8fHwxNzU2NTI4Mjc5fDA&ixlib=rb-4.1.0&q=85',
      title: 'Tropical Paradise',
      description: 'Dreamy island getaway'
    },
    {
      id: 'romantic-hammock',
      url: 'https://images.unsplash.com/photo-1576158831003-d41033ec31fd?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwyfHxob25leW1vb24lMjB0cmF2ZWx8ZW58MHx8fHwxNzU2NTI4Mjc5fDA&ixlib=rb-4.1.0&q=85',
      title: 'Romantic Escape',
      description: 'Peaceful beachside relaxation'
    },
    {
      id: 'overwater-villa',
      url: 'https://images.pexels.com/photos/1179156/pexels-photo-1179156.jpeg',
      title: 'Overwater Villa',
      description: 'Luxury honeymoon destination'
    }
  ],
  travel: [
    {
      id: 'infinity-pool',
      url: 'https://images.unsplash.com/photo-1551918120-9739cb430c6d?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwyfHxsdXh1cnklMjB0cmF2ZWx8ZW58MHx8fHwxNzU2NTI0MTAwfDA&ixlib=rb-4.1.0&q=85',
      title: 'Luxury Resort',
      description: 'Premium travel experience'
    },
    {
      id: 'mountain-adventure',
      url: 'https://images.pexels.com/photos/33620149/pexels-photo-33620149.jpeg',
      title: 'Adventure Together',
      description: 'Exploring new horizons'
    }
  ],
  home: [
    {
      id: 'modern-kitchen',
      url: 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?crop=entropy&cs=srgb&fm=jpg&w=800&q=85',
      title: 'Dream Kitchen',
      description: 'Create culinary memories'
    },
    {
      id: 'cozy-living',
      url: 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?crop=entropy&cs=srgb&fm=jpg&w=800&q=85',
      title: 'Cozy Living Space',
      description: 'Your perfect home together'
    }
  ],
  experience: [
    {
      id: 'fine-dining',
      url: 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?crop=entropy&cs=srgb&fm=jpg&w=800&q=85',
      title: 'Fine Dining',
      description: 'Memorable culinary experiences'
    },
    {
      id: 'celebration',
      url: 'https://images.unsplash.com/photo-1530103862676-de8c9debad1d?crop=entropy&cs=srgb&fm=jpg&w=800&q=85',
      title: 'Special Celebrations',
      description: 'Unforgettable moments together'
    }
  ],
  general: [
    {
      id: 'champagne-toast',
      url: 'https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?crop=entropy&cs=srgb&fm=jpg&w=800&q=85',
      title: 'Celebration Toast',
      description: 'Cheers to your future'
    },
    {
      id: 'romantic-dinner',
      url: 'https://images.unsplash.com/photo-1464207687429-7505649dae38?crop=entropy&cs=srgb&fm=jpg&w=800&q=85',
      title: 'Romantic Evening',
      description: 'Special moments together'
    }
  ]
};

// Get random image by category
export const getRandomImageByCategory = (category = 'general') => {
  const categoryImages = DEFAULT_FUND_IMAGES[category.toLowerCase()] || DEFAULT_FUND_IMAGES.general;
  const randomIndex = Math.floor(Math.random() * categoryImages.length);
  return categoryImages[randomIndex];
};

// Get all images for a category
export const getImagesByCategory = (category) => {
  return DEFAULT_FUND_IMAGES[category.toLowerCase()] || DEFAULT_FUND_IMAGES.general;
};

// Get random registry hero image
export const getRandomRegistryImage = () => {
  const randomIndex = Math.floor(Math.random() * DEFAULT_REGISTRY_IMAGES.length);
  return DEFAULT_REGISTRY_IMAGES[randomIndex];
};