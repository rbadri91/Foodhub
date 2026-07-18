import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api, money } from "../api/client";
import Ticket from "../components/Ticket";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";

function ReviewSection({ slug, authed, onSaved }) {
  const [reviews, setReviews] = useState([]);
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const load = () =>
    api(`/restaurants/${slug}/reviews/`).then((d) => setReviews(d.results ?? d));

  useEffect(() => {
    load();
  }, [slug]);

  async function submit(e) {
    e.preventDefault();
    if (!authed) return navigate("/auth");
    setError(null);
    try {
      await api(`/restaurants/${slug}/reviews/`, {
        method: "POST",
        body: { rating, comment },
      });
      setComment("");
      await load();
      onSaved();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="menu-section">
      <h2>Reviews</h2>
      <form onSubmit={submit} style={{ marginBottom: 16 }}>
        <label style={{ marginRight: 8 }}>
          Your rating:{" "}
          <select value={rating} onChange={(e) => setRating(Number(e.target.value))}>
            {[5, 4, 3, 2, 1].map((n) => (
              <option key={n} value={n}>{"★".repeat(n)}</option>
            ))}
          </select>
        </label>
        <textarea
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="What did you think?"
          rows={2}
          maxLength={2000}
          style={{ display: "block", width: "100%", margin: "8px 0" }}
        />
        <button className="add-btn" type="submit">
          {authed ? "Post review" : "Sign in to review"}
        </button>
        {error && <p className="muted" style={{ color: "crimson" }}>{error}</p>}
      </form>
      {reviews.length === 0 && <p className="muted">No reviews yet — be the first.</p>}
      {reviews.map((r) => (
        <div className="menu-item" key={r.id}>
          <div>
            <strong>{r.user}</strong>{" "}
            <span className="muted">{"★".repeat(r.rating)}</span>
            {r.comment && <div className="desc">{r.comment}</div>}
          </div>
        </div>
      ))}
    </div>
  );
}

export default function RestaurantPage() {
  const { slug } = useParams();
  const [restaurant, setRestaurant] = useState(null);
  const { authed } = useAuth();
  const { cart, setItem } = useCart();
  const navigate = useNavigate();

  const loadRestaurant = () => api(`/restaurants/${slug}/`).then(setRestaurant);

  useEffect(() => {
    loadRestaurant();
  }, [slug]);

  if (!restaurant) return <p className="muted" style={{ padding: 32 }}>Loading menu…</p>;

  function qtyOf(itemId) {
    return cart?.items?.find((i) => i.menu_item.id === itemId)?.quantity ?? 0;
  }

  async function add(item) {
    if (!authed) return navigate("/auth");
    await setItem(item.id, qtyOf(item.id) + 1);
  }

  return (
    <div className="restaurant-layout">
      <div>
        <h1 style={{ fontFamily: "var(--display)", fontWeight: 800, marginBottom: 4 }}>
          {restaurant.name}
        </h1>
        <p className="muted">
          ★ {restaurant.rating} · {restaurant.cuisine} · {restaurant.address || restaurant.city}
        </p>
        {restaurant.sections.map((section) => (
          <div className="menu-section" key={section.id}>
            <h2>{section.name}</h2>
            {section.items.map((item) => (
              <div className="menu-item" key={item.id}>
                <div>
                  <strong>{item.name}</strong>
                  <div className="desc">{item.description}</div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <div className="price">{money(item.price_cents)}</div>
                  <button className="add-btn" onClick={() => add(item)}>
                    {qtyOf(item.id) > 0 ? `Add (${qtyOf(item.id)})` : "Add"}
                  </button>
                </div>
              </div>
            ))}
          </div>
        ))}
        <ReviewSection slug={slug} authed={authed} onSaved={loadRestaurant} />
      </div>
      <aside>
        <Ticket />
      </aside>
    </div>
  );
}
