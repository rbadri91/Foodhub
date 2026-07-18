from django.urls import path

from .views import OrderDetailView, OrderListCreateView

urlpatterns = [
    path("", OrderListCreateView.as_view()),
    path("<uuid:id>/", OrderDetailView.as_view()),
]
