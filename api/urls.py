from django.urls import path
from . import views

urlpatterns = [
    path('ping/', views.ping, name='api_ping'),
    path('login/', views.login_api, name='api_login'),
    path('cached/', views.cached_time, name='api_cached'),
]
