from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'chart'

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='charts'),
    path('data/pie', views.get_pie_data, name='pie_street'),
    path('data/sun', views.get_sun_data, name='sun_street'),
    path('data/calender', views.get_calender_data, name='calender_street'),
]
