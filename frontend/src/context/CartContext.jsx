import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { api } from "../api/client";
import { useAuth } from "./AuthContext";

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const { authed } = useAuth();
  const [cart, setCart] = useState(null);

  const load = useCallback(async () => {
    if (!authed) return setCart(null);
    setCart(await api("/cart/"));
  }, [authed]);

  useEffect(() => { load(); }, [load]);

  const setItem = useCallback(async (menuItemId, quantity) => {
    setCart(await api("/cart/items/", { method: "POST", body: { menu_item_id: menuItemId, quantity } }));
  }, []);

  const value = useMemo(() => {
    const itemCount = cart?.items?.reduce((n, i) => n + i.quantity, 0) ?? 0;
    return { cart, setItem, itemCount, reload: load };
  }, [cart, setItem, load]);

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export const useCart = () => useContext(CartContext);
