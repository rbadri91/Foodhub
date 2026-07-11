// Thin fetch wrapper: attaches the JWT, refreshes once on 401,
// and normalizes the backend's error envelope.
const BASE = "/api";

let tokens = JSON.parse(localStorage.getItem("fh_tokens") || "null");

export function setTokens(next) {
  tokens = next;
  if (next) localStorage.setItem("fh_tokens", JSON.stringify(next));
  else localStorage.removeItem("fh_tokens");
}

export function isAuthed() {
  return Boolean(tokens?.access);
}

async function refresh() {
  if (!tokens?.refresh) return false;
  const res = await fetch(`${BASE}/auth/token/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh: tokens.refresh }),
  });
  if (!res.ok) {
    setTokens(null);
    return false;
  }
  setTokens({ ...tokens, ...(await res.json()) });
  return true;
}

export async function api(path, { method = "GET", body, headers = {}, retry = true } = {}) {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(tokens?.access ? { Authorization: `Bearer ${tokens.access}` } : {}),
      ...headers,
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (res.status === 401 && retry && (await refresh())) {
    return api(path, { method, body, headers, retry: false });
  }
  if (res.status === 204) return null;
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const details = data?.error?.details || data;
    throw new Error(typeof details === "string" ? details : JSON.stringify(details));
  }
  return data;
}

export const money = (cents) => `$${(cents / 100).toFixed(2)}`;
