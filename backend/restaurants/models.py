import uuid

from django.db import models
from django.utils.text import slugify


class Restaurant(models.Model):
    """A restaurant, sourced from OpenStreetMap or seeded demo data.

    The 2017 app proxied EatStreet's API on every page view. That API no
    longer exists — and coupling reads to a third party was fragile anyway.
    Restaurants are now synced into our own tables (see the
    `sync_restaurants` management command), so the app owns its data.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    osm_id = models.BigIntegerField(null=True, blank=True, unique=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    cuisine = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=100, db_index=True)
    state = models.CharField(max_length=50, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    price_level = models.PositiveSmallIntegerField(default=2)  # 1–4
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=4.0)
    supports_delivery = models.BooleanField(default=True)
    supports_pickup = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["city", "cuisine"])]
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f"{self.name}-{self.city}")[:200]
            slug, n = base, 2
            while Restaurant.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class MenuSection(models.Model):
    restaurant = models.ForeignKey(Restaurant, related_name="sections", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["position"]
        unique_together = [("restaurant", "name")]

    def __str__(self) -> str:
        return f"{self.restaurant.name} — {self.name}"


class MenuItem(models.Model):
    """Prices are integer cents. Floats and money don't mix."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section = models.ForeignKey(MenuSection, related_name="items", on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=400, blank=True)
    price_cents = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.name} (${self.price_cents / 100:.2f})"
