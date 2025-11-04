from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PatientViewSet,
    RepresentativeViewSet,
    PatientFileViewSet,
    PatientPhoneViewSet,
    PatientSocialNetworkViewSet,
    PatientContactPersonViewSet,
    PatientDiseaseViewSet,
    PatientDiagnosisViewSet
)

router = DefaultRouter()
router.register('patients', PatientViewSet, basename='patient')
router.register('representatives', RepresentativeViewSet, basename='representative')
router.register('files', PatientFileViewSet, basename='patient-file')
router.register('phones', PatientPhoneViewSet, basename='patient-phone')
router.register('social-networks', PatientSocialNetworkViewSet, basename='patient-social')
router.register('contact-persons', PatientContactPersonViewSet, basename='patient-contact')
router.register('diseases', PatientDiseaseViewSet, basename='patient-disease')
router.register('diagnoses', PatientDiagnosisViewSet, basename='patient-diagnosis')

urlpatterns = [
    path('', include(router.urls)),
]
