"""
URLs for consent system API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PatientSearchView,
    AccessRequestViewSet,
    AccessRequestStatusView,
    OTPVerifyView,
    AccessGrantViewSet,
    AuditLogViewSet
)

router = DefaultRouter()
router.register(r'access-requests', AccessRequestViewSet, basename='access-request')
router.register(r'grants', AccessGrantViewSet, basename='access-grant')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')

urlpatterns = [
    # Patient search
    path('search-patient/', PatientSearchView.as_view(), name='search-patient'),
    
    # Access request status polling
    path('access-requests/<uuid:pk>/status/', AccessRequestStatusView.as_view(), name='access-request-status'),
    
    # OTP verification
    path('otp/verify/', OTPVerifyView.as_view(), name='otp-verify'),
    
    # Router URLs
    path('', include(router.urls)),
]

