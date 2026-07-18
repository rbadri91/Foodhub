"""Review guarantees: reviews persist, one per user per restaurant,
the aggregate rating is real once reviews exist, and the author
always comes from the JWT — never the payload.
"""
import pytest
from rest_framework.test import APIClient

from accounts.models import User
from restaurants.models import Restaurant, Review
from restaurants.services import submit_review


@pytest.fixture
def user(db):
    return User.objects.create_user("badri", email="b@example.com", password="test-pass-123")


@pytest.fixture
def restaurant(db):
    return Restaurant.objects.create(name="Test Trattoria", city="Dallas", cuisine="italian")


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


def test_review_saved_to_database(auth_client, restaurant, user):
    res = auth_client.post(
        f"/api/restaurants/{restaurant.slug}/reviews/",
        {"rating": 5, "comment": "Great carbonara."},
        format="json",
    )
    assert res.status_code == 201
    review = Review.objects.get()
    assert review.user == user
    assert review.restaurant == restaurant
    assert review.rating == 5
    assert review.comment == "Great carbonara."


def test_one_review_per_user_resubmit_replaces(user, restaurant):
    submit_review(user=user, restaurant=restaurant, rating=2, comment="meh")
    submit_review(user=user, restaurant=restaurant, rating=4, comment="better on retry")
    assert Review.objects.count() == 1
    assert Review.objects.get().rating == 4


def test_aggregate_rating_recomputed(user, restaurant):
    other = User.objects.create_user("sam", email="s@example.com", password="test-pass-123")
    submit_review(user=user, restaurant=restaurant, rating=5)
    submit_review(user=other, restaurant=restaurant, rating=2)

    restaurant.refresh_from_db()
    assert str(restaurant.rating) == "3.5"


def test_post_requires_auth(restaurant, db):
    res = APIClient().post(
        f"/api/restaurants/{restaurant.slug}/reviews/", {"rating": 5}, format="json"
    )
    assert res.status_code == 401
    assert Review.objects.count() == 0


def test_reviews_are_public_to_read(user, restaurant):
    submit_review(user=user, restaurant=restaurant, rating=4, comment="solid")
    res = APIClient().get(f"/api/restaurants/{restaurant.slug}/reviews/")
    assert res.status_code == 200
    body = res.json()
    results = body["results"] if isinstance(body, dict) else body
    assert results[0]["rating"] == 4
    assert results[0]["user"] == "badri"


@pytest.mark.parametrize("bad_rating", [0, 6, -1])
def test_rating_out_of_range_rejected(auth_client, restaurant, bad_rating):
    res = auth_client.post(
        f"/api/restaurants/{restaurant.slug}/reviews/", {"rating": bad_rating}, format="json"
    )
    assert res.status_code == 400
    assert Review.objects.count() == 0


def test_author_comes_from_jwt_not_payload(auth_client, restaurant, user):
    """A forged user field in the payload must be ignored."""
    mallory = User.objects.create_user("mallory", email="m@example.com", password="test-pass-123")
    res = auth_client.post(
        f"/api/restaurants/{restaurant.slug}/reviews/",
        {"rating": 1, "comment": "forged", "user": mallory.id},
        format="json",
    )
    assert res.status_code == 201
    assert Review.objects.get().user == user
