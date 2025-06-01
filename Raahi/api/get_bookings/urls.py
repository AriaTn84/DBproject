from django.urls import path
from .views import get_user_bookings

urlpatterns = [
    path('', get_user_bookings, name='get_user_bookings'),
]