import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { I18nProvider } from './i18n';
import { Toaster } from './components/ui/toaster';
import AuthPage from './pages/Auth';
import PasswordReset from './pages/PasswordReset';
import Dashboard from './pages/Dashboard';
import CreateRegistry from './pages/CreateRegistry';
import PublicRegistry from './pages/PublicRegistry';
import Admin from './pages/Admin';
import AdminRegistryDetail from './pages/AdminRegistryDetail';
import AdminUserDetail from './pages/AdminUserDetail';
import Terms from './pages/Terms';
import Privacy from './pages/Privacy';
import Footer from './components/layout/Footer';
import CookieBanner from './components/CookieBanner';
import { initAnalytics } from './lib/analytics';
import { PROFESSIONAL_COPY } from './utils/professionalCopy';
import './App.css';

// Landing Page Component with Professional Design
function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Navigation */}
      <nav className="border-b bg-white/90 backdrop-blur-sm sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-slate-900">The giftspace</h1>
              <span className="ml-3 text-sm text-gray-600">Beautiful Wedding Registries</span>
            </div>
            <div className="flex items-center gap-4">
              <a href="/auth" className="text-slate-600 hover:text-slate-900 font-medium">
                Sign In
              </a>
              <a 
                href="/auth" 
                className="bg-blue-600 text-white px-6 py-2 rounded-full hover:bg-blue-700 transition-colors font-medium shadow-sm"
              >
                Get Started
              </a>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section with Beautiful Beach Background */}
      <div 
        className="relative px-4 sm:px-6 lg:px-8 py-32 min-h-screen flex items-center"
        style={{
          backgroundImage: 'url("https://images.unsplash.com/photo-1718152220111-6e1208d984bc?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDN8MHwxfHNlYXJjaHwxfHxmaWppJTIwYmVhY2h8ZW58MHx8fHwxNzU2NTQ0NzQ3fDA&ixlib=rb-4.1.0&q=85")',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat'
        }}
      >
        {/* Elegant overlay for text readability */}
        <div className="absolute inset-0 bg-gradient-to-r from-slate-900/70 via-slate-900/50 to-transparent"></div>
        
        <div className="relative text-left max-w-4xl mx-auto">
          <div className="text-white">
            <h1 className="text-6xl font-bold mb-6 leading-tight">
              Your Perfect Wedding<br />
              <span className="text-blue-300">Gift Registry</span>
            </h1>
            <p className="text-xl mb-8 max-w-2xl text-slate-200 leading-relaxed">
              Create beautiful gift funds for your special day. Let friends and 
              family give meaningful gifts toward your dream honeymoon and future together.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-start items-start">
              <a 
                href="/auth" 
                className="bg-blue-600 text-white px-8 py-4 rounded-full text-lg font-semibold hover:bg-blue-700 transition-colors shadow-lg hover:shadow-xl"
              >
                {PROFESSIONAL_COPY.hero.cta}
              </a>
              <a 
                href="#features" 
                className="text-slate-200 hover:text-white font-medium flex items-center gap-2"
              >
                Learn More
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div id="features" className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-20">
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              Everything you need for your perfect registry
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Professional tools designed to make your wedding registry beautiful and effortless
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {Object.entries(PROFESSIONAL_COPY.features).map(([key, feature]) => (
              <div key={key} className="text-center group">
                <div className="bg-gradient-to-br from-blue-100 to-indigo-100 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform">
                  {key === 'easy' && (
                    <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  )}
                  {key === 'secure' && (
                    <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                  )}
                  {key === 'beautiful' && (
                    <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zM21 5a2 2 0 00-2-2h-4a2 2 0 00-2 2v12a4 4 0 004 4h4a2 2 0 002-2V5z" />
                    </svg>
                  )}
                  {key === 'mobile' && (
                    <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a1 1 0 001-1V4a1 1 0 00-1-1H8a1 1 0 00-1 1v16a1 1 0 001 1z" />
                    </svg>
                  )}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">{feature.title}</h3>
                <p className="text-gray-600 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-24 bg-gradient-to-r from-blue-600 to-indigo-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-8">
            Ready to create your perfect registry?
          </h2>
          <p className="text-xl text-rose-100 mb-12 leading-relaxed">
            Join thousands of couples who've chosen The giftspace for their special day
          </p>
          <a 
            href="/auth" 
            className="bg-white text-rose-600 px-8 py-4 rounded-full text-lg font-semibold hover:bg-gray-50 transition-colors shadow-lg hover:shadow-xl inline-flex items-center gap-3"
          >
            {PROFESSIONAL_COPY.hero.cta}
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </a>
        </div>
      </div>

      <Footer />
      <CookieBanner />
    </div>
  );
}

function App() {
  // Initialize analytics
  React.useEffect(() => {
    initAnalytics();
  }, []);

  return (
    <I18nProvider>
      <AuthProvider>
        <Router>
          <div className="App">
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/auth" element={<AuthPage />} />
              <Route path="/auth/reset-password" element={<PasswordReset />} />
              <Route path="/create" element={<CreateRegistry />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/r/:slug" element={<PublicRegistry />} />
              <Route path="/admin" element={<Admin />} />
              <Route path="/admin/r/:id" element={<AdminRegistryDetail />} />
              <Route path="/admin/u/:id" element={<AdminUserDetail />} />
              <Route path="/legal/terms" element={<Terms />} />
              <Route path="/legal/privacy" element={<Privacy />} />
              {/* Catch-all route - redirect unknown paths to home */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
            <Toaster />
          </div>
        </Router>
      </AuthProvider>
    </I18nProvider>
  );
}

export default App;