from django.urls import path
from .views import send_otp, verify_otp, CustomTokenRefreshView

urlpatterns = [
    path('send-otp/', send_otp, name='send_otp'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh_custom'),
]