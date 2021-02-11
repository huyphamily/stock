from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('symbol/<slug:ticker>', views.symbol, name='symbol'),
    path('earning', views.earning, name='earning'),
]
