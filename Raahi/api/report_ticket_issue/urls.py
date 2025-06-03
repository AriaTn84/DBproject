from django.urls import path
from .views import report_ticket_issue_view

urlpatterns = [
    path('', report_ticket_issue_view, name='report-ticket-issue'),
]