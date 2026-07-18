from django.urls import path

from .views import PaymentIntentView, stripe_webhook

urlpatterns = [
    path("intent/", PaymentIntentView.as_view()),
    path("webhook/", stripe_webhook),
]
