from django.urls import path
from .views import send_otp, verify_otp, get_otp_users

urlpatterns = [
    path('send-otp/', send_otp, name='send_otp'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('otp-users/', get_otp_users, name='get_otp_users'),
]