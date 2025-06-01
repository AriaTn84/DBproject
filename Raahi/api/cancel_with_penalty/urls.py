from django.urls import path
from .views import cancel_with_penalty

urlpatterns = [
    path('', cancel_with_penalty, name='cancel_with_penalty'),
]