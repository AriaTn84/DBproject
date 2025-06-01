from django.urls import path
from Raahi.api.get_ticket_details.views import get_ticket_details

urlpatterns = [
    path('', get_ticket_details, name='get_ticket_details'),
]