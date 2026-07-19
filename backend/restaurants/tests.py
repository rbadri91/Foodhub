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


# ---- AI assistant chat ----


def _mock_claude_reply(monkeypatch, reply_text):
    """Stub the Anthropic client so tests never call the real API."""
    from unittest.mock import MagicMock

    from restaurants import assistant

    block = MagicMock()
    block.type = "text"
    block.text = reply_text
    client = MagicMock()
    client.messages.create.return_value = MagicMock(content=[block])
    monkeypatch.setattr(assistant.anthropic, "Anthropic", lambda **kw: client)
    return client


def test_chat_returns_grounded_reply(db, settings, monkeypatch):
    settings.ANTHROPIC_API_KEY = "test-key"
    client_mock = _mock_claude_reply(monkeypatch, "Try Bangkok Basil for pad thai.")
    Restaurant.objects.create(name="Bangkok Basil", city="Dallas", cuisine="thai")

    res = APIClient().post(
        "/api/chat/", {"message": "Who has pad thai?"}, format="json"
    )
    assert res.status_code == 200
    assert res.json()["reply"] == "Try Bangkok Basil for pad thai."

    # The catalog must be in the (cached) system prompt sent to Claude
    call = client_mock.messages.create.call_args.kwargs
    assert "Bangkok Basil" in call["system"][1]["text"]
    assert call["system"][1]["cache_control"] == {"type": "ephemeral"}
    assert call["messages"][-1] == {"role": "user", "content": "Who has pad thai?"}


def test_chat_passes_history(db, settings, monkeypatch):
    settings.ANTHROPIC_API_KEY = "test-key"
    client_mock = _mock_claude_reply(monkeypatch, "It is 4.7 stars.")

    res = APIClient().post(
        "/api/chat/",
        {
            "message": "What's its rating?",
            "history": [
                {"role": "user", "content": "Tell me about Bangkok Basil"},
                {"role": "assistant", "content": "It's a Thai place in Dallas."},
            ],
        },
        format="json",
    )
    assert res.status_code == 200
    messages = client_mock.messages.create.call_args.kwargs["messages"]
    assert len(messages) == 3
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"


def test_chat_503_when_not_configured(db, settings):
    settings.ANTHROPIC_API_KEY = ""
    res = APIClient().post("/api/chat/", {"message": "hi"}, format="json")
    assert res.status_code == 503


def test_chat_rejects_bad_input(db, settings):
    settings.ANTHROPIC_API_KEY = "test-key"
    assert APIClient().post("/api/chat/", {}, format="json").status_code == 400
    assert (
        APIClient().post("/api/chat/", {"message": "x" * 501}, format="json").status_code
        == 400
    )
    assert (
        APIClient()
        .post(
            "/api/chat/",
            {"message": "hi", "history": [{"role": "system", "content": "evil"}]},
            format="json",
        )
        .status_code
        == 400
    )
