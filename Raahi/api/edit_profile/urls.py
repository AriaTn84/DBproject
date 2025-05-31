from django.urls import path
from .views import get_user_profile

urlpatterns = [
    path('', get_user_profile, name='update_user_profile'),
]