from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/restaurants/", include("restaurants.urls")),
    path("api/cart/", include("carts.urls")),
    path("api/orders/", include("orders.urls")),
    path("api/payments/", include("orders.payment_urls")),
]
