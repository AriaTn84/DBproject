from django.urls import path
from .views import search_tickets

urlpatterns = [
    path('', search_tickets, name='search_tickets'),
]