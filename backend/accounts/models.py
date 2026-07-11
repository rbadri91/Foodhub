from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user from day one — the standard Django recommendation.

    The 2017 version bolted a Profile onto auth.User with addresses in a
    Postgres ArrayField of raw strings. Addresses are now first-class rows.
    """

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)

    REQUIRED_FIELDS = ["email"]

    def __str__(self) -> str:
        return self.username


class Address(models.Model):
    user = models.ForeignKey(User, related_name="addresses", on_delete=models.CASCADE)
    label = models.CharField(max_length=50, blank=True)  # "Home", "Work"
    line1 = models.CharField(max_length=200)
    line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "addresses"
        ordering = ["-is_default", "-created_at"]

    def __str__(self) -> str:
        return f"{self.line1}, {self.city}"
