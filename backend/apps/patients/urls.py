from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatientViewSet, RepresentativeViewSet, PatientFileViewSet

router = DefaultRouter()
router.register('patients', PatientViewSet, basename='patient')
router.register('representatives', RepresentativeViewSet, basename='representative')
router.register('files', PatientFileViewSet, basename='patient-file')

urlpatterns = [
    path('', include(router.urls)),
]
