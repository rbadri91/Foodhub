from rest_framework import serializers

from restaurants.serializers import MenuItemSerializer

from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer(read_only=True)
    menu_item_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "menu_item", "menu_item_id", "quantity"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal_cents = serializers.IntegerField(read_only=True)
    restaurant_name = serializers.CharField(source="restaurant.name", read_only=True, default=None)
    restaurant_slug = serializers.CharField(source="restaurant.slug", read_only=True, default=None)

    class Meta:
        model = Cart
        fields = ["id", "restaurant", "restaurant_name", "restaurant_slug", "items", "subtotal_cents"]
