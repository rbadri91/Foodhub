from django.db import models
import uuid
from django.contrib.postgres.fields import ArrayField,JSONField
from django.contrib.auth.models import User
from django.utils import timezone
from .manager import ChargeManager



# Create your models here.
class Order(models.Model):
    	order_id = models.CharField(max_length=120, default=uuid.uuid4, unique=True, primary_key=True)
    	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    	delivery_address = models.CharField(max_length=200, blank=True)
    	order_Desc= ArrayField(JSONField(),default=list, null=True);
    	order_by = models.ForeignKey(User,null=True, blank=True,on_delete=models.CASCADE);

class StripeObject(models.Model):

    stripe_id = models.CharField(max_length=255, unique=True,null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True

class Card(StripeObject):

    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.TextField(blank=True)
    address_line_1 = models.TextField(blank=True)
    address_line_1_check = models.CharField(max_length=15)
    address_line_2 = models.TextField(blank=True)
    address_city = models.TextField(blank=True)
    address_state = models.TextField(blank=True)
    address_country = models.TextField(blank=True)
    address_zip = models.TextField(blank=True)
    address_zip_check = models.CharField(max_length=15)
    country = models.CharField(max_length=2, blank=True)
    cvc_check = models.CharField(max_length=15, blank=True)
    dynamic_last4 = models.CharField(max_length=4, blank=True)
    tokenization_method = models.CharField(max_length=15, blank=True)
    exp_month = models.IntegerField()
    exp_year = models.IntegerField()


class Invoice(StripeObject):

    customer = models.ForeignKey(User, related_name="invoices", on_delete=models.CASCADE)
    amount_due = models.DecimalField(decimal_places=2, max_digits=9)
    attempted = models.NullBooleanField()
    attempt_count = models.PositiveIntegerField(null=True)
    charge = models.ForeignKey("Charge", null=True, related_name="invoices", on_delete=models.CASCADE)
    statement_descriptor = models.TextField(blank=True)
    closed = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    paid = models.BooleanField(default=False)
    receipt_number = models.TextField(blank=True)
    subtotal = models.DecimalField(decimal_places=2, max_digits=9)
    tax = models.DecimalField(decimal_places=2, max_digits=9, null=True)
    tax_percent = models.DecimalField(decimal_places=2, max_digits=9, null=True)
    total = models.DecimalField(decimal_places=2, max_digits=9)
    date = models.DateTimeField()

    @property
    def status(self):
        return "Paid" if self.paid else "Open"

    @property
    def stripe_invoice(self):
        return stripe.Invoice.retrieve(self.stripe_id)

class Charge(StripeObject):

    customer = models.ForeignKey(User, null=True, related_name="charges", on_delete=models.CASCADE)
    invoice = models.ForeignKey(Invoice, null=True, related_name="charges", on_delete=models.CASCADE)
    source = models.CharField(max_length=100)
    currency = models.CharField(max_length=10, default="usd")
    amount = models.DecimalField(decimal_places=2, max_digits=9, null=True)
    amount_refunded = models.DecimalField(
        decimal_places=2,
        max_digits=9,
        null=True
    )
    description = models.TextField(blank=True)
    paid = models.NullBooleanField(null=True)
    disputed = models.NullBooleanField(null=True)
    refunded = models.NullBooleanField(null=True)
    captured = models.NullBooleanField(null=True)
    receipt_sent = models.BooleanField(default=False)
    charge_created = models.DateTimeField(null=True, blank=True)

    objects = ChargeManager()

    @property
    def stripe_charge(self):
        return stripe.Charge.retrieve(self.stripe_id)

    @property
    def card(self):
        return Card.objects.filter(stripe_id=self.source).first()