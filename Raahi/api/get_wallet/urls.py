from django.urls import path
from .views import get_wallet

urlpatterns = [
    path('', get_wallet, name='get_wallet'),
]