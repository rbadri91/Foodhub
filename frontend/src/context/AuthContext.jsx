import { createContext, useCallback, useContext, useMemo, useState } from "react";
import { api, isAuthed, setTokens } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [authed, setAuthed] = useState(isAuthed());

  const login = useCallback(async (username, password) => {
    const data = await api("/auth/token/", { method: "POST", body: { username, password } });
    setTokens(data);
    setAuthed(true);
  }, []);

  const register = useCallback(async (username, email, password) => {
    await api("/auth/register/", { method: "POST", body: { username, email, password } });
    await login(username, password);
  }, [login]);

  const logout = useCallback(() => {
    setTokens(null);
    setAuthed(false);
  }, []);

  const value = useMemo(
    () => ({ authed, login, register, logout }),
    [authed, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
