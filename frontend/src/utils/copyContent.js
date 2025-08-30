// Professional copy content for The giftspace platform

// Registry creation suggestions
export const PROFESSIONAL_COPY = {
  // Registry suggestions
  registryTitles: [
    "Our Dream Honeymoon",
    "The Perfect Wedding Weekend", 
    "Celebrating Love & New Beginnings",
    "Our Wedding & Future Together",
    "A Celebration of Forever"
  ],

  // Fund suggestions by category
  funds: {
    honeymoon: [
      {
        title: "Romantic Maldives Escape",
        description: "Help us create magical memories in an overwater villa surrounded by crystal-clear waters.",
        goal: 8000
      },
      {
        title: "European Honeymoon Adventure", 
        description: "From Paris cafés to Italian vineyards - join us on a romantic journey across Europe.",
        goal: 6000
      },
      {
        title: "Tropical Paradise Getaway",
        description: "Sun, sand, and endless romance in a beautiful beachfront resort.",
        goal: 5000
      }
    ],
    
    travel: [
      {
        title: "Weekend City Escapes",
        description: "Help us explore new cities and create adventures together throughout our first year.",
        goal: 3000
      },
      {
        title: "Anniversary Adventures",
        description: "Annual trips to celebrate our love and explore the world hand in hand.",
        goal: 4500
      }
    ],
    
    home: [
      {
        title: "Dream Kitchen Renovation",
        description: "Help us create the heart of our home where we'll cook, laugh, and make memories.",
        goal: 7500
      },
      {
        title: "Cozy Living Room Setup",
        description: "Beautiful furniture and décor to make our house feel like home.",
        goal: 4000
      },
      {
        title: "Master Bedroom Sanctuary", 
        description: "Create our perfect retreat with luxurious bedding and thoughtful touches.",
        goal: 3500
      }
    ],
    
    experience: [
      {
        title: "Fine Dining Experiences",
        description: "Special dinners and wine tastings to celebrate milestones together.",
        goal: 2500
      },
      {
        title: "Couples Spa Retreats",
        description: "Relaxing spa days to unwind and reconnect throughout the year.",
        goal: 2000
      },
      {
        title: "Concert & Theater Nights",
        description: "Create magical evenings with live music and performances we'll treasure.",
        goal: 1800
      }
    ],
    
    general: [
      {
        title: "Our Future Together Fund",
        description: "Help us build the foundation for our dreams, big and small.",
        goal: 5000
      },
      {
        title: "Special Occasions Fund",
        description: "Birthdays, anniversaries, and surprise celebrations throughout our journey.",
        goal: 3000
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

// Get random fund suggestion by category
export const getRandomFundSuggestion = (category = 'general') => {
  const categoryFunds = PROFESSIONAL_COPY.funds[category.toLowerCase()] || PROFESSIONAL_COPY.funds.general;
  const randomIndex = Math.floor(Math.random() * categoryFunds.length);
  return categoryFunds[randomIndex];
};

// Get all funds for a category  
export const getFundsByCategory = (category) => {
  return PROFESSIONAL_COPY.funds[category.toLowerCase()] || PROFESSIONAL_COPY.funds.general;
};

// Marketing copy for landing pages
export const MARKETING_COPY = {
  hero: {
    headline: "Create Your Perfect Wedding Cash Registry",
    subheadline: "Turn your dreams into reality with beautifully crafted gift funds that make it easy for guests to contribute to what matters most.",
    cta: "Start Your Registry"
  },
  
  features: [
    {
      title: "Beautiful & Personal", 
      description: "Customize every detail to match your love story and wedding style."
    },
    {
      title: "Easy for Guests",
      description: "Simple, secure contributions that take seconds to complete."
    },
    {
      title: "Real-time Updates", 
      description: "Watch your dreams come to life as contributions roll in."
    }
  ],
  
  testimonials: [
    {
      quote: "The giftspace made our wedding registry so much more meaningful. Our guests loved being able to contribute to our honeymoon dreams!",
      author: "Sarah & Ahmed"
    },
    {
      quote: "Setting up our registry was incredibly easy, and the design was absolutely beautiful. Highly recommend!",
      author: "Layla & Omar"  
    }
  ]
};