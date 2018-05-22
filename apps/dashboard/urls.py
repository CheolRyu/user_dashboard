from django.conf.urls import url 
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^signin$', views.signin),
    url(r'^login$', views.login),
    url(r'^register$', views.register),
    url(r'^registration$', views.registration),
    url(r'^show/user/(?P<user_id>\d+)$', views.wall), 
    url(r'^message/(?P<user_id>\d+)$', views.process_message),
]