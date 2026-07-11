import { createContext, useContext, useState } from "react";
import { api, isAuthed, setTokens } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [authed, setAuthed] = useState(isAuthed());

  async function login(username, password) {
    const data = await api("/auth/token/", { method: "POST", body: { username, password } });
    setTokens(data);
    setAuthed(true);
  }

  async function register(username, email, password) {
    await api("/auth/register/", { method: "POST", body: { username, email, password } });
    await login(username, password);
  }

  function logout() {
    setTokens(null);
    setAuthed(false);
  }

  return (
    <AuthContext.Provider value={{ authed, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
