from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^home/$', views.home, name='home'),
    url(r'^listStates/$', views.listStates, name='listStates'),
    url(r'^cities/(?P<state_name>[0-9A-Za-z._\'\- ]+)$',views.cities, name='cities'),
    url(r'^city/(?P<city_name>[0-9A-Za-z._\'\-() ]+)/$',views.city, name='city'),
    url(r'^restaurant/(?P<restaurant_name>[0-9A-Za-z._\'\-&\+\?% ]+)/$',views.restaurant_description, name='restaurant'),
    url(r'^findrestaurants/(?P<address>[0-9A-Za-z._\'\-,()&\+\?% ]+)/$',views.find_restaurants, name='findrestaurants'),
    url(r'^account_activation_sent/$', views.account_activation_sent, name='account_activation_sent'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    url(r'^accounts/login/$', views.login, {'template_name': 'foodhubinit/login.html','redirect_authenticated_user': True}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'login'}, name='logout'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^account/$', views.account, name='account'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^profile/nameedit/$', views.edit_name, name='edit_name'),
    url(r'^profile/emailedit/$', views.edit_email, name='edit_email'),
    url(r'^profile/password_change/$', views.edit_password, name='password_change'),
    url(r'^address/$', views.address, name='address'),
]