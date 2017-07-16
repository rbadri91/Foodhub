import django
from django.conf.urls import url
from .sample_views import SampleView
from ..urls import urlpatterns

urlpatterns += [
	url(
        r'^confirmOrder/$',
        SampleView.as_view(),
        name='confirmOrder'
    ),

    url(
        r'^saveAddress/$',
        SampleView.as_view(),
        name='saveAddress'
    ),
    url(
        r'^orderPayment/$',
        SampleView.as_view(),
        name='orderPayment'
    ),
    url(
        r'^charge/$',
        SampleView.as_view(),
        name='charge'
    ),
]