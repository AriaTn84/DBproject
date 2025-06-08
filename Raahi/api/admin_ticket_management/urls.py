from django.urls import path
from .views import (
    list_cancelled_reservations_view,
    list_user_reports_view,
    update_user_report_view,
    confirm_reservation_view, cancel_reservation_by_admin_view
)

urlpatterns = [
    path('reservations/cancelled/', list_cancelled_reservations_view, name='admin-list-cancelled-reservations'),
    path('reports/', list_user_reports_view, name='admin-list-user-reports'),
    path('reports/<int:report_id>/update/', update_user_report_view, name='admin-update-user-report'),
    path('reservations/<int:reservation_id>/confirm/', confirm_reservation_view, name='admin-confirm-reservation'),
    path('reservations/<int:reservation_id>/cancel/', cancel_reservation_by_admin_view, name='admin-cancel-reservation'),

]