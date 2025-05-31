from django.urls import path
from .views import cancel_reservation

urlpatterns = [
    path('', cancel_reservation, name='cancel_reservation'),
]