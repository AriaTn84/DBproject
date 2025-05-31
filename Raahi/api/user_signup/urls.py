from django.urls import path
from .views import signup_user

urlpatterns = [
    path('', signup_user, name='signup_user'),
]