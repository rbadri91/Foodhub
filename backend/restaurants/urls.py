from django.urls import path

from .views import RestaurantDetailView, RestaurantListView

urlpatterns = [
    path("", RestaurantListView.as_view()),
    path("<slug:slug>/", RestaurantDetailView.as_view()),
]
