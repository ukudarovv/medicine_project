"""
URL routing for Telegram Bot API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

app_name = 'telegram_bot'

urlpatterns = [
    # Patient management
    path('patient/upsert/', views.PatientUpsertView.as_view(), name='patient-upsert'),
    path('patient/verify-iin/', views.VerifyIINView.as_view(), name='verify-iin'),
    path('patient/by-telegram/<int:telegram_user_id>/', views.GetPatientByTelegramView.as_view(), name='patient-by-telegram'),
    
    # Booking
    path('branches/', views.BranchListView.as_view(), name='branches'),
    path('services/', views.ServiceListView.as_view(), name='services'),
    path('doctors/', views.DoctorListView.as_view(), name='doctors'),
    path('slots/', views.AvailableSlotsView.as_view(), name='slots'),
    
    # Appointments
    path('appointments/', views.AppointmentCreateView.as_view(), name='appointments-create'),
    path('appointments/my/', views.MyAppointmentsView.as_view(), name='appointments-my'),
    path('appointments/<int:pk>/', views.AppointmentUpdateView.as_view(), name='appointments-update'),
    path('appointments/<int:pk>/cancel/', views.AppointmentCancelView.as_view(), name='appointments-cancel'),
    
    # Documents
    path('documents/', views.DocumentListView.as_view(), name='documents'),
    path('documents/generate/', views.DocumentGenerateView.as_view(), name='documents-generate'),
    path('documents/<uuid:pk>/download/', views.DocumentDownloadView.as_view(), name='documents-download'),
    
    # Payments
    path('payments/invoice/', views.CreateInvoiceView.as_view(), name='payments-invoice'),
    path('payments/<int:pk>/status/', views.PaymentStatusView.as_view(), name='payments-status'),
    path('payments/callback/', views.PaymentCallbackView.as_view(), name='payments-callback'),
    path('payments/balance/', views.PatientBalanceView.as_view(), name='payments-balance'),
    
    # Feedback
    path('feedback/', views.FeedbackCreateView.as_view(), name='feedback-create'),
    
    # Support
    path('support/ticket/', views.SupportTicketCreateView.as_view(), name='support-ticket'),
    path('support/faq/', views.FAQListView.as_view(), name='support-faq'),
    
    # Broadcasts (admin only)
    path('broadcast/create/', views.BroadcastCreateView.as_view(), name='broadcast-create'),
    path('broadcast/<uuid:pk>/start/', views.BroadcastStartView.as_view(), name='broadcast-start'),
    path('broadcast/<uuid:pk>/stats/', views.BroadcastStatsView.as_view(), name='broadcast-stats'),
    
    # Webhook (for bot to receive updates)
    path('webhook/', views.TelegramWebhookView.as_view(), name='webhook'),
]

