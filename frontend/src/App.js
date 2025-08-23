import React, { useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Link, Navigate } from "react-router-dom";
import axios from "axios";
import RegistryLanding from "./pages/RegistryLanding";
import CreateRegistry from "./pages/CreateRegistry";
import PublicRegistry from "./pages/PublicRegistry";
import AuthPage from "./pages/Auth";
import Dashboard from "./pages/Dashboard";
import AdminPage from "./pages/Admin";
import AdminRegistryDetail from "./pages/AdminRegistryDetail";
import { Toaster } from "./components/ui/toaster";
import { AuthProvider, useAuth } from "./context/AuthContext";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  useEffect(() => {
    const helloWorldApi = async () => {
      try {
        const response = await axios.get(`${API}/`);
        console.log(response.data.message);
      } catch (e) {
        console.log("Backend not yet needed for mock phase.");
      }
    };
    helloWorldApi();
  }, []);

  return (
    <div className="min-h-screen bg-background text-foreground">
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<RegistryLanding />} />
            <Route path="/auth" element={<AuthPage />} />
            <Route path="/dashboard" element={<Protected><Dashboard /></Protected>} />
            <Route path="/admin" element={<Protected><AdminPage /></Protected>} />
            <Route path="/admin/r/:id" element={<Protected><AdminRegistryDetail /></Protected>} />
            <Route path="/create" element={<Protected><CreateRegistry /></Protected>} />
            <Route path="/r/:slug" element={<PublicRegistry />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
      <Toaster />
    </div>
  );
}

function Protected({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="p-10 text-center">Loading…</div>;
  if (!user) return <Navigate to="/auth" replace />;
  return children;
}

function NotFound() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-24 text-center">
      <h1 className="text-3xl font-semibold">Page not found</h1>
      <p className="text-muted-foreground mt-2">The page you requested does not exist.</p>
      <Link className="inline-block mt-6 underline" to="/">Go home</Link>
    </div>
  );
}

export default App;