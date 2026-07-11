from django.conf import settings
from django.db import models

from restaurants.models import MenuItem, Restaurant


class Cart(models.Model):
    """One active cart per user, persisted in the DB.

    The 2017 app kept the cart in the session dict, so it evaporated on
    logout or across devices. A DB cart survives both, and gives order
    creation a single row to lock (see orders.services).
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="cart", on_delete=models.CASCADE)
    # A cart holds items from one restaurant at a time (like every real
    # delivery app); switching restaurants clears it.
    restaurant = models.ForeignKey(Restaurant, null=True, blank=True, on_delete=models.SET_NULL)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def subtotal_cents(self) -> int:
        return sum(i.menu_item.price_cents * i.quantity for i in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)

    class Meta:
        unique_together = [("cart", "menu_item")]
