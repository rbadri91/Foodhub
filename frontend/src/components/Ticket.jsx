// The signature element: cart rendered as a kitchen order ticket.
import { useNavigate } from "react-router-dom";
import { money } from "../api/client";
import { useCart } from "../context/CartContext";

export default function Ticket({ checkout = false, children }) {
  const { cart, setItem } = useCart();
  const navigate = useNavigate();
  const items = cart?.items ?? [];

  return (
    <div className="ticket">
      <h2>Order Ticket</h2>
      <div className="sub">{cart?.restaurant_name || "No restaurant selected"}</div>
      <hr />
      {items.length === 0 && <div className="sub">— empty —</div>}
      {items.map((i) => (
        <div className="ticket-row" key={i.id}>
          <span>
            <span className="qty-controls">
              <button onClick={() => setItem(i.menu_item.id, i.quantity - 1)} aria-label={`Remove one ${i.menu_item.name}`}>−</button>
              {i.quantity}
              <button onClick={() => setItem(i.menu_item.id, i.quantity + 1)} aria-label={`Add one ${i.menu_item.name}`}>+</button>
            </span>{" "}
            {i.menu_item.name}
          </span>
          <span>{money(i.menu_item.price_cents * i.quantity)}</span>
        </div>
      ))}
      <hr />
      <div className="ticket-row total">
        <span>SUBTOTAL</span>
        <span>{money(cart?.subtotal_cents ?? 0)}</span>
      </div>
      {children}
      {!checkout && (
        <button
          className="checkout-btn"
          disabled={items.length === 0}
          onClick={() => navigate("/checkout")}
        >
          Go to checkout
        </button>
      )}
    </div>
  );
}
