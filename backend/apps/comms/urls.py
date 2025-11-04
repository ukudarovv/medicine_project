from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TemplateViewSet, MessageLogViewSet, SmsProviderViewSet,
    CampaignViewSet, ReminderViewSet, MessageViewSet,
    ContactLogViewSet, SmsBalanceViewSet
)

router = DefaultRouter()

# Legacy endpoints
router.register('templates', TemplateViewSet)
router.register('messages', MessageLogViewSet, basename='message')

# Marketing endpoints
router.register('marketing/providers', SmsProviderViewSet, basename='sms-provider')
router.register('marketing/campaigns', CampaignViewSet, basename='campaign')
router.register('marketing/reminders', ReminderViewSet, basename='reminder')
router.register('marketing/message-log', MessageViewSet, basename='marketing-message')
router.register('marketing/contact-log', ContactLogViewSet, basename='contact-log')
router.register('marketing/sms-balance', SmsBalanceViewSet, basename='sms-balance')

urlpatterns = [path('', include(router.urls))]
