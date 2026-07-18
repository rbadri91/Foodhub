import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, money } from "../api/client";
import Ticket from "../components/Ticket";
import { useCart } from "../context/CartContext";

export default function CheckoutPage() {
  const { cart, reload } = useCart();
  const [fulfillment, setFulfillment] = useState("pickup");
  const [address, setAddress] = useState("");
  const [error, setError] = useState("");
  const [placing, setPlacing] = useState(false);
  const navigate = useNavigate();

  // One idempotency key per checkout attempt: double-clicks and network
  // retries return the same order instead of creating duplicates.
  const idempotencyKey = useMemo(() => crypto.randomUUID(), []);

  const subtotal = cart?.subtotal_cents ?? 0;
  const fees = Math.round(subtotal * 0.05) + (fulfillment === "delivery" ? 399 : 0);

  async function placeOrder() {
    setError("");
    setPlacing(true);
    try {
      const order = await api("/orders/", {
        method: "POST",
        headers: { "Idempotency-Key": idempotencyKey },
        body: { fulfillment, delivery_address: address },
      });
      await reload();
      navigate("/orders", { state: { placed: order.id } });
    } catch (e) {
      setError(e.message);
    } finally {
      setPlacing(false);
    }
  }

  return (
    <div className="restaurant-layout" style={{ paddingTop: 40 }}>
      <div className="form-card" style={{ margin: 0, maxWidth: 480 }}>
        <h1>Checkout</h1>
        <label htmlFor="fulfillment">Fulfillment</label>
        <select id="fulfillment" value={fulfillment} onChange={(e) => setFulfillment(e.target.value)}>
          <option value="pickup">Pickup — free</option>
          <option value="delivery">Delivery — {money(399)}</option>
        </select>
        {fulfillment === "delivery" && (
          <>
            <label htmlFor="address">Delivery address</label>
            <input
              id="address"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              placeholder="123 Main St, Dallas, TX"
            />
          </>
        )}
        <p className="muted" style={{ marginTop: 18 }}>
          Payment runs on Stripe test mode after the order is placed. No card
          data ever touches the FoodHub backend.
        </p>
        {error && <div className="error">{error}</div>}
        <button
          className="checkout-btn"
          disabled={placing || !cart?.items?.length}
          onClick={placeOrder}
        >
          {placing ? "Placing order…" : `Place order · ${money(subtotal + fees)}`}
        </button>
      </div>
      <aside>
        <Ticket checkout>
          <div className="ticket-row">
            <span>FEES{fulfillment === "delivery" ? " + DELIVERY" : ""}</span>
            <span>{money(fees)}</span>
          </div>
          <div className="ticket-row total">
            <span>TOTAL</span>
            <span>{money(subtotal + fees)}</span>
          </div>
        </Ticket>
      </aside>
    </div>
  );
}
