from django.urls import path
from .views import get_all_cities

urlpatterns = [
    path('', get_all_cities, name='get_all_cities'),
]