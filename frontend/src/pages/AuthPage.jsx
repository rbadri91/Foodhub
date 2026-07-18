import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function AuthPage() {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [error, setError] = useState("");
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  async function submit() {
    setError("");
    try {
      if (mode === "login") await login(form.username, form.password);
      else await register(form.username, form.email, form.password);
      navigate("/");
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <div className="form-card">
      <h1>{mode === "login" ? "Log in" : "Create account"}</h1>
      <label htmlFor="username">Username</label>
      <input id="username" value={form.username} onChange={set("username")} autoComplete="username" />
      {mode === "register" && (
        <>
          <label htmlFor="email">Email</label>
          <input id="email" type="email" value={form.email} onChange={set("email")} autoComplete="email" />
        </>
      )}
      <label htmlFor="password">Password</label>
      <input
        id="password" type="password" value={form.password} onChange={set("password")}
        autoComplete={mode === "login" ? "current-password" : "new-password"}
        onKeyDown={(e) => e.key === "Enter" && submit()}
      />
      {error && <div className="error">{error}</div>}
      <button className="checkout-btn" onClick={submit}>
        {mode === "login" ? "Log in" : "Create account"}
      </button>
      <p className="muted" style={{ marginTop: 14 }}>
        {mode === "login" ? "New here? " : "Already have an account? "}
        <a href="#" style={{ color: "var(--basil)", fontWeight: 600 }}
          onClick={(e) => { e.preventDefault(); setMode(mode === "login" ? "register" : "login"); }}>
          {mode === "login" ? "Create an account" : "Log in"}
        </a>
      </p>
    </div>
  );
}
