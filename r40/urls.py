from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('symbol/<slug:ticker>', views.symbol, name='symbol'),
    path('earning', views.earning, name='earning'),
    path('10q', views.list_10q, name='get_10q_list'),
    path('daily-check', views.daily_check, name='daily_check'),
]
