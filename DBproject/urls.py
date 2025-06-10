"""
URL configuration for DBproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/log-in/', include('Raahi.api.log_in.urls')),
    path('api/sign-up/', include('Raahi.api.user_signup.urls')),
    path('api/profile/update-user/', include('Raahi.api.edit_profile.urls')),
    path('api/profile/get/', include('Raahi.api.get_profile.urls')),
    path('api/cities/', include('Raahi.api.get_cities.urls')),
    path('api/reservation/cancel/', include('Raahi.api.cancel_reservation.urls')),
    path('api/get-ticket-details/', include('Raahi.api.get_ticket_details.urls')),
    path('api/get-bookings/', include('Raahi.api.get_bookings.urls')),
    path('api/tickets/search/', include('Raahi.api.search_tickets.urls')),
    path('api/reservation/cancel-penalty/', include('Raahi.api.cancel_with_penalty.urls')),
    path('api/wallet/get/', include('Raahi.api.get_wallet.urls')),
    path('api/report-ticket-issue/', include('Raahi.api.report_ticket_issue.urls')),
    path('api/reserve-ticket/', include('Raahi.api.reserve_a_ticket.urls')),
    path('api/admin/management/', include('Raahi.api.admin_ticket_management.urls')),
    path('api/wallet/charge/', include('Raahi.api.charge_wallet.urls')),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/payment/', include('Raahi.api.payment.urls')),
]
