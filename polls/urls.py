from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^querytag', views.querytag, name='querytag'),
]
