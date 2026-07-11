"""Order domain services.

Checkout is the one flow where correctness really matters, so it lives
here as a plain function with an explicit transaction boundary rather
than inside a view.
"""
import stripe
from django.conf import settings
from django.db import IntegrityError, transaction
from rest_framework.exceptions import ValidationError

from carts.models import Cart

from .models import IdempotencyKey, Order, OrderItem, OutboxEvent

DELIVERY_FEE_CENTS = 399
SERVICE_FEE_RATE = 0.05


def place_order(*, user, fulfillment: str, delivery_address: str, idempotency_key: str) -> Order:
    """Create an order from the user's cart. Safe to retry.

    Guarantees, in order of enforcement:
    1. Idempotency — a retried request with the same Idempotency-Key
       returns the original order (DB unique constraint, race-safe).
    2. Isolation — the cart row is locked (`select_for_update`) so two
       concurrent checkouts of the same cart can't both succeed.
    3. Atomicity — order, items, idempotency record, outbox event, and
       cart clearing commit together or not at all.

    Identity note: `user` comes from the authenticated request context
    (JWT), never from the request payload.
    """
    if not idempotency_key:
        raise ValidationError({"idempotency_key": "Idempotency-Key header is required."})

    existing = IdempotencyKey.objects.filter(user=user, key=idempotency_key).first()
    if existing:
        return existing.order

    with transaction.atomic():
        cart = (
            Cart.objects.select_for_update()
            .select_related("restaurant")
            .filter(user=user)
            .first()
        )
        if cart is None or not cart.items.exists():
            raise ValidationError({"cart": "Your cart is empty."})
        if fulfillment == Order.Fulfillment.DELIVERY and not delivery_address:
            raise ValidationError({"delivery_address": "A delivery address is required."})

        items = list(cart.items.select_related("menu_item"))
        subtotal = sum(i.menu_item.price_cents * i.quantity for i in items)
        fees = int(subtotal * SERVICE_FEE_RATE)
        if fulfillment == Order.Fulfillment.DELIVERY:
            fees += DELIVERY_FEE_CENTS

        order = Order.objects.create(
            user=user,
            restaurant=cart.restaurant,
            fulfillment=fulfillment,
            delivery_address=delivery_address,
            subtotal_cents=subtotal,
            fees_cents=fees,
            total_cents=subtotal + fees,
        )
        OrderItem.objects.bulk_create(
            OrderItem(
                order=order,
                name=i.menu_item.name,
                unit_price_cents=i.menu_item.price_cents,
                quantity=i.quantity,
            )
            for i in items
        )

        try:
            IdempotencyKey.objects.create(user=user, key=idempotency_key, order=order)
        except IntegrityError:
            # Lost a race with a concurrent identical request: roll back
            # our order and surface theirs.
            transaction.set_rollback(True)
            return IdempotencyKey.objects.get(user=user, key=idempotency_key).order

        OutboxEvent.objects.create(
            aggregate_id=order.id,
            event_type="order.created",
            payload={
                "order_id": str(order.id),
                "user_id": user.id,
                "restaurant_id": str(order.restaurant_id),
                "total_cents": order.total_cents,
            },
        )

        cart.items.all().delete()
        cart.restaurant = None
        cart.save(update_fields=["restaurant"])

    return order


def create_payment_intent(order: Order) -> str:
    """Create (or reuse) a Stripe PaymentIntent for an order.

    Returns the client secret the frontend uses with Stripe.js. Raw card
    data never reaches this backend.
    """
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if order.stripe_payment_intent_id:
        intent = stripe.PaymentIntent.retrieve(order.stripe_payment_intent_id)
        return intent.client_secret

    intent = stripe.PaymentIntent.create(
        amount=order.total_cents,
        currency="usd",
        metadata={"order_id": str(order.id)},
        automatic_payment_methods={"enabled": True},
        # Stripe-side idempotency: retrying this call can't double-create.
        idempotency_key=f"order-{order.id}",
    )
    order.stripe_payment_intent_id = intent.id
    order.save(update_fields=["stripe_payment_intent_id"])
    return intent.client_secret


def mark_order_paid(payment_intent_id: str) -> Order | None:
    """Webhook handler logic: transition order to PAID, exactly once.

    Idempotent by design — Stripe retries webhooks, and a second
    delivery finds the order already PAID and does nothing.
    """
    with transaction.atomic():
        order = (
            Order.objects.select_for_update()
            .filter(stripe_payment_intent_id=payment_intent_id)
            .first()
        )
        if order is None or order.status != Order.Status.PENDING_PAYMENT:
            return order
        order.status = Order.Status.PAID
        order.save(update_fields=["status"])
        OutboxEvent.objects.create(
            aggregate_id=order.id,
            event_type="order.paid",
            payload={"order_id": str(order.id), "total_cents": order.total_cents},
        )
    return order
