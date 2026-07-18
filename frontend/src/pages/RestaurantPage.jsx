import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api, money } from "../api/client";
import Ticket from "../components/Ticket";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";

export default function RestaurantPage() {
  const { slug } = useParams();
  const [restaurant, setRestaurant] = useState(null);
  const { authed } = useAuth();
  const { cart, setItem } = useCart();
  const navigate = useNavigate();

  useEffect(() => {
    api(`/restaurants/${slug}/`).then(setRestaurant);
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
      </div>
      <aside>
        <Ticket />
      </aside>
    </div>
  );
}
