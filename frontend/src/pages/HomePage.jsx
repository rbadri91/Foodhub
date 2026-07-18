import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";

const CUISINES = ["all", "italian", "mexican", "indian", "chinese", "japanese", "thai", "american", "pizza", "mediterranean"];

export default function HomePage() {
  const [restaurants, setRestaurants] = useState([]);
  const [search, setSearch] = useState("");
  const [cuisine, setCuisine] = useState("all");

  useEffect(() => {
    const params = new URLSearchParams();
    if (search) params.set("search", search);
    if (cuisine !== "all") params.set("cuisine", cuisine);
    const t = setTimeout(async () => {
      const data = await api(`/restaurants/?${params}`);
      setRestaurants(data.results);
    }, 200);
    return () => clearTimeout(t);
  }, [search, cuisine]);

  return (
    <>
      <header className="hero">
        <h1>Dinner, decided.</h1>
        <p>
          Browse real restaurants near you, build your order, and check out in
          under a minute. Delivery or pickup — your call.
        </p>
        <div className="search-row">
          <input
            placeholder="Search restaurants…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Search restaurants"
          />
        </div>
        <div className="chips" role="tablist" aria-label="Filter by cuisine">
          {CUISINES.map((c) => (
            <button
              key={c}
              className={`chip ${cuisine === c ? "active" : ""}`}
              onClick={() => setCuisine(c)}
            >
              {c}
            </button>
          ))}
        </div>
      </header>
      <section className="grid">
        {restaurants.map((r) => (
          <Link to={`/r/${r.slug}`} key={r.id} className="card">
            <h3>{r.name}</h3>
            <div className="meta">
              <span className="rating">★ {r.rating}</span>
              <span>{"$".repeat(r.price_level)}</span>
              <span>{r.city}</span>
            </div>
            <span className="cuisine-tag">{r.cuisine}</span>
          </Link>
        ))}
        {restaurants.length === 0 && (
          <p className="muted">No restaurants match. Try another cuisine or clear the search.</p>
        )}
      </section>
    </>
  );
}
