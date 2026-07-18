from django.db.models import Prefetch
from rest_framework import generics, permissions

from .models import MenuItem, Restaurant
from .serializers import RestaurantDetailSerializer, RestaurantListSerializer


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
