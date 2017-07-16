
import stripe
from django.core.mail import EmailMessage
from django.conf import settings
from .. import hooks
from decimal import Decimal
from .. import utils
from django.contrib.auth.models import User
from ..models import Charge,Invoice
from Foodhubinit.models import Profile


def sync_charge_from_stripe_data(data):
    obj, _ = Charge.objects.get_or_create(stripe_id=data["id"])
    obj.customer = Profile.objects.filter(stripe_id=data["customer"]).first()
    obj.source = data["source"]["id"]
    obj.invoice = next(iter(Invoice.objects.filter(stripe_id=data["invoice"])), None)
    obj.amount = utils.convert_amount_for_db(data["amount"], obj.currency)
    obj.paid = data["paid"]
    obj.refunded = data["refunded"]
    obj.captured = data["captured"]
    obj.disputed = data["dispute"] is not None
    obj.charge_created = utils.convert_tstamp(data, "created")
    if data.get("description"):
        obj.description = data["description"]
    if data.get("amount_refunded"):
        obj.amount_refunded = data["amount_refunded"]
    if data["refunded"]:
        obj.amount_refunded = obj.amount
    obj.save()
    return obj

def create(amount, customer, source=None,currency="usd",description=None, send_receipt=settings.SEND_EMAIL_RECEIPTS, capture=True, email=None):

    if not isinstance(amount, Decimal):
        raise ValueError(
            "You must supply a decimal value representing dollars."
        )
    stripe_charge = stripe.Charge.create(
        amount=utils.convert_amount_for_api(amount, currency),  # find the final amount
        currency=currency,
        source=source,
        customer=customer,
        description=description,
        capture=capture,
    )
    charge = sync_charge_from_stripe_data(stripe_charge)
    if send_receipt:
        hooks.send_receipt(charge, email)
    return charge
