"""Review domain logic. Views stay thin; this owns the invariants:
one review per (user, restaurant), and Restaurant.rating is the
rounded average of live reviews once any exist.
"""
from decimal import Decimal

from django.db import transaction
from django.db.models import Avg

from .models import Restaurant, Review


@transaction.atomic
def submit_review(*, user, restaurant: Restaurant, rating: int, comment: str = "") -> Review:
    """Create the user's review, or replace their previous one, then
    recompute the restaurant's aggregate rating in the same transaction.
    """
    review, _created = Review.objects.update_or_create(
        restaurant=restaurant,
        user=user,
        defaults={"rating": rating, "comment": comment},
    )
    _recompute_rating(restaurant)
    return review


def _recompute_rating(restaurant: Restaurant) -> None:
    avg = restaurant.reviews.aggregate(avg=Avg("rating"))["avg"]
    if avg is None:
        return  # no reviews left — keep the seeded/default rating
    restaurant.rating = Decimal(avg).quantize(Decimal("0.1"))
    restaurant.save(update_fields=["rating"])
