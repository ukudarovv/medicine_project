"""
URLs for Telegram Bot API
These endpoints are called by the Telegram bot backend
"""
from django.urls import path
from . import views

urlpatterns = [
    # Patient management
    path('patient/upsert/', views.PatientUpsertView.as_view(), name='bot-patient-upsert'),
    path('patient/verify-iin/', views.VerifyIINView.as_view(), name='bot-verify-iin'),
    path('patient/by-telegram/<int:telegram_user_id>/', views.GetPatientByTelegramView.as_view(), name='bot-patient-by-telegram'),
    
    # Consent management (delegated to consent app endpoints)
    path('consent/access-requests/<uuid:pk>/deny/', views.DenyAccessRequestView.as_view(), name='bot-deny-access-request'),
    path('consent/access-requests/<uuid:pk>/', views.AccessRequestDetailView.as_view(), name='bot-access-request-detail'),
    path('consent/patient-grants/<int:telegram_user_id>/', views.PatientGrantsView.as_view(), name='bot-patient-grants'),
]
