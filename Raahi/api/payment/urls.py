from django.urls import path
from .views import get_payment_history, pay_for_ticket

urlpatterns = [
    path('history/', get_payment_history, name='report-ticket-issue'),
    path('pay/', pay_for_ticket, name='pay-for-ticket'),
]
