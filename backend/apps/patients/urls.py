from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PatientViewSet,
    PatientByGrantView,
    RepresentativeViewSet,
    PatientFileViewSet,
    PatientPhoneViewSet,
    PatientSocialNetworkViewSet,
    PatientContactPersonViewSet,
    PatientDiseaseViewSet,
    PatientDiagnosisViewSet,
    PatientDoseLoadViewSet,
)

# Import Sprint 2-5 ViewSets - migrations already applied (0006)
# These can be safely imported now
try:
    from .views import (
        MedicalExaminationViewSet,
        MedExamPastDiseaseViewSet,
        MedExamVaccinationViewSet,
        MedExamLabTestViewSet,
        TreatmentPlanViewSet,
        TreatmentStageViewSet,
        TreatmentStageItemViewSet,
        TreatmentPlanTemplateViewSet
    )
    EXTENDED_VIEWS_AVAILABLE = True
except ImportError:
    EXTENDED_VIEWS_AVAILABLE = False

router = DefaultRouter()
router.register('patients', PatientViewSet, basename='patient')
router.register('representatives', RepresentativeViewSet, basename='representative')
router.register('files', PatientFileViewSet, basename='patient-file')
router.register('phones', PatientPhoneViewSet, basename='patient-phone')
router.register('social-networks', PatientSocialNetworkViewSet, basename='patient-social')
router.register('contact-persons', PatientContactPersonViewSet, basename='patient-contact')
router.register('diseases', PatientDiseaseViewSet, basename='patient-disease')
router.register('diagnoses', PatientDiagnosisViewSet, basename='patient-diagnosis')
router.register('dose-loads', PatientDoseLoadViewSet, basename='patient-dose-load')

# Sprint 3: Medical Examinations & Treatment Plans
if EXTENDED_VIEWS_AVAILABLE:
    router.register('examinations', MedicalExaminationViewSet, basename='medical-examination')
    router.register('exam-past-diseases', MedExamPastDiseaseViewSet, basename='exam-past-disease')
    router.register('exam-vaccinations', MedExamVaccinationViewSet, basename='exam-vaccination')
    router.register('exam-lab-tests', MedExamLabTestViewSet, basename='exam-lab-test')
    router.register('treatment-plans', TreatmentPlanViewSet, basename='treatment-plan')
    router.register('treatment-stages', TreatmentStageViewSet, basename='treatment-stage')
    router.register('treatment-stage-items', TreatmentStageItemViewSet, basename='treatment-stage-item')
    router.register('treatment-plan-templates', TreatmentPlanTemplateViewSet, basename='treatment-plan-template')

urlpatterns = [
    # Get patient by grant ID (for desktop app)
    path('by-grant/<uuid:grant_id>/', PatientByGrantView.as_view(), name='patient-by-grant'),
    
    # Router URLs
    path('', include(router.urls)),
]
