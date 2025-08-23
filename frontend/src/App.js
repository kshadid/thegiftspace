import React, { useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import axios from "axios";
import RegistryLanding from "./pages/RegistryLanding";
import CreateRegistry from "./pages/CreateRegistry";
import PublicRegistry from "./pages/PublicRegistry";
import { Toaster } from "./components/ui/toaster";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  useEffect(() => {
    // quick hello check (safe if backend is available)
    const helloWorldApi = async () => {
      try {
        const response = await axios.get(`${API}/`);
        console.log(response.data.message);
      } catch (e) {
        // eslint-disable-next-line no-console
        console.log("Backend not yet needed for mock phase.");
      }
    };
    helloWorldApi();
  }, []);

  return (
    <div className="min-h-screen bg-background text-foreground">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<RegistryLanding />} />
          <Route path="/create" element={<CreateRegistry />} />
          <Route path="/r/:slug" element={<PublicRegistry />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
      <Toaster />
    </div>
  );
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