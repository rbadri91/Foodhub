import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order
from .serializers import OrderSerializer
from .services import create_payment_intent, mark_order_paid, place_order


class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        # Scoped by authenticated identity — a user can only ever see
        # their own orders. No user id is accepted from the client.
        return Order.objects.filter(user=self.request.user).prefetch_related("items")

    def create(self, request, *args, **kwargs):
        order = place_order(
            user=request.user,
            fulfillment=request.data.get("fulfillment", Order.Fulfillment.PICKUP),
            delivery_address=request.data.get("delivery_address", ""),
            idempotency_key=request.headers.get("Idempotency-Key", ""),
        )
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    lookup_field = "id"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")


class PaymentIntentView(APIView):
    """POST /api/payments/intent/ {order_id} -> {client_secret}."""

    def post(self, request):
        order = Order.objects.filter(
            user=request.user,
            id=request.data.get("order_id"),
            status=Order.Status.PENDING_PAYMENT,
        ).first()
        if order is None:
            return Response({"detail": "No payable order found."}, status=404)
        if not settings.STRIPE_SECRET_KEY:
            return Response(
                {"detail": "Stripe is not configured. Set STRIPE_SECRET_KEY."}, status=503
            )
        return Response({"client_secret": create_payment_intent(order)})


# CSRF does not apply: Stripe calls this server-to-server with no session
# cookie; authenticity is enforced by the webhook signature check below.
@csrf_exempt  # NOSONAR(S4502)
@require_POST
def stripe_webhook(request):
    """Stripe webhook: signature-verified, idempotent.

    Never trust the payload alone — construct_event verifies the
    signature with the webhook secret before we act on anything.
    """
    try:
        event = stripe.Webhook.construct_event(
            request.body,
            request.headers.get("Stripe-Signature", ""),
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event["type"] == "payment_intent.succeeded":
        mark_order_paid(event["data"]["object"]["id"])
    return HttpResponse(status=200)
