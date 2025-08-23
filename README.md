# 💝 The giftspace - Wedding Cash Registry Platform

**The giftspace** is a modern, full-stack wedding cash registry platform that allows couples to create personalized registries and receive cash contributions from friends and family.

## ✨ Features

### 🎯 Core Features
- **User Authentication** - Secure JWT-based registration and login
- **Registry Management** - Create and customize wedding registries
- **Cash Fund Creation** - Set up multiple funds with goals, descriptions, and images
- **Guest Contributions** - Easy contribution flow with optional messaging
- **Email Notifications** - Automatic receipts for guests and notifications for couples
- **Analytics Dashboard** - Track contributions, view insights, and export data
- **Admin Console** - Platform management and user oversight
- **Mobile Responsive** - Optimized for all devices

### 🚀 Technical Features
- **Full-Stack Architecture** - React frontend, FastAPI backend, MongoDB database
- **Real-time Email Integration** - Resend-powered email notifications
- **Background Processing** - Non-blocking email delivery
- **File Upload System** - Chunked image uploads for performance
- **Error Monitoring** - Sentry integration for production monitoring
- **Rate Limiting** - API protection and abuse prevention
- **Comprehensive Testing** - Automated backend and frontend test suites

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  FastAPI Backend │    │    MongoDB      │
│                 │    │                 │    │                 │
│  • User Interface│    │  • REST API     │    │  • User Data    │
│  • State Mgmt   │    │  • Auth (JWT)   │    │  • Registries   │
│  • Responsive   │◄──►│  • Email Service│◄──►│  • Contributions│
│  • PWA Ready    │    │  • File Upload  │    │  • Analytics    │
│                 │    │  • Rate Limiting│    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                ▲
                                │
                       ┌─────────────────┐
                       │  External APIs  │
                       │                 │
                       │  • Resend Email │
                       │  • Sentry       │
                       │  • File Storage │
                       └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- MongoDB 6.0+

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/thegiftspace.git
   cd thegiftspace
   ```

2. **Backend setup:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Configure environment
   cp .env.example .env
   # Edit .env with your configuration
   
   # Start backend
   uvicorn server:app --reload --port 8001
   ```

3. **Frontend setup:**
   ```bash
   cd frontend
   npm install
   
   # Configure environment
   cp .env.example .env
   # Edit .env with your configuration
   
   # Start frontend
   npm start
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8001
   - API Documentation: http://localhost:8001/docs

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```bash
MONGO_URL="mongodb://localhost:27017"
DB_NAME="thegiftspace"
JWT_SECRET="your-super-secure-secret"
RESEND_API_KEY="re_your_resend_api_key"
FROM_EMAIL="noreply@thegiftspace.com"
SENTRY_DSN="your-sentry-dsn"
CORS_ORIGINS="http://localhost:3000"
ADMIN_EMAILS="admin@thegiftspace.com"
```

#### Frontend (.env)
```bash
REACT_APP_BACKEND_URL="http://localhost:8001"
REACT_APP_DOMAIN="thegiftspace.com"
REACT_APP_COMPANY_NAME="The giftspace"
```

## 📚 API Documentation

The backend provides a comprehensive REST API with the following main endpoints:

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

### Registries
- `GET /api/registries` - List user's registries
- `POST /api/registries` - Create new registry
- `GET /api/registries/:id` - Get registry details
- `PUT /api/registries/:id` - Update registry
- `DELETE /api/registries/:id` - Delete registry

### Public Access
- `GET /api/public/registries/:slug` - Public registry view

### Funds
- `GET /api/registries/:id/funds` - List registry funds
- `POST /api/registries/:id/funds` - Create new fund
- `PUT /api/registries/:id/funds/:fundId` - Update fund
- `DELETE /api/registries/:id/funds/:fundId` - Delete fund

### Contributions
- `POST /api/contributions` - Make contribution
- `GET /api/registries/:id/contributions` - List contributions
- `GET /api/registries/:id/analytics` - Registry analytics
- `GET /api/registries/:id/export/csv` - Export data

### Admin
- `GET /api/admin/stats` - Platform statistics
- `GET /api/admin/users` - User management
- `GET /api/admin/registries` - Registry management

Full API documentation available at `/docs` when running the backend.

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest
```

### Frontend Testing
```bash
cd frontend
npm test
```

### End-to-End Testing
The project includes comprehensive testing with automated test suites for both backend and frontend components.

## 🚀 Deployment

### Production Deployment
See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for comprehensive production deployment instructions.

### Quick Deploy Options
- **Vercel** (Frontend) + **Railway** (Backend)
- **DigitalOcean App Platform** (Full-stack)
- **AWS** / **Google Cloud** / **Azure**

### Monitoring Setup
See [SENTRY_SETUP.md](./SENTRY_SETUP.md) for error monitoring configuration.

## 🛡️ Security Features

- **JWT Authentication** with secure token handling
- **Rate Limiting** on API endpoints
- **Input Validation** with Pydantic models
- **CORS Configuration** for cross-origin security
- **Password Hashing** with bcrypt
- **SQL Injection Protection** via MongoDB
- **XSS Protection** with React's built-in sanitization

## 📈 Performance

- **Background Tasks** for email processing
- **Chunked File Uploads** for large images
- **Database Indexing** for fast queries
- **Static Asset Caching** for optimal load times
- **Responsive Images** with optimization
- **Code Splitting** for faster initial loads

## 🎨 UI/UX Features

- **Modern Design** with Tailwind CSS
- **Component Library** using shadcn/ui
- **Dark/Light Mode** support
- **Mobile-First** responsive design
- **Accessibility** compliant (WCAG 2.1)
- **Loading States** and error handling
- **Toast Notifications** for user feedback

## 📱 Progressive Web App

The frontend is PWA-ready with:
- Service Worker for offline functionality
- Web App Manifest for installation
- Push Notifications support
- Offline fallback pages

## 🌍 Internationalization

Basic i18n support is implemented with:
- Multi-language framework
- RTL language support ready
- Currency localization
- Date/time formatting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📋 Roadmap

### Upcoming Features
- [ ] Payment gateway integration (Stripe/PayPal)
- [ ] Social sharing capabilities
- [ ] Advanced analytics and reporting
- [ ] Multi-language support
- [ ] Custom themes and branding
- [ ] Guest RSVP integration
- [ ] QR code generation for registries
- [ ] Mobile app (React Native)

### Technical Improvements
- [ ] Redis caching layer
- [ ] CDN integration for images
- [ ] Advanced monitoring dashboard
- [ ] Automated backup system
- [ ] Load balancing setup
- [ ] Docker containerization

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation:** Check the guides in this repository
- **Issues:** Create an issue on GitHub
- **Email:** support@thegiftspace.com
- **Community:** Join our Discord server

## 🎉 Acknowledgments

- Built with ❤️ for couples celebrating their special day
- Inspired by modern wedding registry platforms
- Thanks to the open-source community for amazing tools

---

**Made with 💕 by The giftspace team**

*Helping couples create memorable wedding experiences, one gift at a time.*
