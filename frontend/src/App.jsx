import { Link, Route, Routes } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import { useCart } from "./context/CartContext";
import AuthPage from "./pages/AuthPage";
import CheckoutPage from "./pages/CheckoutPage";
import HomePage from "./pages/HomePage";
import OrdersPage from "./pages/OrdersPage";
import RestaurantPage from "./pages/RestaurantPage";

export default function App() {
  const { authed, logout } = useAuth();
  const { itemCount } = useCart();

  return (
    <div className="shell">
      <nav>
        <Link to="/" className="brand">Food<em>Hub</em></Link>
        <div className="nav-links">
          {authed ? (
            <>
              <Link to="/orders">Orders</Link>
              <Link to="/checkout">Cart{itemCount > 0 && ` (${itemCount})`}</Link>
              <a href="#" onClick={(e) => { e.preventDefault(); logout(); }}>Log out</a>
            </>
          ) : (
            <Link to="/auth">Log in</Link>
          )}
        </div>
      </nav>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/r/:slug" element={<RestaurantPage />} />
        <Route path="/checkout" element={<CheckoutPage />} />
        <Route path="/orders" element={<OrdersPage />} />
        <Route path="/auth" element={<AuthPage />} />
      </Routes>
    </div>
  );
}
