"""
URLs for EHR (Electronic Health Records) API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EHRRecordViewSet

router = DefaultRouter()
router.register(r'records', EHRRecordViewSet, basename='ehr-record')

urlpatterns = [
    path('', include(router.urls)),
]

