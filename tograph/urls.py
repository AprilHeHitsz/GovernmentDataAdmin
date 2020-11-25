from django.conf.urls import url
from . import views

app_name = 'tograph'

urlpatterns = [
    url(r'^$', views.show, name='show'),
]
