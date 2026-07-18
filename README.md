# FoodHub

A food ordering platform: browse restaurants, build a cart, check out with delivery or pickup, pay with Stripe. Originally built in 2017 on Django 1.11 + the EatStreet API; rebuilt in 2026 as a Django 5.2 REST API with a React frontend.

**Stack:** Django 5.2 (LTS) · Django REST Framework · SimpleJWT · PostgreSQL · Stripe PaymentIntents · React 18 + Vite · OpenStreetMap (Overpass) for restaurant data

## Quick start

```bash
# Backend (SQLite, zero config)
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py seed_demo          # offline demo data
python manage.py runserver

# Frontend (separate terminal)
cd frontend
npm install
npm run dev                          # http://localhost:5173, proxies /api to :8000
```

Or with Docker (Postgres included): `docker compose up`

To pull real restaurants for your city from OpenStreetMap instead of demo data:

```bash
python manage.py sync_restaurants --city "Dallas" --state "TX" --limit 40
```

## Architecture

```
React (Vite) ── JWT ──> Django REST API ──> PostgreSQL
                             │                  │
                             │            OutboxEvent table
                             ├──> Stripe (PaymentIntents + signed webhooks)
                             └──> OSM Overpass API (restaurant sync, offline-safe)
```

Four Django apps, each owning one bounded concern:

| App | Owns |
|---|---|
| `accounts` | Custom user, JWT auth, normalized addresses |
| `restaurants` | Restaurant/menu catalog, OSM sync, menu seeding |
| `carts` | One persistent DB cart per user (single-restaurant semantics) |
| `orders` | Checkout, idempotency, payments, outbox events |

## Engineering decisions worth reading

**Idempotent checkout.** `POST /api/orders` requires an `Idempotency-Key` header. Retries — double-clicks, network timeouts, client retries — return the original order. The guarantee is a database unique constraint on `(user, key)`, not application logic, so it holds under concurrent requests (the race is resolved by catching `IntegrityError` inside the transaction). See `orders/services.py`.

**Transactional order creation.** The cart row is locked with `select_for_update`; order, order items, idempotency record, outbox event, and cart clearing commit atomically. Two concurrent checkouts of the same cart cannot both succeed.

**Transactional outbox.** Order lifecycle events (`order.created`, `order.paid`) are written to an `OutboxEvent` table in the same transaction as the state change. A relay (worker or CDC) would publish these to Kafka; consumers dedupe on event id. This is the standard answer to "how do you atomically update a database *and* publish an event" without two-phase commit.

**Identity from the token, never the payload.** Every order and address query is scoped to `request.user` extracted from the JWT. No endpoint accepts a user id from the client. The test suite includes a cross-tenant access test proving user B gets a 404 on user A's order.

**Price snapshots.** Order items copy the menu item's name and price at purchase time. Repricing the menu can never rewrite order history.

**No card data, ever.** The 2017 version stored card metadata in a `Card` table. That table is gone. Payment uses Stripe PaymentIntents: the browser confirms payment directly with Stripe, the backend stores only the intent id, and the webhook that marks orders paid is signature-verified and idempotent (Stripe redelivers webhooks; a second delivery is a no-op).

**Money is integer cents.** Everywhere.

**Owned data over API coupling.** The old app called EatStreet on every page view; when EatStreet's API died, the app died. Restaurants are now synced into local tables from OpenStreetMap's Overpass API (free, keyless), with menus generated from per-cuisine templates — no free API provides menus. `seed_demo` makes the whole app runnable offline.

## API

```
POST   /api/auth/register/            create account
POST   /api/auth/token/               obtain JWT pair
POST   /api/auth/token/refresh/       refresh access token
GET    /api/auth/me/                  current user
CRUD   /api/auth/addresses/           saved addresses

GET    /api/restaurants/?city=&cuisine=&search=
GET    /api/restaurants/{slug}/       detail + menu

GET    /api/cart/                     current cart
DELETE /api/cart/                     clear cart
POST   /api/cart/items/               {menu_item_id, quantity}

POST   /api/orders/                   create (Idempotency-Key header required)
GET    /api/orders/                   my orders
GET    /api/orders/{id}/              my order detail

POST   /api/payments/intent/          {order_id} -> {client_secret}
POST   /api/payments/webhook/         Stripe webhook (signature-verified)
```

## Tests

```bash
cd backend && pytest
```

Six tests, each proving a claim above: idempotent retries, price snapshot immutability, cart clearing + outbox write, delivery validation, cross-tenant isolation, and webhook redelivery safety.

## Configuration

All secrets come from environment variables (see `backend/.env.example`). The repo contains no keys — the 2017 version committed its `SECRET_KEY` and database password, which is exactly the kind of thing this rewrite exists to fix.

| Variable | Purpose | Default |
|---|---|---|
| `SECRET_KEY` | Django signing key | insecure dev key |
| `DATABASE_URL` | Postgres connection | SQLite file |
| `STRIPE_SECRET_KEY` | test-mode Stripe key | unset (payments return 503) |
| `STRIPE_WEBHOOK_SECRET` | webhook signature check | unset |
