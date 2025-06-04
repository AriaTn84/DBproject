from django.urls import path
from .views import create_reservation

urlpatterns = [
    path('', create_reservation, name='create_reservation'),
]