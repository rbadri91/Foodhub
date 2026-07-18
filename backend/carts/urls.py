from django.urls import path

from .views import CartItemsView, CartView

urlpatterns = [
    path("", CartView.as_view()),
    path("items/", CartItemsView.as_view()),
]
