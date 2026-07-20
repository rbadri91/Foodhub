import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { api, money } from "../api/client";

export default function OrdersPage() {
  const [orders, setOrders] = useState([]);
  const { state } = useLocation();

  useEffect(() => {
    api("/orders/").then((d) => setOrders(d.results));
  }, []);

  return (
    <div style={{ padding: "40px 0 80px", maxWidth: 640 }}>
      <h1 style={{ fontFamily: "var(--display)", fontWeight: 800 }}>Your orders</h1>
      {state?.placed && (
        <p className="muted">Order placed. The kitchen ticket below is yours.</p>
      )}
      {orders.length === 0 && <p className="muted">No orders yet — go find dinner.</p>}
      {orders.map((o) => (
        <div className="ticket" style={{ position: "static", marginBottom: 28 }} key={o.id}>
          <h2>{o.restaurant_name}</h2>
          <div className="sub">
            {new Date(o.created_at).toLocaleString()} ·{" "}
            <span className={`status-badge status-${o.status}`}>{o.status.replace("_", " ")}</span>
          </div>
          <hr />
          {o.items.map((i) => (
            <div className="ticket-row" key={i.id}>
              <span>{i.quantity} × {i.name}</span>
              <span>{money(i.unit_price_cents * i.quantity)}</span>
            </div>
          ))}
          <hr />
          <div className="ticket-row"><span>FEES</span><span>{money(o.fees_cents)}</span></div>
          <div className="ticket-row total"><span>TOTAL</span><span>{money(o.total_cents)}</span></div>
        </div>
      ))}
    </div>
  );
}
