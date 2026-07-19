from functools import cached_property

from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from . import assistant
from .models import MenuItem, Restaurant
from .serializers import (
    ChatRequestSerializer,
    RestaurantDetailSerializer,
    RestaurantListSerializer,
    ReviewSerializer,
)
from .services import submit_review


class RestaurantListView(generics.ListAPIView):
    """Browse restaurants. Public — no auth needed to window-shop."""

    permission_classes = [permissions.AllowAny]
    serializer_class = RestaurantListSerializer

    def get_queryset(self):
        qs = Restaurant.objects.filter(is_active=True)
        params = self.request.query_params
        if city := params.get("city"):
            qs = qs.filter(city__iexact=city)
        if cuisine := params.get("cuisine"):
            qs = qs.filter(cuisine__icontains=cuisine)
        if search := params.get("search"):
            qs = qs.filter(name__icontains=search)
        return qs


class RestaurantDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RestaurantDetailSerializer
    lookup_field = "slug"
    queryset = Restaurant.objects.prefetch_related(
        Prefetch("sections__items", queryset=MenuItem.objects.filter(is_available=True))
    )


class ReviewListCreateView(generics.ListCreateAPIView):
    """Reviews for one restaurant. Anyone can read; posting requires auth.
    The author always comes from the JWT, never the payload."""

    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        return self.restaurant.reviews.select_related("user")

    @cached_property
    def restaurant(self):
        return get_object_or_404(Restaurant, slug=self.kwargs["slug"], is_active=True)

    def perform_create(self, serializer):
        review = submit_review(
            user=self.request.user,
            restaurant=self.restaurant,
            rating=serializer.validated_data["rating"],
            comment=serializer.validated_data.get("comment", ""),
        )
        serializer.instance = review


class ChatView(APIView):
    """POST /api/chat/ {message, history?} -> {reply}.

    Public, like restaurant browsing. Domain logic lives in assistant.py.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not assistant.is_configured():
            return Response(
                {"detail": "Assistant is not configured. Set ANTHROPIC_API_KEY."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        reply = assistant.ask_assistant(
            message=serializer.validated_data["message"],
            history=serializer.validated_data.get("history", []),
        )
        return Response({"reply": reply})
