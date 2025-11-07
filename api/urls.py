from django.urls import path
from .views import ping, login_api, cached_time

urlpatterns = [
    path('ping/', ping, name='api_ping'),
    path('login/', login_api, name='api_login'),
    path('cached/', cached_time, name='api_cached'),
]