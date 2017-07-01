from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
	url(r'^showCart/$', views.showCart, name='showCart'),
	url(r'^addToCart/$', views.addToCart, name='addToCart'),
	url(r'^removeFromCart/$', views.removeFromCart, name='removeFromCart'),
	url(r'^updateOrderAdddress/$', views.updateOrderAdddress, name='updateOrderAdddress'),
]