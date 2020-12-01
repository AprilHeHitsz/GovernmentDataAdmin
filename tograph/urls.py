from django.conf.urls import url
from . import views

app_name = 'tograph'

urlpatterns = [
    url(r'^$', views.get_graph, name='show'),
    url(r'^crawl/$', views.crawl, name='crawl'),
    url(r'^part/$', views.part, name='part'),
    url(r'^table/$', views.table, name='table'),
    url(r'^to_graph/$', views.get_graph, name='to_graph'),
]
