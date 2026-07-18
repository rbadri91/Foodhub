import uuid

from django.conf import settings
from django.db import models

from restaurants.models import Restaurant


class Order(models.Model):
    """An order with immutable price snapshots.

    Notable changes from the 2017 schema:
    - `order_Desc` (an ArrayField of JSON blobs) is replaced by proper
      OrderItem rows with unit-price snapshots — menu price changes can
      never rewrite a past order.
    - The old `Card` model (which stored card metadata in our DB) is gone
      entirely. Payment uses Stripe PaymentIntents: the client confirms
      the payment directly with Stripe and raw card data never touches
      this server. We store only the PaymentIntent id.
    """

    class Status(models.TextChoices):
        PENDING_PAYMENT = "pending_payment"
        PAID = "paid"
        CONFIRMED = "confirmed"
        CANCELLED = "cancelled"

    class Fulfillment(models.TextChoices):
        DELIVERY = "delivery"
        PICKUP = "pickup"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="orders", on_delete=models.PROTECT)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING_PAYMENT)
    fulfillment = models.CharField(max_length=10, choices=Fulfillment.choices)
    delivery_address = models.CharField(max_length=300, blank=True)
    subtotal_cents = models.PositiveIntegerField()
    fees_cents = models.PositiveIntegerField(default=0)
    total_cents = models.PositiveIntegerField()
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "-created_at"])]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    # Snapshots, not FKs to live menu rows — history must be immutable.
    name = models.CharField(max_length=200)
    unit_price_cents = models.PositiveIntegerField()
    quantity = models.PositiveSmallIntegerField()


class IdempotencyKey(models.Model):
    """Makes POST /api/orders safe to retry.

    The client sends an `Idempotency-Key` header; a retry with the same
    key returns the original order instead of creating a duplicate. The
    unique constraint on (user, key) is the actual guarantee — enforced
    by the database, not application logic.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    key = models.CharField(max_length=100)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "key"], name="uniq_idempotency_user_key")
        ]


class OutboxEvent(models.Model):
    """Transactional outbox for order lifecycle events.

    Events are written in the same DB transaction as the state change,
    so an event exists if and only if the change committed. A relay
    (worker/Debezium) would publish these to Kafka; consumers dedupe on
    event id, giving effectively-once delivery without 2PC.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    aggregate_type = models.CharField(max_length=50, default="order")
    aggregate_id = models.UUIDField()
    event_type = models.CharField(max_length=50)  # e.g. order.created, order.paid
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [models.Index(fields=["published_at", "created_at"])]
