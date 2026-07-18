"""Tests for the guarantees that matter.

Each test maps to a claim in the README: retried checkouts don't
duplicate orders, order history is immutable, users can't see each
other's orders, and webhook redelivery is harmless.
"""
import pytest
from rest_framework.test import APIClient

from accounts.models import User
from carts.models import Cart, CartItem
from orders.models import Order, OutboxEvent
from orders.services import mark_order_paid, place_order
from restaurants.menus import build_menu
from restaurants.models import Restaurant


@pytest.fixture
def user(db):
    return User.objects.create_user("badri", email="b@example.com", password="test-pass-123")


@pytest.fixture
def restaurant(db):
    r = Restaurant.objects.create(name="Test Trattoria", city="Dallas", cuisine="italian")
    build_menu(r)
    return r


@pytest.fixture
def cart(user, restaurant):
    cart = Cart.objects.create(user=user, restaurant=restaurant)
    item = restaurant.sections.first().items.first()
    CartItem.objects.create(cart=cart, menu_item=item, quantity=2)
    return cart


def test_place_order_is_idempotent(user, cart):
    """The same Idempotency-Key returns the same order — no duplicate."""
    first = place_order(user=user, fulfillment="pickup", delivery_address="", idempotency_key="k1")
    second = place_order(user=user, fulfillment="pickup", delivery_address="", idempotency_key="k1")
    assert first.id == second.id
    assert Order.objects.count() == 1


def test_order_snapshots_prices(user, cart, restaurant):
    """Changing a menu price later must not rewrite past orders."""
    menu_item = cart.items.first().menu_item
    original_price = menu_item.price_cents
    order = place_order(user=user, fulfillment="pickup", delivery_address="", idempotency_key="k2")

    menu_item.price_cents = original_price * 10
    menu_item.save()

    order.refresh_from_db()
    assert order.items.first().unit_price_cents == original_price
    assert order.subtotal_cents == original_price * 2


def test_checkout_clears_cart_and_writes_outbox(user, cart):
    place_order(user=user, fulfillment="pickup", delivery_address="", idempotency_key="k3")
    cart.refresh_from_db()
    assert cart.items.count() == 0
    assert OutboxEvent.objects.filter(event_type="order.created").count() == 1


def test_delivery_requires_address(user, cart):
    from rest_framework.exceptions import ValidationError

    with pytest.raises(ValidationError):
        place_order(user=user, fulfillment="delivery", delivery_address="", idempotency_key="k4")


def test_orders_scoped_to_authenticated_user(user, cart, db):
    """Identity comes from the JWT, never the payload: user B cannot
    read user A's orders even with the order id."""
    order = place_order(user=user, fulfillment="pickup", delivery_address="", idempotency_key="k5")

    other = User.objects.create_user("mallory", email="m@example.com", password="test-pass-123")
    client = APIClient()
    client.force_authenticate(other)
    response = client.get(f"/api/orders/{order.id}/")
    assert response.status_code == 404


def test_webhook_transition_is_idempotent(user, cart):
    """Stripe redelivers webhooks; a second delivery must be a no-op."""
    order = place_order(user=user, fulfillment="pickup", delivery_address="", idempotency_key="k6")
    order.stripe_payment_intent_id = "pi_test_123"
    order.save()

    mark_order_paid("pi_test_123")
    mark_order_paid("pi_test_123")  # redelivery

    order.refresh_from_db()
    assert order.status == Order.Status.PAID
    assert OutboxEvent.objects.filter(event_type="order.paid").count() == 1
