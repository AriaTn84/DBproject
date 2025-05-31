from django.urls import path
from .views import get_user_profile

urlpatterns = [
    path('', get_user_profile, name='get_user_profile'),
]