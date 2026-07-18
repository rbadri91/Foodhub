from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from restaurants.models import MenuItem

from .models import Cart, CartItem
from .serializers import CartSerializer


def _get_cart(user) -> Cart:
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


class CartView(APIView):
    """GET the current cart; DELETE to clear it."""

    def get(self, request):
        return Response(CartSerializer(_get_cart(request.user)).data)

    def delete(self, request):
        cart = _get_cart(request.user)
        cart.items.all().delete()
        cart.restaurant = None
        cart.save(update_fields=["restaurant"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartItemsView(APIView):
    """POST {menu_item_id, quantity} — add/update an item.

    Adding from a different restaurant replaces the cart (standard
    single-restaurant cart semantics).
    """

    def post(self, request):
        cart = _get_cart(request.user)
        menu_item = get_object_or_404(
            MenuItem, pk=request.data.get("menu_item_id"), is_available=True
        )
        quantity = int(request.data.get("quantity", 1))
        restaurant = menu_item.section.restaurant

        if cart.restaurant_id and cart.restaurant_id != restaurant.id:
            cart.items.all().delete()
        cart.restaurant = restaurant
        cart.save(update_fields=["restaurant"])

        if quantity <= 0:
            cart.items.filter(menu_item=menu_item).delete()
        else:
            CartItem.objects.update_or_create(
                cart=cart, menu_item=menu_item, defaults={"quantity": min(quantity, 20)}
            )
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)
