import React, { createContext, useContext, useEffect, useState } from "react";
import { apiLogin, apiMe, apiRegister, setAccessToken, getAccessToken } from "../lib/api";

const AuthCtx = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      setLoading(false);
      return;
    }
    apiMe()
      .then((u) => setUser(u))
      .catch(() => setAccessToken(null))
      .finally(() => setLoading(false));
  }, []);

  const login = async (email, password) => {
    const { access_token, user } = await apiLogin({ email, password });
    setAccessToken(access_token);
    setUser(user);
    return user;
  };

  const register = async (name, email, password) => {
    const { access_token, user } = await apiRegister({ name, email, password });
    setAccessToken(access_token);
    setUser(user);
    return user;
  };

  const logout = () => {
    setAccessToken(null);
    setUser(null);
  };

  return (
    <AuthCtx.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthCtx.Provider>
  );
}

export function useAuth() {
  return useContext(AuthCtx);
}