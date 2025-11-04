from django.urls import path
from .views import AppointmentsReportView, RevenueReportView, SMSBalanceReportView, ExportExcelView

urlpatterns = [
    path('appointments', AppointmentsReportView.as_view()),
    path('revenue', RevenueReportView.as_view()),
    path('sms_balance', SMSBalanceReportView.as_view()),
    path('export', ExportExcelView.as_view()),
]
