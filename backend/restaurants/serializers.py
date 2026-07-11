from rest_framework import serializers

from .models import MenuItem, MenuSection, Restaurant


class RestaurantListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ["id", "name", "slug", "cuisine", "address", "city", "state",
                  "price_level", "rating", "supports_delivery", "supports_pickup"]


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ["id", "name", "description", "price_cents", "is_available"]


class MenuSectionSerializer(serializers.ModelSerializer):
    items = MenuItemSerializer(many=True, read_only=True)

    class Meta:
        model = MenuSection
        fields = ["id", "name", "items"]


class RestaurantDetailSerializer(RestaurantListSerializer):
    sections = MenuSectionSerializer(many=True, read_only=True)

    class Meta(RestaurantListSerializer.Meta):
        fields = RestaurantListSerializer.Meta.fields + ["latitude", "longitude", "sections"]
