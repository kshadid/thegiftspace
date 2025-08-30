// Professional copy content for The giftspace platform

// Gift registry creation suggestions
export const PROFESSIONAL_COPY = {
  // Gift registry suggestions
  registryTitles: [
    "Our Dream Honeymoon Gifts",
    "The Perfect Wedding Gift Registry", 
    "Celebrating Love & New Beginnings",
    "Our Wedding Gift Wishes",
    "A Celebration of Forever"
  ],

  // Gift fund suggestions by category
  giftFunds: {
    honeymoon: [
      {
        title: "Romantic Maldives Escape",
        description: "Gift us magical memories in an overwater villa surrounded by crystal-clear waters.",
        giftTarget: 8000
      },
      {
        title: "European Honeymoon Adventure", 
        description: "From Paris cafés to Italian vineyards - help us create romantic memories across Europe.",
        giftTarget: 6000
      },
      {
        title: "Tropical Paradise Getaway",
        description: "Sun, sand, and endless romance in a beautiful beachfront resort - your gift makes it possible!",
        giftTarget: 5000
      }
    ],
    
    travel: [
      {
        title: "Weekend City Escapes",
        description: "Gift us amazing city adventures and memories throughout our first year together.",
        giftTarget: 3000
      },
      {
        title: "Anniversary Adventures",
        description: "Annual trips to celebrate our love - your gift helps us explore the world hand in hand.",
        giftTarget: 4500
      }
    ],
    
    home: [
      {
        title: "Dream Kitchen Renovation",
        description: "Gift us the heart of our home where we'll cook, laugh, and make memories together.",
        giftTarget: 7500
      },
      {
        title: "Cozy Living Room Setup",
        description: "Beautiful furniture and décor to make our house feel like home - made possible by your generosity.",
        giftTarget: 4000
      },
      {
        title: "Master Bedroom Sanctuary", 
        description: "Your gift helps us create our perfect retreat with luxurious bedding and thoughtful touches.",
        giftTarget: 3500
      }
    ],
    
    experience: [
      {
        title: "Fine Dining Experiences",
        description: "Gift us special dinners and wine tastings to celebrate milestones together.",
        giftTarget: 2500
      },
      {
        title: "Couples Spa Retreats",
        description: "Your gift of relaxing spa days helps us unwind and reconnect throughout the year.",
        giftTarget: 2000
      },
      {
        title: "Concert & Theater Nights",
        description: "Gift us magical evenings with live music and performances we'll treasure forever.",
        giftTarget: 1800
      }
    ],
    
    general: [
      {
        title: "Our Future Together Gift Fund",
        description: "Your gifts help us build the foundation for our dreams, big and small.",
        giftTarget: 5000
      },
      {
        title: "Special Occasions Gift Fund",
        description: "Gift us beautiful birthdays, anniversaries, and surprise celebrations throughout our journey.",
        giftTarget: 3000
      }
    ]
  },
  
  // Wedding location suggestions
  locations: [
    "Dubai, UAE",
    "Abu Dhabi, UAE", 
    "Paris, France",
    "Tuscany, Italy",
    "Santorini, Greece",
    "Bali, Indonesia",
    "Maldives",
    "California, USA"
  ],
  
  // Placeholder names for examples
  coupleNames: [
    "Sarah & Ahmed",
    "Layla & Omar", 
    "Emma & Khalil",
    "Noor & Hassan",
    "Sophie & Rashid"
  ]
};

// Get random gift fund suggestion by category
export const getRandomFundSuggestion = (category = 'general') => {
  const categoryFunds = PROFESSIONAL_COPY.giftFunds[category.toLowerCase()] || PROFESSIONAL_COPY.giftFunds.general;
  const randomIndex = Math.floor(Math.random() * categoryFunds.length);
  return categoryFunds[randomIndex];
};

// Get all gift funds for a category  
export const getFundsByCategory = (category) => {
  return PROFESSIONAL_COPY.giftFunds[category.toLowerCase()] || PROFESSIONAL_COPY.giftFunds.general;
};

// Marketing copy for landing pages
export const MARKETING_COPY = {
  hero: {
    headline: "Create Your Perfect Wedding Gift Registry",
    subheadline: "Turn your dreams into reality with beautifully crafted gift funds that make it easy for guests to give meaningful gifts.",
    cta: "Start Your Gift Registry"
  },
  
  features: [
    {
      title: "Beautiful & Personal", 
      description: "Customize every detail to match your love story and wedding style."
    },
    {
      title: "Easy for Gift Givers",
      description: "Simple, secure gift giving that takes seconds to complete."
    },
    {
      title: "Real-time Updates", 
      description: "Watch your dreams come to life as gifts from loved ones arrive."
    }
  ],
  
  testimonials: [
    {
      quote: "The giftspace made our wedding gift registry so much more meaningful. Our guests loved being able to give toward our honeymoon dreams!",
      author: "Sarah & Ahmed"
    },
    {
      quote: "Setting up our gift registry was incredibly easy, and the design was absolutely beautiful. Our guests found it so thoughtful!",
      author: "Layla & Omar"  
    }
  ]
};