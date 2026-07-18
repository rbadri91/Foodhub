from django.urls import path

from .views import RestaurantDetailView, RestaurantListView, ReviewListCreateView

urlpatterns = [
    path("", RestaurantListView.as_view()),
    path("<slug:slug>/", RestaurantDetailView.as_view()),
    path("<slug:slug>/reviews/", ReviewListCreateView.as_view()),
]
