# FoodHub — guidance for Claude Code

## What this is
A portfolio food-ordering platform: Django 5.2 + DRF API backend, React 18 + Vite frontend. Rebuilt in 2026 from a 2017 Django 1.11 app. The README's "Engineering decisions" section is the source of truth for intent — read it first.

## Layout
- `backend/` — Django project (`foodhub/` settings, apps: `accounts`, `restaurants`, `carts`, `orders`)
- `frontend/` — Vite React SPA (proxies `/api` to `:8000` in dev)
- `backend/orders/services.py` — checkout domain logic (idempotency, locking, outbox). Handle with care; every change here needs a test.

## Commands
```bash
# backend
cd backend && source .venv/bin/activate
python manage.py runserver
python manage.py seed_demo                     # offline demo data
python manage.py sync_restaurants --city "Dallas" --state "TX"
pytest                                          # must stay green

# frontend
cd frontend && npm run dev
npm run build                                   # must compile before committing
```

## Invariants — do not break
1. `POST /api/orders` is idempotent via the `Idempotency-Key` header; the guarantee is the DB unique constraint on `(user, key)`.
2. Identity always comes from `request.user` (JWT). Never accept a user id from a request payload.
3. Money is integer cents everywhere. No floats, no Decimals in APIs.
4. OrderItem stores name/price snapshots — never FK to live menu prices for history.
5. No card data touches the backend. Stripe PaymentIntents only; webhook must stay signature-verified and idempotent.
6. State changes that emit events write an `OutboxEvent` row in the same transaction.
7. No secrets in the repo. New config goes through `django-environ` + `.env.example`.

## Conventions
- Domain logic lives in `services.py` modules, not views. Views stay thin.
- New endpoints: serializer + view + url + at least one test.
- Tests use pytest fixtures (see `orders/tests.py` for the house style).

## Roadmap candidates (in rough priority order)
- [ ] Outbox relay: management command that publishes unpublished OutboxEvents (log or Kafka), marking `published_at`
- [ ] Stripe Elements integration on the checkout page (client_secret flow is already wired server-side)
- [ ] Order status transitions: PAID -> CONFIRMED via a restaurant-side action; state machine with allowed-transition validation
- [ ] Restaurant geo search: nearest-N by lat/lon (start with bounding box; H3 if feeling ambitious)
- [ ] GitHub Actions CI: pytest + frontend build on PR
- [ ] Rate limiting on auth endpoints (DRF throttling)
